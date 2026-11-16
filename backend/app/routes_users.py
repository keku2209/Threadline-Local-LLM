from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .schemas import UserOut

router = APIRouter(prefix='/api/users', tags=['users'])

@router.get('', response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return list(db.scalars(select(User).order_by(User.username)))

@router.get('/{user_id}', response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user: raise HTTPException(404, 'User not found')
    return user
