from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.schemas.user import UserBasicInfo


class NotificationResponse(BaseModel):
    """Notification response"""
    id: UUID
    type: str  # like, comment, follow, glitch
    actor: UserBasicInfo  # Who triggered the notification
    target_id: Optional[UUID]  # video_id, comment_id, etc.
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Notification list response"""
    notifications: list[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int


class UnreadCountResponse(BaseModel):
    """Unread notification count"""
    unread_count: int

