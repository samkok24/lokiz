from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.video import Video

router = APIRouter(prefix="/studio", tags=["studio"])


@router.get("/videos/{video_id}/timeline")
async def get_video_timeline(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get video timeline information for studio editing
    Returns video metadata and duration for timeline scrubbing
    Public videos can be viewed by anyone (for glitch workflow)
    """
    # Get video
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Check access permission (private videos only accessible by owner)
    if video.status == "private" and video.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to private video")

    return {
        "video_id": str(video.id),
        "title": video.title,
        "url": video.video_url,
        "duration": video.duration_seconds,
        "status": video.status,
        "created_at": video.created_at.isoformat(),
        "timeline": {
            "total_duration": video.duration_seconds,
            "frame_rate": 30,
            "total_frames": int(video.duration_seconds * 30) if video.duration_seconds else 0
        }
    }


@router.get("/videos/{video_id}/preview")
async def get_video_preview(
    video_id: UUID,
    timestamp: Optional[float] = 0.0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get video preview at specific timestamp
    Used for timeline scrubbing and frame selection
    Public videos can be previewed by anyone (for glitch workflow)
    """
    # Get video
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Check access permission (private videos only accessible by owner)
    if video.status == "private" and video.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to private video")

    # Validate timestamp
    if video.duration_seconds and timestamp > video.duration_seconds:
        raise HTTPException(
            status_code=400,
            detail=f"Timestamp {timestamp}s exceeds video duration {video.duration_seconds}s"
        )

    return {
        "video_id": str(video.id),
        "url": video.video_url,
        "timestamp": timestamp,
        "duration": video.duration_seconds,
        "preview_url": f"{video.video_url}#t={timestamp}"
    }


@router.post("/videos/{video_id}/select-range")
async def select_video_range(
    video_id: UUID,
    start_time: float,
    end_time: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Select a time range from video for editing
    Used for selecting 10-second clips for AI processing
    Public videos can be selected by anyone (for glitch workflow)
    """
    # Get video
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Check access permission (private videos only accessible by owner)
    if video.status == "private" and video.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to private video")

    # Validate range
    if start_time < 0 or end_time < 0:
        raise HTTPException(status_code=400, detail="Time values must be positive")

    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="Start time must be before end time")

    if video.duration_seconds and end_time > video.duration_seconds:
        raise HTTPException(
            status_code=400,
            detail=f"End time {end_time}s exceeds video duration {video.duration_seconds}s"
        )

    duration = end_time - start_time

    # Check if range is within limits (10 seconds for most AI operations)
    if duration > 10:
        raise HTTPException(
            status_code=400,
            detail=f"AI 처리는 최대 10초까지 가능합니다. 현재 선택: {duration:.1f}초"
        )

    return {
        "video_id": str(video.id),
        "start_time": start_time,
        "end_time": end_time,
        "duration": duration,
        "url": video.video_url,
        "range_url": f"{video.video_url}#t={start_time},{end_time}"
    }
