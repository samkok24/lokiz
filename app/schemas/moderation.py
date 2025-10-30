from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.schemas.user import UserBasicInfo


class BlockUserRequest(BaseModel):
    """Request to block a user"""
    blocked_user_id: UUID


class BlockResponse(BaseModel):
    """Block response"""
    id: UUID
    blocker_id: UUID
    blocked_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class BlockedUserResponse(BaseModel):
    """Blocked user with details"""
    id: UUID
    blocked_user: UserBasicInfo
    created_at: datetime


class BlockListResponse(BaseModel):
    """List of blocked users"""
    blocks: List[BlockedUserResponse]
    total: int


class ReportRequest(BaseModel):
    """Request to report content"""
    # One of these must be provided
    reported_user_id: Optional[UUID] = None
    reported_video_id: Optional[UUID] = None
    reported_comment_id: Optional[UUID] = None
    
    report_type: str = Field(..., pattern="^(spam|harassment|inappropriate|copyright|other)$")
    reason: Optional[str] = Field(None, max_length=500)


class ReportResponse(BaseModel):
    """Report response"""
    id: UUID
    reporter_id: UUID
    reported_user_id: Optional[UUID]
    reported_video_id: Optional[UUID]
    reported_comment_id: Optional[UUID]
    report_type: str
    reason: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    """List of reports"""
    reports: List[ReportResponse]
    total: int

