from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.schemas.video import VideoResponse


class VideoGlitchResponse(BaseModel):
    """Video glitch relationship response"""
    id: UUID
    original_video_id: UUID
    glitch_video_id: UUID
    glitch_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class GlitchChainResponse(BaseModel):
    """Glitch chain response with full video details"""
    original_video_id: UUID
    glitch_count: int
    glitches: List[VideoResponse]  # Full video response with thumbnails and stats


class GlitchSourceResponse(BaseModel):
    """Glitch source response"""
    glitch_video_id: UUID
    original_video_id: Optional[UUID]
    original_video: Optional[dict]
    glitch_type: Optional[str]
