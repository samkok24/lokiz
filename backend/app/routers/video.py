from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel

from app.core.deps import get_db, get_current_user, get_current_user_optional
from app.models.user import User
from app.models.video import Video
from app.models.social import VideoGlitch
from app.schemas.video import (
    VideoUploadURLRequest,
    VideoUploadURLResponse,
    VideoUpdateRequest,
    VideoCompleteRequest,
    VideoResponse,
    VideoListResponse
)
from app.services.mock_s3_service import get_mock_s3_service
from app.utils.hashtag_utils import update_video_hashtags

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/upload-url", response_model=VideoUploadURLResponse)
async def get_upload_url(
    request: VideoUploadURLRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get presigned URL for video upload
    """
    s3_service = get_mock_s3_service()

    # Generate presigned URL for video
    video_key = f"videos/{current_user.id}/{request.filename}"
    video_upload_url = s3_service.generate_presigned_url(video_key)

    # Generate presigned URL for thumbnail
    thumbnail_key = f"thumbnails/{current_user.id}/{request.filename}.jpg"
    thumbnail_upload_url = s3_service.generate_presigned_url(thumbnail_key)

    # Create video record
    video = Video(
        user_id=current_user.id,
        caption=request.caption or "",
        video_url=f"https://mock-s3.lokiz.com/{video_key}",
        thumbnail_url=f"https://mock-s3.lokiz.com/{thumbnail_key}",
        duration_seconds=request.duration_seconds,
        status="processing"
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    # Update hashtags if caption exists
    if request.caption:
        update_video_hashtags(db, video, request.caption)

    return VideoUploadURLResponse(
        video_id=video.id,
        video_upload_url=video_upload_url,
        thumbnail_upload_url=thumbnail_upload_url
    )


@router.patch("/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: UUID,
    request: VideoUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update video metadata
    """
    video = db.query(Video).filter(
        Video.id == video_id,
        Video.user_id == current_user.id
    ).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found or you don't have permission"
        )

    if request.width:
        video.width = request.width
    if request.height:
        video.height = request.height
    if request.caption is not None:  # Allow empty string
        video.caption = request.caption
        # Update hashtags
        update_video_hashtags(db, video, request.caption)

    db.commit()
    db.refresh(video)

    # Add glitch_count
    video.glitch_count = db.query(VideoGlitch).filter(
        VideoGlitch.original_video_id == video.id
    ).count()

    return video


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get video by ID
    """
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    # Add glitch_count
    video.glitch_count = db.query(VideoGlitch).filter(
        VideoGlitch.original_video_id == video.id
    ).count()

    return video


@router.post("/{video_id}/complete", response_model=VideoResponse)
async def complete_video_upload(
    video_id: UUID,
    request: VideoCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark video upload as complete and update metadata
    Called by frontend after successful upload to S3
    """
    video = db.query(Video).filter(
        Video.id == video_id,
        Video.user_id == current_user.id
    ).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found or you don't have permission"
        )

    # Update status to completed
    video.status = "completed"

    # Update metadata if provided
    if request.width:
        video.width = request.width
    if request.height:
        video.height = request.height
    if request.actual_duration:
        video.duration_seconds = request.actual_duration

    db.commit()
    db.refresh(video)

    # Add glitch_count
    video.glitch_count = db.query(VideoGlitch).filter(
        VideoGlitch.original_video_id == video.id
    ).count()

    return video


