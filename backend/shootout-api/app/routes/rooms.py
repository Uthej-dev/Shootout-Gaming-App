"""Admin endpoints (all require an admin user): matches CRUD, room details, registered users."""
from fastapi import APIRouter, Depends, Query
from app.core.deps import get_current_user, require_admin
from app.core.errors import AppError, ok, parse_oid
from app.schemas.match import Game, MatchCreate, MatchUpdate, RoomSet
from app.schemas.wallet import WalletAdjust
from app.services import admin_service, match_service

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/matches")
async def list_matches(game: str | None = None, status: str | None = None):
    g = None
    if game:
        try:
            g = Game(game.upper()).value
        except ValueError:
            raise AppError(404, "GAME_NOT_FOUND", f"Unknown game '{game}'")
    if status and status not in ("upcoming", "current", "previous"):
        raise AppError(422, "INVALID_STATUS", "status must be upcoming, current or previous")
    return ok(await admin_service.list_matches(g, status))


@router.post("/matches", status_code=201)
async def create_match(req: MatchCreate):
    return ok(await match_service.create_match(req), "Match created")


@router.put("/matches/{match_id}")
async def update_match(match_id: str, req: MatchUpdate):
    return ok(await admin_service.update_match(parse_oid(match_id, "match id"), req), "Match updated")


@router.delete("/matches/{match_id}")
async def delete_match(match_id: str):
    return ok(await admin_service.delete_match(parse_oid(match_id, "match id")), "Match deleted")


@router.put("/matches/{match_id}/room")
async def set_room(match_id: str, req: RoomSet):
    return ok(await match_service.set_room(parse_oid(match_id, "match id"), req.roomId, req.roomPassword),
              "Room details saved")


@router.get("/users")
async def users(search: str | None = None, skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
    return ok(await admin_service.list_users(search, skip, limit))


@router.get("/users/{user_id}")
async def user_detail(user_id: str):
    return ok(await admin_service.get_user(parse_oid(user_id, "user id")))


@router.get("/users/{user_id}/transactions")
async def user_transactions(user_id: str):
    return ok(await admin_service.user_transactions(parse_oid(user_id, "user id")))


@router.post("/users/{user_id}/wallet")
async def adjust_wallet(user_id: str, req: WalletAdjust, admin=Depends(get_current_user)):
    data = await admin_service.adjust_wallet(admin, parse_oid(user_id, "user id"), req.action, req.amount, req.reason)
    return ok(data, "Money added to wallet" if req.action == "credit" else "Money deducted from wallet")
