from typing import Literal
from pydantic import BaseModel, Field, field_validator


class WalletAdjust(BaseModel):
    """Admin adds or deducts wallet money. A reason is mandatory and is stored in the transaction."""
    action: Literal["credit", "debit"]
    amount: int = Field(gt=0, le=100000)
    reason: str = Field(min_length=3, max_length=200)

    @field_validator("reason")
    @classmethod
    def strip_reason(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Reason must be at least 3 characters")
        return v
