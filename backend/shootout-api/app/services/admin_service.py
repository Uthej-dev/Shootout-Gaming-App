import re
from datetime import datetime, timezone
from pymongo import ReturnDocument
from app.core.errors import AppError
from app.db.database import client, db
from app.services.match_service import _to_utc, match_status, serialize


async def list_matches(game: str | None, status: str | None) -> list[dict]:
    q = {"game": game} if game else {}
    matches = await db.matches.find(q).sort("startTime", -1).to_list(500)
    now = datetime.now(timezone.utc)
    out = [serialize(m, None, now) for m in matches]
    return [m for m in out if m["status"] == status] if status else out


async def update_match(match_id, req) -> dict:
    m = await db.matches.find_one({"_id": match_id})
    if not m:
        raise AppError(404, "MATCH_NOT_FOUND", "Match not found")
    data = req.model_dump(exclude_unset=True)
    data = {k: v for k, v in data.items() if v is not None}
    if not data:
        raise AppError(422, "NOTHING_TO_UPDATE", "No fields to update")
    joined = m["registeredPlayers"] > 0
    if "game" in data:
        data["game"] = data["game"].value if hasattr(data["game"], "value") else data["game"]
        if joined and data["game"] != m["game"]:
            raise AppError(409, "GAME_LOCKED", "Cannot change the game after players have joined")
    if "entryFee" in data and joined and data["entryFee"] != m["entryFee"]:
        raise AppError(409, "ENTRY_FEE_LOCKED", "Cannot change the entry fee after players have joined")
    if "maxPlayers" in data and data["maxPlayers"] < m["registeredPlayers"]:
        raise AppError(409, "MAX_PLAYERS_TOO_LOW", f"{m['registeredPlayers']} players have already joined")
    start = _to_utc(data["startTime"]) if "startTime" in data else m["startTime"]
    end = _to_utc(data["endTime"]) if "endTime" in data else m["endTime"]
    if end <= start:
        raise AppError(422, "INVALID_TIME", "endTime must be after startTime")
    data["startTime"], data["endTime"] = start, end
    data["updatedAt"] = datetime.now(timezone.utc)
    updated = await db.matches.find_one_and_update(
        {"_id": match_id}, {"$set": data}, return_document=ReturnDocument.AFTER)
    return serialize(updated)


async def delete_match(match_id) -> dict:
    """Delete a match. Everyone who paid is refunded (sum of their MATCH_ENTRY transactions)."""
    async def txn(session):
        m = await db.matches.find_one({"_id": match_id}, session=session)
        if not m:
            raise AppError(404, "MATCH_NOT_FOUND", "Match not found")
        now = datetime.now(timezone.utc)
        cursor = await db.transactions.aggregate(
            [{"$match": {"matchId": match_id, "type": "MATCH_ENTRY"}},
             {"$group": {"_id": "$userId", "paid": {"$sum": "$amount"}}}], session=session)
        payers = await cursor.to_list(None)
        total = 0
        refunded = 0
        for row in payers:
            amount = -row["paid"]
            if amount <= 0:
                continue
            before = await db.wallets.find_one_and_update(
                {"userId": row["_id"]}, {"$inc": {"balance": amount}, "$set": {"updatedAt": now}},
                return_document=ReturnDocument.BEFORE, session=session)
            if before is None:
                continue
            await db.users.update_one({"_id": row["_id"]}, {"$inc": {"walletBalance": amount}}, session=session)
            await db.transactions.insert_one({
                "userId": row["_id"], "type": "REFUND", "amount": amount,
                "balanceBefore": before["balance"], "balanceAfter": before["balance"] + amount,
                "matchId": match_id, "createdAt": now}, session=session)
            total += amount
            refunded += 1
        for coll in (db.room_details, db.match_players, db.joined_matches):
            await coll.delete_many({"matchId": match_id}, session=session)
        await db.matches.delete_one({"_id": match_id}, session=session)
        return {"deleted": True, "refundedUsers": refunded, "refundedAmount": total}

    async with client.start_session() as s:
        return await s.with_transaction(txn)


