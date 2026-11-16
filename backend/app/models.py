from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    avatar: Mapped[str] = mapped_column(String(16))
    karma: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    posts: Mapped[list['Post']] = relationship(back_populates='author')
    comments: Mapped[list['Comment']] = relationship(back_populates='author')


class Community(Base):
    __tablename__ = 'communities'
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    member_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    posts: Mapped[list['Post']] = relationship(back_populates='community')


class Post(Base):
    __tablename__ = 'posts'
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    community_id: Mapped[str] = mapped_column(ForeignKey('communities.id'), index=True)
    author_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    title: Mapped[str] = mapped_column(String(300))
    body: Mapped[str] = mapped_column(Text, default='')
    score: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    flair: Mapped[str | None] = mapped_column(String(60), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author: Mapped[User] = relationship(back_populates='posts')
    community: Mapped[Community] = relationship(back_populates='posts')
    comments: Mapped[list['Comment']] = relationship(back_populates='post', cascade='all, delete-orphan')


class Comment(Base):
    __tablename__ = 'comments'
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    post_id: Mapped[str] = mapped_column(ForeignKey('posts.id'), index=True)
    author_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    parent_comment_id: Mapped[str | None] = mapped_column(ForeignKey('comments.id'), nullable=True, index=True)
    body: Mapped[str] = mapped_column(Text)
    score: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    post: Mapped[Post] = relationship(back_populates='comments')
    author: Mapped[User] = relationship(back_populates='comments')
    parent: Mapped['Comment | None'] = relationship(remote_side='Comment.id', back_populates='replies')
    replies: Mapped[list['Comment']] = relationship(back_populates='parent', cascade='all, delete-orphan')


class Vote(Base):
    __tablename__ = 'votes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    post_id: Mapped[str | None] = mapped_column(ForeignKey('posts.id'), nullable=True, index=True)
    comment_id: Mapped[str | None] = mapped_column(ForeignKey('comments.id'), nullable=True, index=True)
    value: Mapped[int] = mapped_column(Integer)
