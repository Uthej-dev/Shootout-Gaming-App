"""Make an existing user an admin.
Run from backend/shootout-api with the venv active:
    python -m scripts.make_admin <username>
"""
import asyncio
import sys

from app.db.database import client, db


async def main(username: str):
    try:
        r = await db.users.update_one({"username": username.lower()}, {"$set": {"isAdmin": True}})
        print(f"'{username}' is now an admin." if r.matched_count else f"No user named '{username}'.")
    finally:
        await client.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m scripts.make_admin <username>")
    asyncio.run(main(sys.argv[1]))
