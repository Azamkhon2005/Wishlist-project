from typing import Optional

from pydantic import BaseModel, Field


class WishBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    link: Optional[str] = None
    price_estimate: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = None


class WishCreate(WishBase):
    pass


class WishUpdate(WishBase):
    pass


class WishInDB(WishBase):
    id: int
    owner_id: int

    class Config:
        {"orm_mode": True}


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=72)


class UserInDB(UserBase):
    id: int
    api_key: Optional[str]

    class Config:
        {"orm_mode": True}
