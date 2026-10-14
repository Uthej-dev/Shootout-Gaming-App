from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class Game(str, Enum):
    BGMI = "BGMI"
    BGMI_TDM = "BGMI_TDM"
    FREE_FIRE = "FREE_FIRE"


class PrizeRank(BaseModel):
    rank: int = Field(ge=1)
    amount: int = Field(ge=0)


class MatchCreate(BaseModel):
    game: Game
    title: str
    startTime: datetime  # naive = LOCAL_TIMEZONE, aware = converted to UTC
    endTime: datetime
    prizePool: int = Field(ge=0)
    perKill: int = Field(ge=0)
    entryFee: int = Field(ge=0)
    teamType: str = Field(pattern="^(Solo|Duo|Squad)$")
    mode: str = Field(pattern="^(TPP|FPP)$")
    map: str
    maxPlayers: int = Field(gt=0)
    prizeBreakdown: list[PrizeRank] = []


class RoomSet(BaseModel):
    roomId: str
    roomPassword: str


class JoinRequest(BaseModel):
    """One join action: 1-4 players, each with their exact in-game name."""
    players: list[str] = Field(min_length=1, max_length=4)

    @field_validator("players")
    @classmethod
    def clean_names(cls, v: list[str]) -> list[str]:
        out, seen = [], set()
        for raw in v:
            name = raw.strip()
            if not 1 <= len(name) <= 30:
                raise ValueError("In-game name must be 1-30 characters")
            if name.lower() in seen:
                raise ValueError(f"Duplicate in-game name in request: {name}")
            seen.add(name.lower())
            out.append(name)
        return out


class MatchUpdate(BaseModel):
    """Partial update: only the fields that are sent are changed."""
    game: Game | None = None
    title: str | None = None
    startTime: datetime | None = None
    endTime: datetime | None = None
    prizePool: int | None = Field(default=None, ge=0)
    perKill: int | None = Field(default=None, ge=0)
    entryFee: int | None = Field(default=None, ge=0)
    teamType: str | None = Field(default=None, pattern="^(Solo|Duo|Squad)$")
    mode: str | None = Field(default=None, pattern="^(TPP|FPP)$")
    map: str | None = None
    maxPlayers: int | None = Field(default=None, gt=0)
    prizeBreakdown: list[PrizeRank] | None = None
