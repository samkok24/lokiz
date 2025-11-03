from pydantic import BaseModel
from typing import List, Optional
from app.schemas.video import VideoResponse


class FeedResponse(BaseModel):
    """Feed response with videos"""
    videos: List[VideoResponse]
    total: int
    page_size: int
    has_more: bool
    next_cursor: Optional[str]
    feed_type: str  # 'for_you' or 'following'

