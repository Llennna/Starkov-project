from __future__ import annotations

import re
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)


class ProfileOut(BaseModel):
    full_name: str
    tagline: str
    city: str
    birth_date: date
    age: int
    avatar_path: str
    intro: str
    current_study: str
    previous_study: str
    interests: list[str]
    quote: str


class TimelineEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    period_label: str
    title: str
    description: str
    location: str
    sort_order: int


class ProjectBase(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=12, max_length=1200)
    stack: str = Field(min_length=2, max_length=255)
    project_url: str = Field(min_length=8, max_length=255)
    year: int = Field(ge=2018, le=2100)
    featured: bool = False
    sort_order: int = Field(ge=0, le=100)

    @field_validator("title", "description", "stack")
    @classmethod
    def strip_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Поле не может быть пустым.")
        return cleaned

    @field_validator("project_url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        cleaned = value.strip()
        if not URL_PATTERN.match(cleaned):
            raise ValueError("Ссылка должна начинаться с http:// или https://")
        return cleaned


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass


class ProjectOut(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ContactMessageCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=120)
    message: str = Field(min_length=10, max_length=1500)

    @field_validator("name", "message")
    @classmethod
    def strip_message_fields(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Поле не может быть пустым.")
        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not EMAIL_PATTERN.match(cleaned):
            raise ValueError("Введите корректный email.")
        return cleaned


class ContactMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    message: str
    created_at: datetime
    is_read: bool


class StatusResponse(BaseModel):
    message: str


class LoginRequest(BaseModel):
    username: str = Field(min_length=2, max_length=60)
    password: str = Field(min_length=4, max_length=120)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


class PortfolioPayload(BaseModel):
    profile: ProfileOut
    timeline: list[TimelineEventOut]
    projects: list[ProjectOut]

