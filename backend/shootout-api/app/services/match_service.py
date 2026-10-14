from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from app.core.config import settings
from app.core.errors import AppError
from app.db.database import client, db

MATCH_NUMBER_START = 100  # first match becomes #101
ROOM_REVEAL_MINUTES = 15  # room id/password are released this long before the match starts


def _now():
    return datetime.now(timezone.utc)


def match_status(m: dict, now=None) -> str:
    now = now or _now()
    if now < m["startTime"]:
        return "upcoming"
    return "current" if now < m["endTime"] else "previous"


def serialize(m: dict, my_players: dict | None = None, now=None, force_joined: bool = False) -> dict:
    names = (my_players or {}).get(m["_id"], [])
    left = max(m["maxPlayers"] - m["registeredPlayers"], 0)
    return {
        "id": str(m["_id"]), "matchNumber": m["matchNumber"], "game": m["game"], "title": m["title"],
        "startTime": m["startTime"].isoformat(), "endTime": m["endTime"].isoformat(),
        "prizePool": m["prizePool"], "perKill": m["perKill"], "entryFee": m["entryFee"],
        "teamType": m["teamType"], "mode": m["mode"], "map": m["map"],
        "maxPlayers": m["maxPlayers"], "registeredPlayers": m["registeredPlayers"],
        "spotsLeft": left, "isFull": left == 0, "prizeBreakdown": m.get("prizeBreakdown", []),
        "status": match_status(m, now),
        "joined": force_joined or len(names) > 0,
        "myPlayers": names,
    }


async def _my_players(user_id, match_ids: list) -> dict:
    """matchId -> in-game names this user has added to that match."""
    out: dict = {}
    cur = db.match_players.find({"userId": user_id, "matchId": {"$in": match_ids}}).sort("joinedAt", 1)
    async for p in cur:
        out.setdefault(p["matchId"], []).append(p["inGameName"])
    return out


def _status_query(status: str | None, now) -> dict:
    if status == "upcoming":
        return {"startTime": {"$gt": now}}
    if status == "current":
        return {"startTime": {"$lte": now}, "endTime": {"$gt": now}}
    if status == "previous":
        return {"endTime": {"$lte": now}}
    return {}


async def list_matches(game: str, status: str | None, user_id) -> list[dict]:
    now = _now()
    q = {"game": game, **_status_query(status, now)}
    matches = await db.matches.find(q).sort("startTime", 1 if status == "upcoming" else -1).to_list(200)
    players = await _my_players(user_id, [m["_id"] for m in matches])
    return [serialize(m, players, now) for m in matches]


async def get_match(match_id, user_id) -> dict:
    m = await db.matches.find_one({"_id": match_id})
    if not m:
        raise AppError(404, "MATCH_NOT_FOUND", "Match not found")
    return serialize(m, await _my_players(user_id, [m["_id"]]))


async def list_user_matches(user_id, status: str | None) -> list[dict]:
    now = _now()
    ids = [j["matchId"] async for j in db.joined_matches.find({"userId": user_id})]
    q = {"_id": {"$in": ids}, **_status_query(status, now)}
    matches = await db.matches.find(q).sort("startTime", -1).to_list(200)
    players = await _my_players(user_id, [m["_id"] for m in matches])
    return [serialize(m, players, now, force_joined=True) for m in matches]


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(settings.local_timezone))
    return dt.astimezone(timezone.utc)


async def create_match(req) -> dict:
    start, end = _to_utc(req.startTime), _to_utc(req.endTime)
    if end <= start:
        raise AppError(422, "INVALID_TIME", "endTime must be after startTime")
    counter = await db.counters.find_one_and_update(
        {"_id": "matchNumber"}, {"$inc": {"seq": 1}}, upsert=True, return_document=ReturnDocument.AFTER)
    now = _now()
    doc = req.model_dump(mode="python")
    doc["game"] = req.game.value
    doc.update(startTime=start, endTime=end, matchNumber=MATCH_NUMBER_START + counter["seq"],
               registeredPlayers=0, createdAt=now, updatedAt=now)
    res = await db.matches.insert_one(doc)
    doc["_id"] = res.inserted_id
    return serialize(doc)


