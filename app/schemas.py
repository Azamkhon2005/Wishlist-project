from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class WishBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    link: Optional[str] = None
    price_estimate: Optional[Decimal] = Field(
        None, gt=Decimal("0.0"), max_digits=18, decimal_places=2
    )
    notes: Optional[str] = None


class WishCreate(WishBase):
    pass


class WishUpdate(WishBase):
    pass


class WishInDB(WishBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72)


class UserInDB(UserBase):
    id: int
    api_key: Optional[str]

    class Config:
        from_attributes = True
