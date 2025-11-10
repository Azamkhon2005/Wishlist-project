import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..custom_routing import SecureJsonRoute
from ..database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = router = APIRouter(
    prefix="/users", tags=["Users"], route_class=SecureJsonRoute
)


@router.post("/", response_model=schemas.UserInDB, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = security.get_password_hash(user.password)

    api_key = security.generate_api_key()

    db_user = models.User(
        username=user.username, hashed_password=hashed_password, api_key=api_key
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
