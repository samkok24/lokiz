from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.deps import get_db, get_current_user_optional
from app.models.user import User
from app.models.video import Video
from app.models.social import VideoGlitch
from app.schemas.search import UserSearchResult, VideoSearchResult, UnifiedSearchResult

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/users", response_model=UserSearchResult)
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search users by username or display_name
    Public endpoint - no authentication required
    """
    # Search by username or display_name (case-insensitive)
    users = db.query(User).filter(
        (User.username.ilike(f"%{q}%")) |
        (User.display_name.ilike(f"%{q}%"))
    ).limit(limit).all()

    total = db.query(User).filter(
        (User.username.ilike(f"%{q}%")) |
        (User.display_name.ilike(f"%{q}%"))
    ).count()

    return UserSearchResult(users=users, total=total)


@router.get("/videos", response_model=VideoSearchResult)
async def search_videos(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Search videos by caption
    Public endpoint - no authentication required
    Only returns completed and public videos
    """
    # Search by caption (case-insensitive)
    # Only show completed videos
    query = db.query(Video).filter(
        Video.caption.ilike(f"%{q}%"),
        Video.status == "completed"
    )

    # If user is not logged in, only show public videos
    if not current_user:
        query = query.filter(Video.is_public.is_(True))

    videos = query.limit(limit).all()

    # Add glitch_count to each video
    for video in videos:
        video.glitch_count = db.query(VideoGlitch).filter(
            VideoGlitch.original_video_id == video.id
        ).count()

    total = db.query(Video).filter(
        Video.caption.ilike(f"%{q}%"),
        Video.status == "completed"
    ).count()

    return VideoSearchResult(videos=videos, total=total)


@router.get("/", response_model=UnifiedSearchResult)
async def unified_search(
    q: str = Query(..., min_length=1, description="Search query"),
    user_limit: int = Query(5, ge=1, le=20),
    video_limit: int = Query(10, ge=1, le=50),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Unified search across users and videos
    Public endpoint - no authentication required
    """
    # Search users
    users = db.query(User).filter(
        (User.username.ilike(f"%{q}%")) |
        (User.display_name.ilike(f"%{q}%"))
    ).limit(user_limit).all()

    user_count = db.query(User).filter(
        (User.username.ilike(f"%{q}%")) |
        (User.display_name.ilike(f"%{q}%"))
    ).count()

    # Search videos
    video_query = db.query(Video).filter(
        Video.caption.ilike(f"%{q}%"),
        Video.status == "completed"
    )

    # If user is not logged in, only show public videos
    if not current_user:
        video_query = video_query.filter(Video.is_public.is_(True))

    videos = video_query.limit(video_limit).all()

    # Add glitch_count to each video
    for video in videos:
        video.glitch_count = db.query(VideoGlitch).filter(
            VideoGlitch.original_video_id == video.id
        ).count()

    video_count = db.query(Video).filter(
        Video.caption.ilike(f"%{q}%"),
        Video.status == "completed"
    ).count()

    return UnifiedSearchResult(
        users=users,
        videos=videos,
        user_count=user_count,
        video_count=video_count
    )
