from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from pydantic import BaseModel

from app.core.deps import get_db
from app.models.hashtag import Hashtag
from app.models.video import Video
from app.models.social import VideoGlitch
from app.schemas.hashtag import (
    HashtagVideoListResponse,
    TrendingHashtagsResponse
)

router = APIRouter(prefix="/hashtags", tags=["hashtags"])


@router.get("/trending", response_model=TrendingHashtagsResponse)
async def get_trending_hashtags(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get trending hashtags (sorted by use_count)
    Public endpoint - no authentication required
    """
    hashtags = db.query(Hashtag).filter(
        Hashtag.use_count > 0
    ).order_by(
        Hashtag.use_count.desc()
    ).limit(limit).all()

    total = db.query(Hashtag).filter(Hashtag.use_count > 0).count()

    return TrendingHashtagsResponse(hashtags=hashtags, total=total)


@router.get("/{hashtag_name}/videos", response_model=HashtagVideoListResponse)
async def get_hashtag_videos(
    hashtag_name: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get videos for a specific hashtag
    Public endpoint - no authentication required
    Only returns completed and public videos
    """
    # Find hashtag (case-insensitive)
    hashtag = db.query(Hashtag).filter(
        Hashtag.name == hashtag_name.lower()
    ).first()

    if not hashtag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hashtag #{hashtag_name} not found"
        )

    # Get videos with this hashtag (only completed and public)
    videos = db.query(Video).join(
        Video.hashtags
    ).filter(
        Hashtag.id == hashtag.id,
        Video.status == "completed",
        Video.is_public.is_(True)
    ).order_by(
        Video.created_at.desc()
    ).limit(limit).all()

    # Add glitch_count to each video
    for video in videos:
        video.glitch_count = db.query(VideoGlitch).filter(
            VideoGlitch.original_video_id == video.id
        ).count()

    total = db.query(Video).join(
        Video.hashtags
    ).filter(
        Hashtag.id == hashtag.id,
        Video.status == "completed",
        Video.is_public.is_(True)
    ).count()

    return HashtagVideoListResponse(
        hashtag=hashtag,
        videos=videos,
        total=total
    )


class HashtagBatchStatsRequest(BaseModel):
    """Request to get stats for multiple hashtags"""
    hashtag_names: List[str]


@router.post("/batch-stats")
async def get_hashtags_batch_stats(
    request: HashtagBatchStatsRequest,
    db: Session = Depends(get_db)
):
    """
    Get statistics for multiple hashtags at once
    Includes video count, total views, latest thumbnail, and trending score
    Maximum 50 hashtags per request
    Public endpoint - no authentication required
    """
    # Validate batch size
    if len(request.hashtag_names) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 hashtags per batch request"
        )

    if not request.hashtag_names:
        return {"hashtags": {}}

    # Normalize hashtag names (lowercase)
    normalized_names = [name.lower() for name in request.hashtag_names]

    # Query all hashtags
    hashtags = db.query(Hashtag).filter(
        Hashtag.name.in_(normalized_names)
    ).all()

    # Build result dictionary
    result = {}
    for hashtag in hashtags:
        # Get video count
        video_count = db.query(Video).join(
            Video.hashtags
        ).filter(
            Hashtag.id == hashtag.id,
            Video.status == "completed",
            Video.is_public.is_(True),
            Video.deleted_at.is_(None)
        ).count()

        # Get total views (sum of view_count from all videos with this hashtag)
        total_views = db.query(func.sum(Video.view_count)).join(
            Video.hashtags
        ).filter(
            Hashtag.id == hashtag.id,
            Video.status == "completed",
            Video.is_public.is_(True),
            Video.deleted_at.is_(None)
        ).scalar() or 0

        # Get latest video thumbnail
        latest_video = db.query(Video).join(
            Video.hashtags
        ).filter(
            Hashtag.id == hashtag.id,
            Video.status == "completed",
            Video.is_public.is_(True),
            Video.deleted_at.is_(None)
        ).order_by(Video.created_at.desc()).first()

        latest_thumbnail = latest_video.thumbnail_url if latest_video else None

        # Calculate trending score (simple formula: use_count * 0.7 + video_count * 0.3)
        trending_score = round(hashtag.use_count * 0.7 + video_count * 0.3, 2)

        result[hashtag.name] = {
            "video_count": video_count,
            "total_views": int(total_views),
            "latest_thumbnail": latest_thumbnail,
            "trending_score": trending_score,
            "use_count": hashtag.use_count
        }

    # Add missing hashtags as not found
    for name in normalized_names:
        if name not in result:
            result[name] = {
                "video_count": 0,
                "total_views": 0,
                "latest_thumbnail": None,
                "trending_score": 0.0,
                "use_count": 0
            }

    return {"hashtags": result}
