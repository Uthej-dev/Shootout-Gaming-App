from pymongo import ASCENDING, AsyncMongoClient
from app.core.config import settings

# One client for the whole app (reused across requests).
client = AsyncMongoClient(settings.mongodb_url, tz_aware=True)
db = client[settings.database_name]


async def init_indexes():
    await db.users.create_index("username", unique=True)
    await db.users.create_index("mobileNumber", unique=True)
    await db.matches.create_index("matchNumber", unique=True)
    await db.matches.create_index([("game", ASCENDING), ("startTime", ASCENDING)])
    await db.joined_matches.create_index([("userId", ASCENDING), ("matchId", ASCENDING)], unique=True)
    await db.wallets.create_index("userId", unique=True)
    # one row per player added to a match; the unique index stops the same in-game name joining twice
    await db.match_players.create_index([("matchId", ASCENDING), ("nameKey", ASCENDING)], unique=True)
    await db.match_players.create_index([("userId", ASCENDING), ("matchId", ASCENDING)])
    await db.room_details.create_index("matchId", unique=True)
    await db.transactions.create_index([("userId", ASCENDING), ("createdAt", -1)])
