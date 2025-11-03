from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from pydantic import BaseModel

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.social import Follow
from app.schemas.social import FollowResponse, FollowListResponse
from app.utils.notification_utils import create_notification

router = APIRouter(prefix="/follows", tags=["follows"])


@router.post("/users/{user_id}", response_model=FollowResponse, status_code=status.HTTP_201_CREATED)
async def follow_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Follow a user
    """
    # Cannot follow yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself"
        )

    # Check if user exists
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if already following
    existing_follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).first()

    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this user"
        )

    # Create follow
    follow = Follow(
        follower_id=current_user.id,
        following_id=user_id
    )
    db.add(follow)
    db.commit()
    db.refresh(follow)

    # Create notification for followed user
    create_notification(
        db=db,
        user_id=user_id,
        notification_type="follow",
        actor_id=current_user.id,
        target_id=None
    )

    return follow


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unfollow a user
    """
    # Find follow
    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).first()

    if not follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not following this user"
        )

    # Delete follow
    db.delete(follow)
    db.commit()

    return None


@router.get("/users/{user_id}/followers", response_model=FollowListResponse)
async def get_user_followers(
    user_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get followers of a user
    """
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get total count
    total = db.query(Follow).filter(Follow.following_id == user_id).count()

    # Get followers
    offset = (page - 1) * page_size
    follows = db.query(Follow).filter(
        Follow.following_id == user_id
    ).order_by(
        Follow.created_at.desc()
    ).offset(offset).limit(page_size).all()

    return FollowListResponse(
        follows=follows,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/users/{user_id}/following", response_model=FollowListResponse)
async def get_user_following(
    user_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get users that a user is following
    """
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get total count
    total = db.query(Follow).filter(Follow.follower_id == user_id).count()

    # Get following
    offset = (page - 1) * page_size
    follows = db.query(Follow).filter(
        Follow.follower_id == user_id
    ).order_by(
        Follow.created_at.desc()
    ).offset(offset).limit(page_size).all()

    return FollowListResponse(
        follows=follows,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/users/{user_id}/check")
async def check_if_following(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if current user is following a user
    """
    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).first()

    return {"following": follow is not None}


class FollowBatchCheckRequest(BaseModel):
    """Request to check follow status for multiple users"""
    user_ids: List[UUID]


@router.post("/check-batch")
async def check_follows_batch(
    request: FollowBatchCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if current user is following multiple users at once
    Maximum 100 users per request
    """
    # Validate batch size
    if len(request.user_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 users per batch request"
        )

    if not request.user_ids:
        return {"following_users": {}}

    # Query all follows for the user in one go
    follows = db.query(Follow.following_id).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id.in_(request.user_ids)
    ).all()

    # Create a set of following user IDs for O(1) lookup
    following_user_ids = {str(follow.following_id) for follow in follows}

    # Build result dictionary
    result = {
        str(user_id): str(user_id) in following_user_ids
        for user_id in request.user_ids
    }

    return {"following_users": result}
