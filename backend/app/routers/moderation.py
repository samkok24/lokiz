from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.video import Video
from app.models.social import Comment, Block, Report
from app.schemas.moderation import (
    BlockUserRequest,
    BlockResponse,
    BlockedUserResponse,
    BlockListResponse,
    ReportRequest,
    ReportResponse,
    ReportListResponse
)
from app.schemas.user import UserBasicInfo

router = APIRouter(prefix="/moderation", tags=["moderation"])


@router.post("/block", response_model=BlockResponse, status_code=status.HTTP_201_CREATED)
async def block_user(
    request: BlockUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Block a user
    Blocked users' content will not appear in your feed
    """
    # Cannot block yourself
    if request.blocked_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot block yourself"
        )
    
    # Check if user exists
    blocked_user = db.query(User).filter(User.id == request.blocked_user_id).first()
    if not blocked_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already blocked
    existing_block = db.query(Block).filter(
        Block.blocker_id == current_user.id,
        Block.blocked_id == request.blocked_user_id
    ).first()
    
    if existing_block:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already blocked"
        )
    
    # Create block
    block = Block(
        blocker_id=current_user.id,
        blocked_id=request.blocked_user_id
    )
    db.add(block)
    db.commit()
    db.refresh(block)
    
    return block


@router.delete("/block/{blocked_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unblock_user(
    blocked_user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unblock a user
    """
    block = db.query(Block).filter(
        Block.blocker_id == current_user.id,
        Block.blocked_id == blocked_user_id
    ).first()
    
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found"
        )
    
    db.delete(block)
    db.commit()
    
    return None


@router.get("/blocks", response_model=BlockListResponse)
async def get_blocked_users(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of blocked users
    """
    blocks = db.query(Block).filter(
        Block.blocker_id == current_user.id
    ).order_by(Block.created_at.desc()).limit(limit).all()
    
    # Build response with user details (optimized batch query)
    blocked_users = []
    
    if blocks:
        # Batch query: Get all blocked users at once (No N+1)
        blocked_user_ids = [block.blocked_id for block in blocks]
        users = db.query(User).filter(User.id.in_(blocked_user_ids)).all()
        users_dict = {u.id: u for u in users}
        
        # Build responses using cached data
        for block in blocks:
            blocked_user = users_dict.get(block.blocked_id)
            if blocked_user:
                blocked_users.append(BlockedUserResponse(
                    id=block.id,
                    blocked_user=UserBasicInfo(
                        id=blocked_user.id,
                        username=blocked_user.username,
                        profile_image=blocked_user.profile_image
                    ),
                    created_at=block.created_at
                ))
    
    total = db.query(Block).filter(Block.blocker_id == current_user.id).count()
    
    return BlockListResponse(
        blocks=blocked_users,
        total=total
    )


@router.post("/report", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def report_content(
    request: ReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Report a user, video, or comment
    At least one of reported_user_id, reported_video_id, or reported_comment_id must be provided
    """
    # Validate that at least one target is provided
    if not any([request.reported_user_id, request.reported_video_id, request.reported_comment_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide at least one of: reported_user_id, reported_video_id, reported_comment_id"
        )
    
    # Validate that only one target is provided
    targets = [request.reported_user_id, request.reported_video_id, request.reported_comment_id]
    if sum(1 for t in targets if t is not None) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only report one item at a time"
        )
    
    # Verify reported content exists
    if request.reported_user_id:
        user = db.query(User).filter(User.id == request.reported_user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Cannot report yourself
        if request.reported_user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot report yourself"
            )
    
    if request.reported_video_id:
        video = db.query(Video).filter(Video.id == request.reported_video_id).first()
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
    if request.reported_comment_id:
        comment = db.query(Comment).filter(Comment.id == request.reported_comment_id).first()
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    
    # Create report
    report = Report(
        reporter_id=current_user.id,
        reported_user_id=request.reported_user_id,
        reported_video_id=request.reported_video_id,
        reported_comment_id=request.reported_comment_id,
        report_type=request.report_type,
        reason=request.reason,
        status="pending"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report


@router.get("/reports", response_model=ReportListResponse)
async def get_my_reports(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of reports made by current user
    """
    reports = db.query(Report).filter(
        Report.reporter_id == current_user.id
    ).order_by(Report.created_at.desc()).limit(limit).all()
    
    total = db.query(Report).filter(Report.reporter_id == current_user.id).count()
    
    return ReportListResponse(
        reports=reports,
        total=total
    )


@router.get("/is-blocked/{user_id}")
async def check_if_blocked(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if a user is blocked by current user
    """
    block = db.query(Block).filter(
        Block.blocker_id == current_user.id,
        Block.blocked_id == user_id
    ).first()
    
    return {"is_blocked": block is not None}

