from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .crud import search
from .database import get_db
from .schemas import SearchOut

router = APIRouter(prefix='/api/search', tags=['search'])

@router.get('', response_model=SearchOut)
def search_content(q: str = Query(min_length=1), db: Session = Depends(get_db)):
    posts, communities = search(db, q)
    return {'posts': posts, 'communities': communities}
