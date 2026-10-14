from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.core.errors import ok
from app.services import auth_service, match_service, wallet_service

router = APIRouter(prefix="/users/me", tags=["users"])


@router.get("")
async def me(user=Depends(get_current_user)):
    data = auth_service.public_user(user)
    data["walletBalance"] = (await wallet_service.get_wallet(user["_id"]))["balance"]
    return ok(data)


@router.get("/joined-matches")
async def joined(user=Depends(get_current_user)):
    return ok(await match_service.list_user_matches(user["_id"], None))


@router.get("/current-matches")
async def current(user=Depends(get_current_user)):
    return ok(await match_service.list_user_matches(user["_id"], "current"))


@router.get("/previous-matches")
async def previous(user=Depends(get_current_user)):
    return ok(await match_service.list_user_matches(user["_id"], "previous"))
