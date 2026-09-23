from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def reject_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("Value cannot be empty")
    return value.strip()


class EventBase(BaseModel):
    title: str = Field(min_length=1)
    venue: str = Field(min_length=1)
    capacity: int = Field(gt=0)
    organizer: str = Field(min_length=1)
    status: Literal["Open", "Closed"]

    _required_text = field_validator(
        "title", "venue", "organizer", mode="before"
    )(reject_blank)


class EventCreate(EventBase):
    pass


class EventRead(EventBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ReservationCreate(BaseModel):
    student_name: str = Field(min_length=1)
    roll_number: str = Field(min_length=1)
    email: EmailStr

    _required_text = field_validator(
        "student_name", "roll_number", mode="before"
    )(reject_blank)


class ReservationRead(ReservationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    event_id: int


class AvailabilityRead(BaseModel):
    capacity: int
    booked: int
    remaining: int
