import re
from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.core.errors import AppError, ok, parse_oid
from app.schemas.match import Game, JoinRequest
from app.services import match_service

router = APIRouter(prefix="/matches", tags=["matches"])
_OID = re.compile(r"^[0-9a-fA-F]{24}$")


def _game(value: str) -> str:
    try:
        return Game(value.upper()).value
    except ValueError:
        raise AppError(404, "GAME_NOT_FOUND", f"Unknown game '{value}'")


# NOTE: the two-segment routes with a fixed suffix (/room, /players) must be registered BEFORE
# /{game}/{status}, otherwise that generic route would swallow them.
@router.get("/{match_id}/room")
async def room(match_id: str, user=Depends(get_current_user)):
    return ok(await match_service.get_room(parse_oid(match_id, "match id"), user))


@router.get("/{match_id}/players")
async def players(match_id: str, user=Depends(get_current_user)):
    return ok(await match_service.list_players(parse_oid(match_id, "match id"), user))


@router.post("/{match_id}/join")
async def join(match_id: str, body: JoinRequest, user=Depends(get_current_user)):
    data = await match_service.join_match(parse_oid(match_id, "match id"), user, body.players)
    return ok(data, "Joined match successfully")


# GET /matches/{game} and GET /matches/{match_id} share one path shape, so dispatch on the value.
@router.get("/{key}")
async def game_or_match(key: str, user=Depends(get_current_user)):
    if _OID.match(key):
        return ok(await match_service.get_match(parse_oid(key), user["_id"]))
    return ok(await match_service.list_matches(_game(key), None, user["_id"]))


@router.get("/{game}/{status}")
async def by_status(game: str, status: str, user=Depends(get_current_user)):
    if status not in ("upcoming", "current", "previous"):
        raise AppError(404, "NOT_FOUND", "Not found")
    return ok(await match_service.list_matches(_game(game), status, user["_id"]))
