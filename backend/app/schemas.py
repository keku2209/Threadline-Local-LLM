from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    username: str
    display_name: str
    avatar: str
    karma: int
    created_at: datetime


class CommunityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    display_name: str
    description: str
    member_count: int
    created_at: datetime


class PostCreate(BaseModel):
    community_id: str
    author_id: str
    title: str = Field(min_length=1, max_length=300)
    body: str = ''
    flair: str | None = Field(default=None, max_length=60)
    image_url: str | None = None


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    community_id: str
    author_id: str
    title: str
    body: str
    score: int
    comment_count: int
    flair: str | None
    image_url: str | None
    created_at: datetime
    updated_at: datetime
    author: UserOut
    community: CommunityOut


class CommentCreate(BaseModel):
    author_id: str
    body: str = Field(min_length=1, max_length=10000)
    parent_comment_id: str | None = None


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    post_id: str
    author_id: str
    parent_comment_id: str | None
    body: str
    score: int
    created_at: datetime
    updated_at: datetime
    author: UserOut


class VoteRequest(BaseModel):
    user_id: str
    value: int = Field(ge=-1, le=1)


class DiscussionComment(BaseModel):
    id: str
    author: UserOut
    body: str
    score: int
    created_at: datetime
    replies: list['DiscussionComment'] = []


class DiscussionOut(BaseModel):
    post: PostOut
    comments: list[DiscussionComment]


class SearchOut(BaseModel):
    posts: list[PostOut]
    communities: list[CommunityOut]


class SentimentCounts(BaseModel):
    positive: int
    negative: int
    neutral: int


class Viewpoint(BaseModel):
    name: str
    description: str
    comment_ids: list[str]
    sentiment_summary: str


class Argument(BaseModel):
    text: str
    comment_id: str
    supporting_ids: list[str] = []


class ImportantComment(BaseModel):
    comment_id: str
    reason: str


class DiscussionQuality(BaseModel):
    agreement_level: float
    disagreement_level: float
    polarization: float
    substantive_discussion: float


class AnalysisOut(BaseModel):
    post_id: str
    summary: str
    overall_sentiment: str
    sentiment_counts: SentimentCounts
    sentiment_percentages: dict[str, float]
    themes: list[str]
    viewpoints: list[Viewpoint]
    consensus: str
    disagreements: list[str]
    arguments_for: list[Argument]
    arguments_against: list[Argument]
    important_comments: list[ImportantComment]
    discussion_quality: DiscussionQuality
    comments_analyzed: int
    ai_provider: str
