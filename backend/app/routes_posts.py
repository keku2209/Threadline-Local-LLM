from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from .crud import apply_vote, list_comments, list_posts
from .ai_service import analyze_discussion
from .database import get_db
from .models import Comment, Community, Post, User
from .schemas import AnalysisOut, CommentCreate, CommentOut, DiscussionComment, DiscussionOut, PostCreate, PostOut, VoteRequest

router = APIRouter(prefix='/api', tags=['posts'])


def require(db: Session, model, object_id: str, label: str):
    item = db.get(model, object_id)
    if not item: raise HTTPException(404, f'{label} not found')
    return item

@router.get('/posts', response_model=list[PostOut])
def get_posts(community_id: str | None = Query(default=None), db: Session = Depends(get_db)):
    return list_posts(db, community_id)

@router.get('/posts/{post_id}', response_model=PostOut)
def get_post(post_id: str, db: Session = Depends(get_db)):
    post = db.scalar(select(Post).options(joinedload(Post.author), joinedload(Post.community)).where(Post.id == post_id))
    return post or (_ for _ in ()).throw(HTTPException(404, 'Post not found'))

@router.post('/posts', response_model=PostOut, status_code=201)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
    require(db, User, payload.author_id, 'Author')
    require(db, Community, payload.community_id, 'Community')
    post = Post(id=f'p{int(datetime.utcnow().timestamp() * 1000)}', **payload.model_dump())
    db.add(post); db.commit(); db.refresh(post)
    return db.scalar(select(Post).options(joinedload(Post.author), joinedload(Post.community)).where(Post.id == post.id))

@router.get('/posts/{post_id}/comments', response_model=list[CommentOut])
def get_comments(post_id: str, db: Session = Depends(get_db)):
    require(db, Post, post_id, 'Post')
    return list_comments(db, post_id)

@router.post('/posts/{post_id}/comments', response_model=CommentOut, status_code=201)
def create_comment(post_id: str, payload: CommentCreate, db: Session = Depends(get_db)):
    post = require(db, Post, post_id, 'Post'); require(db, User, payload.author_id, 'Author')
    if payload.parent_comment_id:
        parent = require(db, Comment, payload.parent_comment_id, 'Parent comment')
        if parent.post_id != post_id: raise HTTPException(400, 'Parent comment belongs to another post')
    comment = Comment(id=f'cm{int(datetime.utcnow().timestamp() * 1000000)}', post_id=post_id, **payload.model_dump())
    post.comment_count += 1; db.add(comment); db.commit(); db.refresh(comment)
    return db.scalar(select(Comment).options(joinedload(Comment.author)).where(Comment.id == comment.id))

@router.post('/posts/{post_id}/vote')
def vote_post(post_id: str, payload: VoteRequest, db: Session = Depends(get_db)):
    require(db, Post, post_id, 'Post'); require(db, User, payload.user_id, 'User')
    return {'score': apply_vote(db, user_id=payload.user_id, value=payload.value, post_id=post_id)}

@router.post('/comments/{comment_id}/replies', response_model=CommentOut, status_code=201)
def reply(comment_id: str, payload: CommentCreate, db: Session = Depends(get_db)):
    parent = require(db, Comment, comment_id, 'Comment')
    payload.parent_comment_id = comment_id
    return create_comment(parent.post_id, payload, db)

@router.post('/comments/{comment_id}/vote')
def vote_comment(comment_id: str, payload: VoteRequest, db: Session = Depends(get_db)):
    require(db, Comment, comment_id, 'Comment'); require(db, User, payload.user_id, 'User')
    return {'score': apply_vote(db, user_id=payload.user_id, value=payload.value, comment_id=comment_id)}

@router.get('/posts/{post_id}/discussion', response_model=DiscussionOut)
def get_discussion(post_id: str, db: Session = Depends(get_db)):
    post = get_post(post_id, db); rows = list_comments(db, post_id)
    def build(parent_id: str | None) -> list[DiscussionComment]:
        return [DiscussionComment(id=item.id, author=item.author, body=item.body, score=item.score, created_at=item.created_at, replies=build(item.id)) for item in rows if item.parent_comment_id == parent_id]
    return {'post': post, 'comments': build(None)}


@router.post('/posts/{post_id}/analyze', response_model=AnalysisOut)
def analyze_post(post_id: str, db: Session = Depends(get_db)):
    post = require(db, Post, post_id, 'Post')
    return analyze_discussion(post, list_comments(db, post_id))
