"""Create sample BGMI matches (0 players joined) for testing.

Run from backend/shootout-api with the venv active:
    python -m scripts.seed_matches          # skips if upcoming BGMI matches already exist
    python -m scripts.seed_matches --force  # add them anyway
"""
import asyncio
import sys
from datetime import datetime, timedelta, timezone

from app.db.database import client, db, init_indexes
from app.schemas.match import MatchCreate
from app.services import match_service


def pr(*amounts):
    return [{"rank": i + 1, "amount": a} for i, a in enumerate(amounts)]


# (hours from now, prize pool, per kill, entry fee, team, mode, map, breakdown)
SAMPLES = [
    (2, 600, 10, 14, "Squad", "TPP", "Erangel", pr(300, 100, 70, 50, 40, 40)),
    (3, 1000, 15, 25, "Squad", "TPP", "Miramar", pr(500, 200, 120, 80, 60, 40)),
    (5, 300, 5, 10, "Solo", "TPP", "Sanhok", pr(150, 75, 40, 20, 15)),
    (8, 1500, 20, 40, "Duo", "FPP", "Erangel", pr(700, 350, 200, 120, 80, 50)),
    (12, 2500, 25, 60, "Squad", "FPP", "Miramar", pr(1000, 600, 400, 250, 150, 100)),
    (24, 800, 10, 20, "Squad", "TPP", "Erangel", pr(400, 200, 100, 60, 40)),
]


async def main(force: bool):
    try:
        await _seed(force)
    finally:
        await client.close()


async def _seed(force: bool):
    await init_indexes()
    now = datetime.now(timezone.utc)
    if not force and await db.matches.count_documents({"game": "BGMI", "startTime": {"$gt": now}}):
        print("Upcoming BGMI matches already exist. Use --force to add more.")
        return
    for hours, pool, kill, fee, team, mode, mp, breakdown in SAMPLES:
        start = now + timedelta(hours=hours)
        m = MatchCreate(
            game="BGMI", title="Warfield", startTime=start, endTime=start + timedelta(minutes=30),
            prizePool=pool, perKill=kill, entryFee=fee, teamType=team, mode=mode, map=mp,
            maxPlayers=100, prizeBreakdown=breakdown,
        )
        out = await match_service.create_match(m)
        print(f"Created {out['title']} #{out['matchNumber']}  0/{out['maxPlayers']}  fee ₹{out['entryFee']}")


if __name__ == "__main__":
    asyncio.run(main("--force" in sys.argv))
