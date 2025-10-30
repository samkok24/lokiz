from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List
from app.schemas.video import VideoResponse


class HashtagResponse(BaseModel):
    """Hashtag response"""
    id: UUID
    name: str
    use_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class HashtagVideoListResponse(BaseModel):
    """Hashtag video list response"""
    hashtag: HashtagResponse
    videos: List[VideoResponse]
    total: int


class TrendingHashtagsResponse(BaseModel):
    """Trending hashtags response"""
    hashtags: List[HashtagResponse]
    total: int
