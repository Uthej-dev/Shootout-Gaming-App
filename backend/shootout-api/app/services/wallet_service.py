from app.db.database import db


async def get_wallet(user_id) -> dict:
    w = await db.wallets.find_one({"userId": user_id})
    return {"balance": w["balance"] if w else 0}


async def list_transactions(user_id, limit: int = 50) -> list[dict]:
    out = []
    async for t in db.transactions.find({"userId": user_id}).sort("createdAt", -1).limit(limit):
        out.append({"id": str(t["_id"]), "type": t["type"], "amount": t["amount"],
                    "balanceBefore": t["balanceBefore"], "balanceAfter": t["balanceAfter"],
                    "matchId": str(t["matchId"]) if t.get("matchId") else None,
                    "createdAt": t["createdAt"].isoformat()})
    return out
