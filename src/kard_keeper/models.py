from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date


class GiftCard(BaseModel):
    name: str = Field(..., min_length=1)
    balance: float = Field(..., ge=0)
    expires: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Card name cannot be empty")
        return v
