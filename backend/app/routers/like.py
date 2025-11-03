from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from pydantic import BaseModel

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.video import Video
from app.models.social import Like
from app.schemas.social import LikeResponse
from app.utils.notification_utils import create_notification

router = APIRouter(prefix="/likes", tags=["likes"])


@router.post("/videos/{video_id}", response_model=LikeResponse, status_code=status.HTTP_201_CREATED)
async def like_video(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Like a video
    """
    # Check if video exists
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    # Check if already liked
    existing_like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.video_id == video_id
    ).first()

    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already liked this video"
        )

    # Create like
    like = Like(
        user_id=current_user.id,
        video_id=video_id
    )
    db.add(like)

    # Increment like_count
    video.like_count += 1

    db.commit()
    db.refresh(like)

    # Create notification for video owner
    create_notification(
        db=db,
        user_id=video.user_id,
        notification_type="like",
        actor_id=current_user.id,
        target_id=video_id
    )

    return like


@router.delete("/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_video(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unlike a video
    """
    # Check if video exists
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    # Find like
    like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.video_id == video_id
    ).first()

    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found"
        )

    # Delete like
    db.delete(like)

    # Decrement like_count
    if video.like_count > 0:
        video.like_count -= 1

    db.commit()

    return None


@router.get("/videos/{video_id}/check")
async def check_if_liked(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if current user liked a video
    """
    like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.video_id == video_id
    ).first()

    return {"liked": like is not None}


class LikeBatchCheckRequest(BaseModel):
    """Request to check like status for multiple videos"""
    video_ids: List[UUID]


@router.post("/check-batch")
async def check_likes_batch(
    request: LikeBatchCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if current user liked multiple videos at once
    Maximum 100 videos per request
    """
    # Validate batch size
    if len(request.video_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 videos per batch request"
        )

    if not request.video_ids:
        return {"liked_videos": {}}

    # Query all likes for the user in one go
    likes = db.query(Like.video_id).filter(
        Like.user_id == current_user.id,
        Like.video_id.in_(request.video_ids)
    ).all()

    # Create a set of liked video IDs for O(1) lookup
    liked_video_ids = {str(like.video_id) for like in likes}

    # Build result dictionary
    result = {
        str(video_id): str(video_id) in liked_video_ids
        for video_id in request.video_ids
    }

    return {"liked_videos": result}
