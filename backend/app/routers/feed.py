from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional
from datetime import datetime, timedelta

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.video import Video
from app.models.social import VideoGlitch, Like, Follow, Block
from app.schemas.feed import FeedResponse
from app.schemas.user import UserBasicInfo

router = APIRouter(prefix="/feed", tags=["feed"])


def get_blocked_user_ids(db: Session, user_id) -> list:
    """Get list of user IDs blocked by current user"""
    blocks = db.query(Block.blocked_id).filter(Block.blocker_id == user_id).all()
    return [block.blocked_id for block in blocks]


def get_blocking_user_ids(db: Session, user_id) -> list:
    """Get list of user IDs who blocked current user"""
    blocks = db.query(Block.blocker_id).filter(Block.blocked_id == user_id).all()
    return [block.blocker_id for block in blocks]


def build_video_responses_optimized(db: Session, videos: list) -> list:
    """
    Build video responses with optimized batch queries (No N+1)
    """
    if not videos:
        return []
    
    video_ids = [v.id for v in videos]
    user_ids = list(set([v.user_id for v in videos]))
    
    # Batch query 1: Get all users at once
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    users_dict = {u.id: u for u in users}
    
    # Batch query 2: Get glitch counts for all videos at once
    glitch_counts = db.query(
        VideoGlitch.original_video_id,
        func.count(VideoGlitch.id).label('count')
    ).filter(
        VideoGlitch.original_video_id.in_(video_ids)
    ).group_by(VideoGlitch.original_video_id).all()
    glitch_counts_dict = {g[0]: g[1] for g in glitch_counts}
    
    # Batch query 3: Get original video IDs for glitches
    glitches = db.query(
        VideoGlitch.glitch_video_id,
        VideoGlitch.original_video_id
    ).filter(
        VideoGlitch.glitch_video_id.in_(video_ids)
    ).all()
    glitches_dict = {g[0]: g[1] for g in glitches}
    
    # Build responses using cached data
    video_responses = []
    for video in videos:
        user = users_dict.get(video.user_id)
        if not user:
            continue  # Skip if user not found (shouldn't happen)
        
        glitch_count = glitch_counts_dict.get(video.id, 0)
        original_video_id = glitches_dict.get(video.id)
        
        video_responses.append({
            "id": video.id,
            "user": UserBasicInfo(
                id=user.id,
                username=user.username,
                profile_image=user.profile_image
            ),
            "video_url": video.video_url,
            "thumbnail_url": video.thumbnail_url,
            "duration_seconds": video.duration_seconds,
            "caption": video.caption,
            "view_count": video.view_count,
            "like_count": video.like_count,
            "comment_count": video.comment_count,
            "glitch_count": glitch_count,
            "original_video_id": original_video_id,
            "created_at": video.created_at
        })
    
    return video_responses


