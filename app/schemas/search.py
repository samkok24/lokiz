from pydantic import BaseModel
from typing import List
from app.schemas.user import UserBasicInfo
from app.schemas.video import VideoResponse


class UserSearchResult(BaseModel):
    """User search result"""
    users: List[UserBasicInfo]
    total: int


class VideoSearchResult(BaseModel):
    """Video search result"""
    videos: List[VideoResponse]
    total: int


class UnifiedSearchResult(BaseModel):
    """Unified search result"""
    users: List[UserBasicInfo]
    videos: List[VideoResponse]
    user_count: int
    video_count: int