@router.post("/{video_id}/view")
async def increment_view_count(
    video_id: UUID,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Increment view count for a video
    Public endpoint - no authentication required
    Does not increment if viewing own video
    """
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    # Don't increment if user is viewing their own video
    if current_user and current_user.id == video.user_id:
        return {"success": True, "message": "Own video - view not counted"}

    # Increment view count
    video.view_count += 1
    db.commit()

    return {"success": True, "view_count": video.view_count}


class VideoBatchMetadataRequest(BaseModel):
    """Request to get metadata for multiple videos"""
    video_ids: List[UUID]


@router.post("/batch-metadata")
async def get_videos_batch_metadata(
    request: VideoBatchMetadataRequest,
    db: Session = Depends(get_db)
):
    """
    Get metadata (view_count, like_count, etc.) for multiple videos at once
    Maximum 100 videos per request
    Public endpoint - no authentication required
    Used for real-time stats updates in feed
    """
    # Validate batch size
    if len(request.video_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 videos per batch request"
        )

    if not request.video_ids:
        return {"videos": {}}

    # Query all videos in one go
    videos = db.query(Video).filter(
        Video.id.in_(request.video_ids),
        Video.deleted_at.is_(None)
    ).all()

    # Build result dictionary
    result = {
        str(video.id): {
            "view_count": video.view_count,
            "like_count": video.like_count,
            "comment_count": video.comment_count,
            "glitch_count": db.query(VideoGlitch).filter(
                VideoGlitch.original_video_id == video.id
            ).count()
        }
        for video in videos
    }

    # Add missing videos as not found
    for video_id in request.video_ids:
        if str(video_id) not in result:
            result[str(video_id)] = {
                "view_count": 0,
                "like_count": 0,
                "comment_count": 0,

                "glitch_count": 0
            }

    return {"videos": result}


@router.get("/me", response_model=VideoListResponse)
async def get_my_videos(
    status: Optional[str] = Query(None, regex="^(processing|completed|failed)$"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's videos
    """
    query = db.query(Video).filter(Video.user_id == current_user.id)

    # Filter by status if provided
    if status:
        query = query.filter(Video.status == status)

    # Apply cursor pagination
    if cursor:
        query = query.filter(Video.id < cursor)

    # Get videos
    videos = query.order_by(Video.created_at.desc()).limit(page_size + 1).all()

    # Check if there are more videos
    has_more = len(videos) > page_size
    if has_more:
        videos = videos[:page_size]

    # Add glitch_count to each video
    for video in videos:
        video.glitch_count = db.query(VideoGlitch).filter(
            VideoGlitch.original_video_id == video.id
        ).count()

    # Get next cursor
    next_cursor = str(videos[-1].id) if has_more and videos else None

    return VideoListResponse(
        videos=videos,
        total=len(videos),
        page=1,
        page_size=page_size,
        has_more=has_more,
        next_cursor=next_cursor
    )


@router.get("/", response_model=VideoListResponse)
async def get_videos(
    status: Optional[str] = Query(None, regex="^(processing|completed|failed)$"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    db: Session = Depends(get_db)
):
    """
    Get public videos (feed)
    """
    # Only show completed videos in feed
    query = db.query(Video).filter(Video.status == "completed")

    # Apply cursor pagination
    if cursor:
        query = query.filter(Video.id < cursor)

    # Get videos
    videos = query.order_by(Video.created_at.desc()).limit(page_size + 1).all()

    # Check if there are more videos
    has_more = len(videos) > page_size
    if has_more:
        videos = videos[:page_size]

    # Add glitch_count to each video
    for video in videos:
        video.glitch_count = db.query(VideoGlitch).filter(
            VideoGlitch.original_video_id == video.id
        ).count()

    # Get next cursor
    next_cursor = str(videos[-1].id) if has_more and videos else None

    return VideoListResponse(
        videos=videos,
        total=len(videos),
        page=1,
        page_size=page_size,
        has_more=has_more,
        next_cursor=next_cursor
    )


@router.delete("/{video_id}")
async def delete_video(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete video (mark as deleted)
    """
    video = db.query(Video).filter(
        Video.id == video_id,
        Video.user_id == current_user.id
    ).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found or you don't have permission"
        )

    # Check glitch count
    glitch_count = db.query(VideoGlitch).filter(
        VideoGlitch.original_video_id == video_id
    ).count()

    # Soft delete (mark as private and set deleted_at)
    from datetime import datetime, timezone
    video.is_public = False
    video.deleted_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "message": "Video marked as deleted",
        "glitch_count": glitch_count,
        "deleted_at": video.deleted_at.isoformat()
    }
