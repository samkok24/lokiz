from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.schemas.user import UserBasicInfo


class VideoUploadRequest(BaseModel):
    """Request to get presigned upload URL"""
    file_type: str = Field(..., description="MIME type (e.g., 'video/mp4')")
    duration: Optional[float] = Field(None, description="Video duration in seconds")


class VideoUploadResponse(BaseModel):
    """Response with presigned upload URL"""
    upload_url: str
    file_key: str
    file_url: str
    video_id: UUID


class VideoCreateRequest(BaseModel):
    """Request to create video metadata after upload"""
    file_key: str
    file_url: str
    thumbnail_url: Optional[str] = None
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    caption: Optional[str] = None


class VideoResponse(BaseModel):
    """Video response"""
    id: UUID
    user: UserBasicInfo  # user_id 대신 user 객체
    video_url: str
    thumbnail_url: str
    duration_seconds: int
    caption: Optional[str]
    view_count: int
    like_count: int
    comment_count: int
    glitch_count: int  # 이 영상을 템플릿으로 사용한 글리치 개수
    original_video_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    """Video list response"""
    videos: list[VideoResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
    next_cursor: Optional[str] = None



class VideoUploadURLRequest(BaseModel):
    """Request to get presigned upload URL"""
    filename: str
    caption: Optional[str] = None
    duration_seconds: int


class VideoUploadURLResponse(BaseModel):
    """Response with presigned upload URLs"""
    video_id: UUID
    video_upload_url: str
    thumbnail_upload_url: str


class VideoUpdateRequest(BaseModel):
    """Request to update video metadata"""
    caption: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class VideoCompleteRequest(BaseModel):
    """Request to mark video upload as complete"""
    width: Optional[int] = None
    height: Optional[int] = None
    actual_duration: Optional[int] = None

