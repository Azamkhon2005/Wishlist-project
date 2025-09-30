from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from . import models
from .database import get_db

api_key_header = APIKeyHeader(name="X-API-Key")


def get_current_user(
    api_key: str = Security(api_key_header), db: Session = Depends(get_db)
):
    """
    Проверяет API ключ и возвращает пользователя.
    """
    user = db.query(models.User).filter(models.User.api_key == api_key).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return user
