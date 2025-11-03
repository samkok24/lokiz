from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel

from app.core.deps import get_db, get_current_user_optional
from app.models.user import User
from app.models.video import Video
from app.models.social import Follow, Like, VideoGlitch
from app.schemas.user import UserProfileResponse
from app.schemas.video import VideoListResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get user profile by ID
    Public endpoint - no authentication required
    """
    # Get user
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get statistics
    follower_count = db.query(Follow).filter(Follow.following_id == user_id).count()
    following_count = db.query(Follow).filter(Follow.follower_id == user_id).count()
    video_count = db.query(Video).filter(
        Video.user_id == user_id,
        Video.status == "completed"
    ).count()

    # Get total likes (sum of like_count from all user's videos)
    total_likes = db.query(func.sum(Video.like_count)).filter(
        Video.user_id == user_id,
        Video.status == "completed"
    ).scalar() or 0

    # Build response
    return UserProfileResponse(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        bio=user.bio,
        profile_image_url=user.profile_image_url,
        follower_count=follower_count,
        following_count=following_count,
        video_count=video_count,
        total_likes=total_likes,
        created_at=user.created_at
    )


@router.get("/{user_id}/videos", response_model=VideoListResponse)
async def get_user_videos(
    user_id: UUID,
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get user's videos (infinite scroll)
    Public endpoint - shows only public/completed videos for non-owners
    Owner can see all their videos
    """
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Build query
    query = db.query(Video).filter(Video.user_id == user_id)

    # If not the owner, only show completed and public videos
    is_owner = current_user and current_user.id == user_id
    if not is_owner:
        query = query.filter(
            Video.status == "completed",
            Video.is_public.is_(True),
            Video.deleted_at.is_(None)
        )

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


@router.get("/{user_id}/liked-videos", response_model=VideoListResponse)
async def get_user_liked_videos(
    user_id: UUID,
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get videos liked by user (infinite scroll)
    Public endpoint - shows only public/completed videos
    """
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Build query - join Like and Video
    query = db.query(Video).join(
        Like,
        Like.video_id == Video.id
    ).filter(
        Like.user_id == user_id,
        Video.status == "completed",
        Video.is_public.is_(True),
        Video.deleted_at.is_(None)
    )

    # Apply cursor pagination (use Like.created_at for ordering)
    if cursor:
        # Cursor is Like.id in this case
        query = query.filter(Like.id < cursor)

    # Order by when the user liked it (most recent first)
    query = query.order_by(Like.created_at.desc())

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

    # Get next cursor (use last video's Like.id)
    next_cursor = None
    if has_more and videos:
        last_like = db.query(Like).filter(
            Like.user_id == user_id,
            Like.video_id == videos[-1].id
        ).first()
        if last_like:
            next_cursor = str(last_like.id)

    return VideoListResponse(
        videos=videos,
        total=len(videos),
        page=1,
        page_size=page_size,
        has_more=has_more,
        next_cursor=next_cursor
     )


class UserBatchInfoRequest(BaseModel):
    """Request to get info for multiple users"""
    user_ids: List[UUID]


@router.post("/batch-info")
async def get_users_batch_info(
    request: UserBatchInfoRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get detailed info for multiple users at once
    Includes profile, follower/following counts, video count, and follow status
    Maximum 100 users per request
    Public endpoint - authentication optional (follow status only if authenticated)
    """
    # Validate batch size
    if len(request.user_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 users per batch request"
        )

    if not request.user_ids:
        return {"users": {}}

    # Query all users
    users = db.query(User).filter(
        User.id.in_(request.user_ids)
    ).all()

    # Check follow status if authenticated
    following_set = set()
    if current_user:
        follows = db.query(Follow).filter(
            Follow.follower_id == current_user.id,
            Follow.following_id.in_(request.user_ids)
        ).all()
        following_set = {follow.following_id for follow in follows}

    # Build result dictionary
    result = {}
    for user in users:
        # Get follower count
        follower_count = db.query(Follow).filter(
            Follow.following_id == user.id
        ).count()

        # Get following count
        following_count = db.query(Follow).filter(
            Follow.follower_id == user.id
        ).count()

        # Get video count
        video_count = db.query(Video).filter(
            Video.user_id == user.id,
            Video.status == "completed",
            Video.deleted_at.is_(None)
        ).count()

        result[str(user.id)] = {
            "username": user.username,
            "display_name": user.display_name,
            "profile_image_url": user.profile_image_url,
            "bio": user.bio,
            "follower_count": follower_count,
            "following_count": following_count,
            "video_count": video_count,
            "is_following": user.id in following_set if current_user else False,
            "is_verified": False  # TODO: Add verification system
        }

    return {"users": result}
