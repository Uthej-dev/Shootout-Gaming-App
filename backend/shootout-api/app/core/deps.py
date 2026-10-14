from bson import ObjectId
from fastapi import Depends
from fastapi.security import HTTPBearer
from app.core.errors import AppError
from app.core.security import decode_token
from app.db.database import db

bearer = HTTPBearer(auto_error=False)


async def get_current_user(creds=Depends(bearer)) -> dict:
    if not creds:
        raise AppError(401, "NOT_AUTHENTICATED", "Not authenticated")
    try:
        uid = ObjectId(decode_token(creds.credentials)["sub"])
    except Exception:
        raise AppError(401, "INVALID_TOKEN", "Invalid or expired token")
    user = await db.users.find_one({"_id": uid})
    if not user or not user.get("isActive", True):
        raise AppError(401, "INVALID_TOKEN", "User not found or inactive")
    return user


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if not user.get("isAdmin"):
        raise AppError(403, "FORBIDDEN", "Admin access required")
    return user
