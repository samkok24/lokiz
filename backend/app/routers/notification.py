from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from pydantic import BaseModel

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import (
    NotificationListResponse,
    UnreadCountResponse
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's notifications
    Requires authentication
    """
    # Get total count
    total = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).count()

    # Get unread count
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read.is_(False)
    ).count()

    # Get notifications
    offset = (page - 1) * page_size
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(
        Notification.created_at.desc()
    ).offset(offset).limit(page_size).all()

    return NotificationListResponse(
        notifications=notifications,
        total=total,
        unread_count=unread_count,
        page=page,
        page_size=page_size
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get unread notification count
    Requires authentication
    """
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read.is_(False)
    ).count()

    return UnreadCountResponse(unread_count=unread_count)


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark notification as read
    Requires authentication
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    notification.is_read = True
    db.commit()

    return {"message": "Notification marked as read"}


@router.patch("/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark all notifications as read
    Requires authentication
    """
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read.is_(False)
    ).update({"is_read": True})

    db.commit()

    return {"message": "All notifications marked as read"}


class NotificationBatchMarkReadRequest(BaseModel):
    """Request to mark multiple notifications as read"""
    notification_ids: List[UUID]


@router.post("/batch-mark-read")
async def mark_notifications_batch_read(
    request: NotificationBatchMarkReadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark multiple notifications as read at once
    Maximum 100 notifications per request
    Requires authentication
    """
    # Validate batch size
    if len(request.notification_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 notifications per batch request"
        )

    if not request.notification_ids:
        return {"marked_count": 0, "success": True}

    # Update notifications
    marked_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.id.in_(request.notification_ids),
        Notification.is_read.is_(False)
    ).update({"is_read": True}, synchronize_session=False)

    db.commit()

    return {"marked_count": marked_count, "success": True}