async def list_users(search: str | None, skip: int, limit: int) -> dict:
    q: dict = {}
    if search and search.strip():
        term = re.escape(search.strip())
        q["$or"] = [{"username": {"$regex": term.lower()}}, {"mobileNumber": {"$regex": term}}]
    total = await db.users.count_documents(q)
    users = await db.users.find(q, {"passwordHash": 0}).sort("createdAt", -1).skip(skip).limit(limit).to_list(limit)
    ids = [u["_id"] for u in users]
    balances = {w["userId"]: w["balance"] async for w in db.wallets.find({"userId": {"$in": ids}})}
    return {"total": total, "users": [{
        "id": str(u["_id"]), "username": u["username"], "mobileNumber": u["mobileNumber"],
        "walletBalance": balances.get(u["_id"], 0), "isActive": u.get("isActive", True),
        "isAdmin": bool(u.get("isAdmin")), "createdAt": u["createdAt"].isoformat()} for u in users]}


async def get_user(user_id) -> dict:
    u = await db.users.find_one({"_id": user_id}, {"passwordHash": 0})
    if not u:
        raise AppError(404, "USER_NOT_FOUND", "User not found")
    w = await db.wallets.find_one({"userId": user_id})
    return {"id": str(u["_id"]), "username": u["username"], "mobileNumber": u["mobileNumber"],
            "walletBalance": w["balance"] if w else 0, "isActive": u.get("isActive", True),
            "isAdmin": bool(u.get("isAdmin")), "createdAt": u["createdAt"].isoformat()}


async def user_transactions(user_id, limit: int = 50) -> list[dict]:
    rows = await db.transactions.find({"userId": user_id}).sort("createdAt", -1).limit(limit).to_list(limit)
    return [{"id": str(t["_id"]), "type": t["type"], "amount": t["amount"],
             "balanceBefore": t["balanceBefore"], "balanceAfter": t["balanceAfter"],
             "reason": t.get("reason"), "matchId": str(t["matchId"]) if t.get("matchId") else None,
             "createdAt": t["createdAt"].isoformat()} for t in rows]


async def adjust_wallet(admin: dict, user_id, action: str, amount: int, reason: str) -> dict:
    """Add or deduct wallet money. One transaction: wallet, user mirror and the audit record."""
    delta = amount if action == "credit" else -amount

    async def txn(session):
        if not await db.users.find_one({"_id": user_id}, {"_id": 1}, session=session):
            raise AppError(404, "USER_NOT_FOUND", "User not found")
        now = datetime.now(timezone.utc)
        flt = {"userId": user_id}
        if delta < 0:
            flt["balance"] = {"$gte": amount}  # never push a wallet below zero
        before = await db.wallets.find_one_and_update(
            flt, {"$inc": {"balance": delta}, "$set": {"updatedAt": now}},
            return_document=ReturnDocument.BEFORE, session=session)
        if before is None:
            w = await db.wallets.find_one({"userId": user_id}, session=session)
            if w is None:
                raise AppError(404, "WALLET_NOT_FOUND", "Wallet not found")
            raise AppError(409, "INSUFFICIENT_BALANCE", f"User only has ₹{w['balance']} in the wallet")
        await db.users.update_one({"_id": user_id}, {"$inc": {"walletBalance": delta}}, session=session)
        await db.transactions.insert_one({
            "userId": user_id, "type": "ADMIN_CREDIT" if delta > 0 else "ADMIN_DEBIT", "amount": delta,
            "balanceBefore": before["balance"], "balanceAfter": before["balance"] + delta,
            "reason": reason, "adminId": admin["_id"], "matchId": None, "createdAt": now}, session=session)
        return {"userId": str(user_id), "amount": delta, "balance": before["balance"] + delta}

    async with client.start_session() as s:
        return await s.with_transaction(txn)
