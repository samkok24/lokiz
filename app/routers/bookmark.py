from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.video import Video
from app.models.social import Bookmark, VideoGlitch
from app.schemas.video import VideoListResponse

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


@router.post("/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def bookmark_video(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bookmark (save) a video
    """
    # Check if video exists
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    # Check if already bookmarked
    existing_bookmark = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.video_id == video_id
    ).first()

    if existing_bookmark:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video already bookmarked"
        )

    # Create bookmark
    bookmark = Bookmark(
        user_id=current_user.id,
        video_id=video_id
    )
    db.add(bookmark)
    db.commit()

    return None


@router.delete("/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unbookmark_video(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove bookmark from a video
    """
    # Find bookmark
    bookmark = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.video_id == video_id
    ).first()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not bookmarked"
        )

    # Delete bookmark
    db.delete(bookmark)
    db.commit()

    return None


@router.get("/videos/{video_id}/check")
async def check_bookmark(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if current user has bookmarked a video
    """
    bookmark = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.video_id == video_id
    ).first()

    return {"is_bookmarked": bookmark is not None}


@router.get("/", response_model=VideoListResponse)
async def get_bookmarked_videos(
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get bookmarked videos for current user (infinite scroll)
    Only shows public/completed videos
    """
    # Build query - join Bookmark and Video
    query = db.query(Video).join(
        Bookmark,
        Bookmark.video_id == Video.id
    ).filter(
        Bookmark.user_id == current_user.id,
        Video.status == "completed",
        Video.is_public.is_(True),
        Video.deleted_at.is_(None)
    )

    # Apply cursor pagination (use Bookmark.created_at for ordering)
    if cursor:
        # Cursor is Bookmark.id in this case
        query = query.filter(Bookmark.id < cursor)

    # Order by when the user bookmarked it (most recent first)
    query = query.order_by(Bookmark.created_at.desc())

    # Get videos
    videos = query.limit(page_size + 1).all()

    # Check if there are more videos
    has_more = len(videos) > page_size
    if has_more:
        videos = videos[:page_size]

    # Add glitch_count to each video
    for video in videos:
        video.glitch_count = db.query(VideoGlitch).filter(
            VideoGlitch.original_video_id == video.id
        ).count()

    # Get next cursor (use last video's Bookmark.id)
    next_cursor = None
    if has_more and videos:
        last_bookmark = db.query(Bookmark).filter(
            Bookmark.user_id == current_user.id,
            Bookmark.video_id == videos[-1].id
        ).first()
        if last_bookmark:
            next_cursor = str(last_bookmark.id)

    return VideoListResponse(
        videos=videos,
        total=len(videos),
        page=1,
        page_size=page_size,
        has_more=has_more,
        next_cursor=next_cursor
    )
