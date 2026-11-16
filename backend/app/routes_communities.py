from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import Community
from .schemas import CommunityOut

router = APIRouter(prefix='/api/communities', tags=['communities'])

@router.get('', response_model=list[CommunityOut])
def list_communities(db: Session = Depends(get_db)):
    return list(db.scalars(select(Community).order_by(Community.member_count.desc())))

@router.get('/{community_id}', response_model=CommunityOut)
def get_community(community_id: str, db: Session = Depends(get_db)):
    community = db.get(Community, community_id)
    if not community: raise HTTPException(404, 'Community not found')
    return community
