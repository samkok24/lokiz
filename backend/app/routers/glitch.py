from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.video import Video
from app.models.social import VideoGlitch, Like
from app.schemas.glitch import GlitchChainResponse, GlitchSourceResponse
from app.schemas.user import UserBasicInfo

router = APIRouter(prefix="/glitch", tags=["glitch"])


@router.get("/videos/{video_id}/glitches", response_model=GlitchChainResponse)
async def get_video_glitches(
    video_id: UUID,
    sort: str = Query("latest", regex="^(latest|popular)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all glitches created from this video
    Shows the glitch chain - who glitched this video
    Requires authentication
    Sort options: latest (default), popular (by like_count)
    """
    # Verify video exists
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Check access permission (private videos only accessible by owner)
    if video.status == "private" and video.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to private video")

    # Get all glitches created from this video
    query = db.query(VideoGlitch).filter(
        VideoGlitch.original_video_id == video_id
    )

    # Apply sorting
    if sort == "latest":
        query = query.order_by(VideoGlitch.created_at.desc())
    elif sort == "popular":
        # Join with Video to sort by like_count
        query = query.join(Video, VideoGlitch.glitch_video_id == Video.id).order_by(Video.like_count.desc())

    glitches = query.all()

    # Build glitch list with full video details (like TikTok grid view)
    glitch_videos = []
    for glitch in glitches:
        glitch_video = db.query(Video).filter(Video.id == glitch.glitch_video_id).first()
        if glitch_video:
            # Only include public glitches or user's own glitches
            if glitch_video.status != "private" or glitch_video.user_id == current_user.id:
                # Get user info
                user = db.query(User).filter(User.id == glitch_video.user_id).first()
                
                # Check if current user liked this video
                user_liked = db.query(Like).filter(
                    Like.user_id == current_user.id,
                    Like.video_id == glitch_video.id
                ).first() is not None
                
                # Get glitch count for this video
                video_glitch_count = db.query(VideoGlitch).filter(
                    VideoGlitch.original_video_id == glitch_video.id
                ).count()
                
                # Build VideoResponse
                glitch_videos.append({
                    "id": glitch_video.id,
                    "user": UserBasicInfo(
                        id=user.id,
                        username=user.username,
                        profile_image=user.profile_image
                    ),
                    "video_url": glitch_video.video_url,
                    "thumbnail_url": glitch_video.thumbnail_url,
                    "duration_seconds": glitch_video.duration_seconds,
                    "caption": glitch_video.caption,
                    "view_count": glitch_video.view_count,
                    "like_count": glitch_video.like_count,
                    "comment_count": glitch_video.comment_count,
                    "glitch_count": video_glitch_count,
                    "original_video_id": glitch.original_video_id,
                    "created_at": glitch_video.created_at
                })

    return GlitchChainResponse(
        original_video_id=video_id,
        glitch_count=len(glitch_videos),
        glitches=glitch_videos
    )


@router.get("/videos/{video_id}/source", response_model=GlitchSourceResponse)
async def get_glitch_source(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the original video that this glitch was created from
    Shows where this video came from
    Requires authentication
    """
    # Verify video exists
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Check access permission (private videos only accessible by owner)
    if video.status == "private" and video.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to private video")

    # Check if this video is a glitch
    glitch = db.query(VideoGlitch).filter(
        VideoGlitch.glitch_video_id == video_id
    ).first()

    if not glitch:
        # This video is not a glitch
        return GlitchSourceResponse(
            glitch_video_id=video_id,
            original_video_id=None,
            original_video=None,
            glitch_type=None
        )

    # Get original video info
    original_video = db.query(Video).filter(Video.id == glitch.original_video_id).first()

    # Check if user can access original video
    if original_video and original_video.status == "private" and original_video.user_id != current_user.id:
        # Original video is private and user is not the owner
        return GlitchSourceResponse(
            glitch_video_id=video_id,
            original_video_id=glitch.original_video_id,
            original_video=None,  # Don't expose private video details
            glitch_type=glitch.glitch_type
        )

    return GlitchSourceResponse(
        glitch_video_id=video_id,
        original_video_id=glitch.original_video_id,
        original_video={
            "id": str(original_video.id),
            "title": original_video.title,
            "url": original_video.video_url,
            "user_id": str(original_video.user_id),
            "created_at": original_video.created_at.isoformat()
        } if original_video else None,
        glitch_type=glitch.glitch_type
    )