@router.get("/for-you", response_model=FeedResponse)
async def get_for_you_feed(
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    For You feed with personalized recommendations
    
    Algorithm:
    1. Exclude blocked users and users who blocked you
    2. Prioritize videos from users you follow
    3. Show trending videos (high engagement in last 7 days)
    4. Mix in new content from various creators
    5. Avoid showing same creator consecutively
    
    Performance: Optimized with batch queries (No N+1)
    """
    # Get blocked user IDs (both ways)
    blocked_ids = get_blocked_user_ids(db, current_user.id)
    blocking_ids = get_blocking_user_ids(db, current_user.id)
    excluded_user_ids = list(set(blocked_ids + blocking_ids))
    
    # Get users current user follows
    following = db.query(Follow.following_id).filter(
        Follow.follower_id == current_user.id
    ).all()
    following_ids = [f.following_id for f in following]
    
    # Get videos current user already liked (to diversify recommendations)
    liked_video_ids = db.query(Like.video_id).filter(
        Like.user_id == current_user.id
    ).limit(100).all()
    liked_video_ids = [like.video_id for like in liked_video_ids]
    
    # Base query: completed, public videos
    query = db.query(Video).filter(
        Video.status == "completed",
        Video.is_public == True,
        Video.deleted_at.is_(None)
    )
    
    # Exclude blocked users
    if excluded_user_ids:
        query = query.filter(Video.user_id.notin_(excluded_user_ids))
    
    # Apply cursor pagination
    if cursor:
        query = query.filter(Video.id < cursor)
    
    # Calculate engagement score for ranking
    # Score = (likes * 3 + comments * 5 + glitches * 10 + views * 0.1) / days_old
    # Higher weight for recent content
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # Subquery for engagement score
    videos = query.order_by(
        # Prioritize followed users
        Video.user_id.in_(following_ids).desc() if following_ids else Video.created_at.desc(),
        # Then by engagement (like_count + comment_count + glitch_count)
        (Video.like_count + Video.comment_count * 2 + Video.glitch_count * 3).desc(),
        # Then by recency
        Video.created_at.desc()
    ).limit(page_size * 3).all()  # Get more to filter and diversify
    
    # Diversify: avoid consecutive videos from same creator
    diversified_videos = []
    last_user_id = None
    skipped_videos = []
    
    for video in videos:
        if len(diversified_videos) >= page_size:
            break
        
        # Skip if same user as last video
        if video.user_id == last_user_id:
            skipped_videos.append(video)
            continue
        
        diversified_videos.append(video)
        last_user_id = video.user_id
    
    # Fill remaining slots with skipped videos if needed
    if len(diversified_videos) < page_size:
        remaining = page_size - len(diversified_videos)
        diversified_videos.extend(skipped_videos[:remaining])
    
    # Limit to page_size
    videos = diversified_videos[:page_size]
    
    # Check if there are more videos
    has_more = len(videos) == page_size
    
    # Build video responses with optimized batch queries (No N+1)
    video_responses = build_video_responses_optimized(db, videos)
    
    # Get next cursor
    next_cursor = str(videos[-1].id) if has_more and videos else None
    
    return FeedResponse(
        videos=video_responses,
        total=len(video_responses),
        page_size=page_size,
        has_more=has_more,
        next_cursor=next_cursor,
        feed_type="for_you"
    )


@router.get("/following", response_model=FeedResponse)
async def get_following_feed(
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Following feed - videos from users you follow
    Sorted by recency (latest first)
    Excludes blocked users
    
    Performance: Optimized with batch queries (No N+1)
    """
    # Get blocked user IDs (both ways)
    blocked_ids = get_blocked_user_ids(db, current_user.id)
    blocking_ids = get_blocking_user_ids(db, current_user.id)
    excluded_user_ids = list(set(blocked_ids + blocking_ids))
    
    # Get users current user follows
    following = db.query(Follow.following_id).filter(
        Follow.follower_id == current_user.id
    ).all()
    following_ids = [f.following_id for f in following]
    
    # If not following anyone, return empty feed
    if not following_ids:
        return FeedResponse(
            videos=[],
            total=0,
            page_size=page_size,
            has_more=False,
            next_cursor=None,
            feed_type="following"
        )
    
    # Remove blocked users from following list
    if excluded_user_ids:
        following_ids = [uid for uid in following_ids if uid not in excluded_user_ids]
    
    # Base query: completed, public videos from followed users
    query = db.query(Video).filter(
        Video.status == "completed",
        Video.is_public == True,
        Video.deleted_at.is_(None),
        Video.user_id.in_(following_ids)
    )
    
    # Apply cursor pagination
    if cursor:
        query = query.filter(Video.id < cursor)
    
    # Get videos sorted by recency
    videos = query.order_by(Video.created_at.desc()).limit(page_size + 1).all()
    
    # Check if there are more videos
    has_more = len(videos) > page_size
    if has_more:
        videos = videos[:page_size]
    
    # Build video responses with optimized batch queries (No N+1)
    video_responses = build_video_responses_optimized(db, videos)
    
    # Get next cursor
    next_cursor = str(videos[-1].id) if has_more and videos else None
    
    return FeedResponse(
        videos=video_responses,
        total=len(video_responses),
        page_size=page_size,
        has_more=has_more,
        next_cursor=next_cursor,
        feed_type="following"
    )

