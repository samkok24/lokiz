from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from pydantic import BaseModel

from app.core.deps import get_db, get_current_user_optional
from app.models.user import User
from app.models.video import Video
from app.models.social import VideoShare

router = APIRouter(prefix="/shares", tags=["shares"])


class VideoShareRequest(BaseModel):
    """Request to share a video"""
    share_platform: Optional[str] = None  # 'twitter', 'facebook', 'copy_link', etc.


@router.post("/videos/{video_id}", status_code=status.HTTP_201_CREATED)
async def share_video(
    video_id: UUID,
    request: VideoShareRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Share a video
    Authentication is optional (anonymous shares are allowed)
    """
    # Check if video exists
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    # Create share record if user is authenticated
    if current_user:
        share = VideoShare(
            user_id=current_user.id,
            video_id=video_id,
            share_platform=request.share_platform
        )
        db.add(share)

    # Increment share_count
    video.share_count += 1

    db.commit()

    return {
        "success": True,
        "share_count": video.share_count
    }


@router.get("/videos/{video_id}/count")
async def get_video_share_count(
    video_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get share count for a video
    Public endpoint - no authentication required
    """
    # Check if video exists
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    return {
        "video_id": str(video_id),
        "share_count": video.share_count
    }
