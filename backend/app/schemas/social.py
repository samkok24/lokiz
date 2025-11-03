from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.schemas.user import UserBasicInfo


# Like Schemas
class LikeResponse(BaseModel):
    """Like response"""
    id: UUID
    user_id: UUID
    video_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Comment Schemas
class CommentCreateRequest(BaseModel):
    """Comment creation request"""
    content: str


class CommentUpdateRequest(BaseModel):
    """Comment update request"""
    content: str


class CommentResponse(BaseModel):
    """Comment response"""
    id: UUID
    user: UserBasicInfo  # user_id 대신
    video_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    """Comment list response"""
    comments: list[CommentResponse]
    total: int
    page: int
    page_size: int


# Follow Schemas
class FollowResponse(BaseModel):
    """Follow response"""
    id: UUID
    follower: UserBasicInfo  # follower_id 대신
    following: UserBasicInfo  # following_id 대신
    created_at: datetime

    class Config:
        from_attributes = True


class FollowListResponse(BaseModel):
    """Follow list response"""
    follows: list[FollowResponse]
    total: int
    page: int
    page_size: int
