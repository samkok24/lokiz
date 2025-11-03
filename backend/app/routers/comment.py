from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from pydantic import BaseModel

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.video import Video
from app.models.social import Comment, CommentLike
from app.schemas.social import (
    CommentCreateRequest,
    CommentUpdateRequest,
    CommentResponse,
    CommentListResponse
)
from app.utils.notification_utils import create_notification

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/videos/{video_id}", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    video_id: UUID,
    request: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a comment on a video
    """
    # Check if video exists
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    # Create comment
    comment = Comment(
        user_id=current_user.id,
        video_id=video_id,
        content=request.content
    )
    db.add(comment)

    # Increment comment_count
    video.comment_count += 1

    db.commit()
    db.refresh(comment)

    # Create notification for video owner
    create_notification(
        db=db,
        user_id=video.user_id,
        notification_type="comment",
        actor_id=current_user.id,
        target_id=video_id
    )

    return comment


@router.get("/videos/{video_id}", response_model=CommentListResponse)
async def get_video_comments(
    video_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get comments for a video
    """
    # Check if video exists
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    # Get total count
    total = db.query(Comment).filter(Comment.video_id == video_id).count()

    # Get comments
    offset = (page - 1) * page_size
    comments = db.query(Comment).filter(
        Comment.video_id == video_id
    ).order_by(
        Comment.created_at.desc()
    ).offset(offset).limit(page_size).all()

    return CommentListResponse(
        comments=comments,
        total=total,
        page=page,
        page_size=page_size
    )


@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: UUID,
    request: CommentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a comment
    """
    # Find comment
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Check ownership
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment"
        )

    # Update comment
    comment.content = request.content

    db.commit()
    db.refresh(comment)

    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a comment
    """
    # Find comment
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Check ownership
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )

    # Get video to decrement count
    video = db.query(Video).filter(Video.id == comment.video_id).first()

    # Delete comment
    db.delete(comment)

    # Decrement comment_count
    if video and video.comment_count > 0:
        video.comment_count -= 1

    db.commit()

    return None


class CommentBatchInfoRequest(BaseModel):
    """Request to get info for multiple comments"""
    comment_ids: List[UUID]


@router.post("/batch-info")
async def get_comments_batch_info(
    request: CommentBatchInfoRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed info for multiple comments at once
    Includes author profile, follow status, and like count
    Maximum 100 comments per request
    """
    # Validate batch size
    if len(request.comment_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 comments per batch request"
        )

    if not request.comment_ids:
        return {"comments": {}}

    # Import Follow model
    from app.models.social import Follow

    # Query all comments with user relationship
    comments = db.query(Comment).filter(
        Comment.id.in_(request.comment_ids)
    ).all()

    # Get all unique user IDs from comments
    user_ids = list(set([comment.user_id for comment in comments]))

    # Check follow status for all users at once
    follows = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id.in_(user_ids)
    ).all()
    following_set = {follow.following_id for follow in follows}

    # Build result dictionary
    result = {}
    for comment in comments:
        result[str(comment.id)] = {
            "user": {
                "id": str(comment.user.id),
                "username": comment.user.username,
                "display_name": comment.user.display_name,
                "profile_image_url": comment.user.profile_image_url,
                "is_following": comment.user_id in following_set
            },
            "content": comment.content,
            "created_at": comment.created_at.isoformat(),
            "updated_at": comment.updated_at.isoformat()
        }

    return {"comments": result}


@router.post("/comments/{comment_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def like_comment(
    comment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Like a comment
    """
    # Check if comment exists
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Check if already liked
    existing_like = db.query(CommentLike).filter(
        CommentLike.user_id == current_user.id,
        CommentLike.comment_id == comment_id
    ).first()

    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment already liked"
        )

    # Create like
    like = CommentLike(
        user_id=current_user.id,
        comment_id=comment_id
    )
    db.add(like)

    # Increment like_count
    comment.like_count += 1

    db.commit()

    return None


@router.delete("/comments/{comment_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_comment(
    comment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unlike a comment
    """
    # Check if comment exists
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Find like
    like = db.query(CommentLike).filter(
        CommentLike.user_id == current_user.id,
        CommentLike.comment_id == comment_id
    ).first()

    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not liked"
        )

    # Delete like
    db.delete(like)

    # Decrement like_count
    if comment.like_count > 0:
        comment.like_count -= 1

    db.commit()

    return None


@router.get("/comments/{comment_id}/like/check")
async def check_comment_like(
    comment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if current user has liked a comment
    """
    like = db.query(CommentLike).filter(
        CommentLike.user_id == current_user.id,
        CommentLike.comment_id == comment_id
    ).first()

    return {"is_liked": like is not None}
