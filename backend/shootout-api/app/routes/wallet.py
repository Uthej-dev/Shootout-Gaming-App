from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.core.errors import ok
from app.services import wallet_service

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("")
async def wallet(user=Depends(get_current_user)):
    return ok(await wallet_service.get_wallet(user["_id"]))


@router.get("/transactions")
async def transactions(user=Depends(get_current_user)):
    return ok(await wallet_service.list_transactions(user["_id"]))
