import uuid

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr = Field(max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=40)


class AdminCreate(UserCreate):
    role: str = "admin"
    is_verified: bool = True


class UserPublic(UserBase):
    id: uuid.UUID


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
