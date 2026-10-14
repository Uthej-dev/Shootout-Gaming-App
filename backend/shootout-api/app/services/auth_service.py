from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError
from app.core.config import settings
from app.core.errors import AppError
from app.core.security import create_access_token, hash_password, verify_password
from app.db.database import db
from app.schemas.auth import LoginRequest, RegisterRequest


def public_user(u: dict) -> dict:
    return {"id": str(u["_id"]), "username": u["username"], "mobileNumber": u["mobileNumber"],
            "isAdmin": bool(u.get("isAdmin"))}


async def register_user(req: RegisterRequest) -> dict:
    now = datetime.now(timezone.utc)
    bonus = settings.dev_signup_bonus
    user = {
        "username": req.username.lower(), "mobileNumber": req.mobileNumber,
        "passwordHash": hash_password(req.password), "walletBalance": bonus,
        "isActive": True, "isAdmin": False, "createdAt": now, "updatedAt": now,
    }
    if await db.users.find_one({"username": user["username"]}):
        raise AppError(409, "USERNAME_EXISTS", "Username already exists")
    if await db.users.find_one({"mobileNumber": req.mobileNumber}):
        raise AppError(409, "MOBILE_EXISTS", "Mobile number already registered")
    try:
        res = await db.users.insert_one(user)
    except DuplicateKeyError:
        raise AppError(409, "USER_EXISTS", "Username or mobile number already registered")
    user["_id"] = res.inserted_id
    await db.wallets.insert_one({"userId": res.inserted_id, "balance": bonus, "updatedAt": now})
    if bonus:
        await db.transactions.insert_one({
            "userId": res.inserted_id, "type": "BONUS", "amount": bonus,
            "balanceBefore": 0, "balanceAfter": bonus, "matchId": None, "createdAt": now})
    return public_user(user)


async def login_user(req: LoginRequest) -> dict:
    ident = req.identifier.strip()
    user = await db.users.find_one({"$or": [{"username": ident.lower()}, {"mobileNumber": ident}]})
    if not user or not verify_password(req.password, user["passwordHash"]) or not user.get("isActive", True):
        raise AppError(401, "INVALID_CREDENTIALS", "Invalid username/mobile or password")
    return {"accessToken": create_access_token(str(user["_id"])), "tokenType": "bearer", "user": public_user(user)}