async def join_match(match_id, user: dict, names: list[str]) -> dict:
    """Add 1-4 players (exact in-game names) to a match. Can be called repeatedly by the same user.
    Fee = entryFee x number of players. Everything happens in one transaction."""
    keys = [n.lower() for n in names]
    n = len(names)

    async def txn(session):
        now = _now()
        m = await db.matches.find_one({"_id": match_id}, session=session)
        if not m:
            raise AppError(404, "MATCH_NOT_FOUND", "Match not found")
        if match_status(m, now) != "upcoming":
            raise AppError(400, "MATCH_NOT_JOINABLE", "Match is no longer open for joining")
        taken = [p["inGameName"] async for p in
                 db.match_players.find({"matchId": match_id, "nameKey": {"$in": keys}}, session=session)]
        if taken:
            raise AppError(409, "DUPLICATE_PLAYER_NAME",
                           f"Already registered in this match: {', '.join(taken)}")
        r = await db.matches.update_one(
            {"_id": match_id, "registeredPlayers": {"$lte": m["maxPlayers"] - n}},
            {"$inc": {"registeredPlayers": n}, "$set": {"updatedAt": now}}, session=session)
        if r.matched_count == 0:
            left = max(m["maxPlayers"] - m["registeredPlayers"], 0)
            if left == 0:
                raise AppError(409, "MATCH_FULL", "Match is full")
            raise AppError(409, "NOT_ENOUGH_SPOTS", f"Only {left} spot{'s' if left != 1 else ''} left")
        fee = m["entryFee"] * n
        before = await db.wallets.find_one_and_update(
            {"userId": user["_id"], "balance": {"$gte": fee}},
            {"$inc": {"balance": -fee}, "$set": {"updatedAt": now}},
            return_document=ReturnDocument.BEFORE, session=session)
        if before is None:
            raise AppError(400, "INSUFFICIENT_BALANCE", "Insufficient wallet balance")
        try:
            await db.match_players.insert_many(
                [{"matchId": match_id, "userId": user["_id"], "inGameName": nm, "nameKey": k, "joinedAt": now}
                 for nm, k in zip(names, keys)], session=session)
        except DuplicateKeyError:
            raise AppError(409, "DUPLICATE_PLAYER_NAME", "One of these in-game names is already registered in this match")
        await db.joined_matches.update_one(
            {"userId": user["_id"], "matchId": match_id},
            {"$inc": {"playersCount": n}, "$set": {"updatedAt": now},
             "$setOnInsert": {"joinedAt": now, "status": "joined"}},
            upsert=True, session=session)
        await db.users.update_one({"_id": user["_id"]}, {"$inc": {"walletBalance": -fee}}, session=session)
        await db.transactions.insert_one({
            "userId": user["_id"], "type": "MATCH_ENTRY", "amount": -fee, "playersCount": n,
            "balanceBefore": before["balance"], "balanceAfter": before["balance"] - fee,
            "matchId": match_id, "createdAt": now}, session=session)
        return {"matchId": str(match_id), "balance": before["balance"] - fee, "feeCharged": fee,
                "playersAdded": n, "registeredPlayers": m["registeredPlayers"] + n}

    async with client.start_session() as s:
        return await s.with_transaction(txn)


async def set_room(match_id, roomId: str, roomPassword: str) -> dict:
    if not await db.matches.find_one({"_id": match_id}, {"_id": 1}):
        raise AppError(404, "MATCH_NOT_FOUND", "Match not found")
    await db.room_details.update_one(
        {"matchId": match_id}, {"$set": {"roomId": roomId, "roomPassword": roomPassword}}, upsert=True)
    return {"matchId": str(match_id)}


async def _match_for_participant(match_id, user: dict) -> dict:
    """The match, if it exists and the user may see its room info (joined players and admins only)."""
    m = await db.matches.find_one({"_id": match_id})
    if not m:
        raise AppError(404, "MATCH_NOT_FOUND", "Match not found")
    if not user.get("isAdmin") and not await db.joined_matches.find_one(
            {"userId": user["_id"], "matchId": match_id}):
        raise AppError(403, "NOT_JOINED", "Join this match to see room details")
    return m


async def get_room(match_id, user: dict) -> dict:
    """Match info plus room id/password. The secrets are only sent from 15 min before the start
    (decided here on the server, so a changed phone clock cannot reveal them early)."""
    m = await _match_for_participant(match_id, user)
    now = _now()
    reveal_at = m["startTime"] - timedelta(minutes=ROOM_REVEAL_MINUTES)
    visible = bool(user.get("isAdmin")) or now >= reveal_at
    room = await db.room_details.find_one({"matchId": match_id}) if visible else None
    return {
        "matchId": str(match_id), "game": m["game"], "title": m["title"], "matchNumber": m["matchNumber"],
        "startTime": m["startTime"].isoformat(), "endTime": m["endTime"].isoformat(),
        "status": match_status(m, now), "revealAt": reveal_at.isoformat(), "serverTime": now.isoformat(),
        "roomVisible": visible, "roomPublished": room is not None,
        "roomId": room["roomId"] if room else None,
        "roomPassword": room["roomPassword"] if room else None,
    }


async def list_players(match_id, user: dict) -> dict:
    """In-game names of everyone registered in the match (no mobile numbers or usernames)."""
    await _match_for_participant(match_id, user)
    rows = await db.match_players.find({"matchId": match_id}).sort("joinedAt", 1).to_list(500)
    return {"matchId": str(match_id), "total": len(rows),
            "players": [{"inGameName": r["inGameName"], "isMine": r["userId"] == user["_id"]} for r in rows]}
