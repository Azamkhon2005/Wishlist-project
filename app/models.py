from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    api_key = Column(String, unique=True, index=True)
    wishes = relationship("Wish", back_populates="owner", cascade="all, delete-orphan")


class Wish(Base):
    __tablename__ = "wishes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    link = Column(String)
    price_estimate = Column(Float)
    notes = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="wishes")
