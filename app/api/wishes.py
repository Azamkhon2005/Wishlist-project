from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/wishes", tags=["Wishes"])


@router.post("/", response_model=schemas.WishInDB, status_code=status.HTTP_201_CREATED)
def create_wish(
    wish: schemas.WishCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_wish = models.Wish(**wish.dict(), owner_id=current_user.id)
    db.add(db_wish)
    db.commit()
    db.refresh(db_wish)
    return db_wish


@router.get("/", response_model=List[schemas.WishInDB])
def read_wishes(
    price_lt: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Wish).filter(models.Wish.owner_id == current_user.id)
    if price_lt is not None:
        query = query.filter(models.Wish.price_estimate < price_lt)
    return query.all()


def get_owner_wish(wish_id: int, db: Session, current_user: models.User):
    wish = db.query(models.Wish).filter(models.Wish.id == wish_id).first()
    if not wish:
        raise HTTPException(status_code=404, detail="Wish not found")
    if wish.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return wish


@router.get("/{wish_id}", response_model=schemas.WishInDB)
def read_wish(
    wish_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return get_owner_wish(wish_id, db, current_user)


@router.put("/{wish_id}", response_model=schemas.WishInDB)
def update_wish(
    wish_id: int,
    wish_update: schemas.WishUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_wish = get_owner_wish(wish_id, db, current_user)
    for key, value in wish_update.dict(exclude_unset=True).items():
        setattr(db_wish, key, value)
    db.commit()
    db.refresh(db_wish)
    return db_wish


@router.delete("/{wish_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wish(
    wish_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_wish = get_owner_wish(wish_id, db, current_user)
    db.delete(db_wish)
    db.commit()
