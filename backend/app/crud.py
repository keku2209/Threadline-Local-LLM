from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session, joinedload

from .models import Comment, Community, Post, User, Vote


def get_or_404(db: Session, model, object_id: str):
    item = db.get(model, object_id)
    if item is None:
        return None
    return item


def list_posts(db: Session, community_id: str | None = None) -> list[Post]:
    statement = select(Post).options(joinedload(Post.author), joinedload(Post.community)).order_by(Post.created_at.desc())
    if community_id:
        statement = statement.where(Post.community_id == community_id)
    return list(db.scalars(statement).unique())


def list_comments(db: Session, post_id: str) -> list[Comment]:
    statement = select(Comment).options(joinedload(Comment.author)).where(Comment.post_id == post_id).order_by(Comment.created_at.asc())
    return list(db.scalars(statement).unique())


def apply_vote(db: Session, *, user_id: str, value: int, post_id: str | None = None, comment_id: str | None = None) -> int:
    statement = select(Vote).where(Vote.user_id == user_id)
    statement = statement.where(Vote.post_id == post_id) if post_id else statement.where(Vote.comment_id == comment_id)
    vote = db.scalar(statement)
    target = db.get(Post if post_id else Comment, post_id or comment_id)
    if target is None:
        return 0
    old_value = vote.value if vote else 0
    if value == 0:
        if vote:
            db.delete(vote)
    elif vote:
        vote.value = value
    else:
        vote = Vote(user_id=user_id, value=value, post_id=post_id, comment_id=comment_id)
        db.add(vote)
    target.score += value - old_value
    db.commit()
    return target.score


def search(db: Session, query: str) -> tuple[list[Post], list[Community]]:
    pattern = f'%{query.strip()}%'
    posts = list(db.scalars(select(Post).options(joinedload(Post.author), joinedload(Post.community)).where(or_(Post.title.ilike(pattern), Post.body.ilike(pattern))).order_by(Post.created_at.desc())).unique())
    communities = list(db.scalars(select(Community).where(or_(Community.name.ilike(pattern), Community.display_name.ilike(pattern), Community.description.ilike(pattern))).order_by(Community.member_count.desc())))
    return posts, communities
