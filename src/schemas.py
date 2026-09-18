import json
from datetime import datetime
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class Action(str, Enum):
    REQUEST_PHOTOS = "REQUEST_PHOTOS"
    APPROVE_RETURN = "APPROVE_RETURN"
    OPEN_SHIPPING_INVESTIGATION = "OPEN_SHIPPING_INVESTIGATION"
    REPLACE_CORRECT_ITEM = "REPLACE_CORRECT_ITEM"
    NEEDS_MORE_INFORMATION = "NEEDS_MORE_INFORMATION"
    APPROVE_REFUND_OR_REPLACEMENT = "APPROVE_REFUND_OR_REPLACEMENT"
    REQUEST_DEFECT_EVIDENCE = "REQUEST_DEFECT_EVIDENCE"
    APPROVE_REPLACEMENT = "APPROVE_REPLACEMENT"
    REJECT_OUTSIDE_WINDOW = "REJECT_OUTSIDE_WINDOW"
    WAIT_AND_TRACK = "WAIT_AND_TRACK"
    OFFER_REPLACEMENT_OR_REFUND = "OFFER_REPLACEMENT_OR_REFUND"
    CANCEL_AND_REFUND = "CANCEL_AND_REFUND"
    CANNOT_CANCEL_AFTER_DISPATCH = "CANNOT_CANCEL_AFTER_DISPATCH"
    REJECT_OPENED_ITEM = "REJECT_OPENED_ITEM"
    REJECT_FOOD_RETURN = "REJECT_FOOD_RETURN"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TicketCreate(BaseModel):
     message: str = Field(min_length=1, max_length=5000)


class DecisionResponse(BaseModel):
    action: Action
    confidence: float = Field(ge=0, le=1)
    reason: str = Field(min_length=1)
    sources: list[str]

    @field_validator("sources", mode="before")
    @classmethod
    def parse_sources(cls, value):
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass

            return [source for source in value.split(",") if source]

        return value


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    message: str
    created_at: datetime
    decision: DecisionResponse | None