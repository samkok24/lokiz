from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from pydantic import BaseModel
import os
import uuid

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.video import Video
from app.models.ai_job import AIJob
from app.models.social import VideoGlitch
from app.schemas.ai_job import (
    I2VTemplateRequest,
    GlitchAnimateRequest,
    GlitchReplaceRequest,
    StickerToRealityRequest,
    MusicGenerationRequest,
    FrameCaptureRequest,
    FrameCaptureResponse,
    AIJobResponse
)
from app.services.replicate_service import get_replicate_service
from app.services.mock_s3_service import get_mock_s3_service
from app.utils.video_utils import extract_frame_from_video
from app.utils.notification_utils import create_notification

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/capture-frame", response_model=FrameCaptureResponse)
async def capture_frame(
    request: FrameCaptureRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Capture a frame from video at specified timestamp
    Returns image URL for use in I2V generation
    """
    # Verify video ownership
    video = db.query(Video).filter(
        Video.id == request.video_id,
        Video.user_id == current_user.id
    ).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    try:
        # Get S3 service
        s3_service = get_mock_s3_service()

        # Download video from S3
        local_video_path = f"/tmp/{video.id}.mp4"
        s3_service.download_file(video.s3_key, local_video_path)

        # Extract frame
        frame_filename = f"{uuid.uuid4()}.jpg"
        local_frame_path = f"/tmp/{frame_filename}"

        success = extract_frame_from_video(
            video_path=local_video_path,
            timestamp=request.timestamp,
            output_path=local_frame_path
        )

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to extract frame from video"
            )

        # Upload frame to S3
        frame_s3_key = f"frames/{current_user.id}/{frame_filename}"
        frame_url = s3_service.upload_file(local_frame_path, frame_s3_key)

        # Clean up local files
        os.remove(local_video_path)
        os.remove(local_frame_path)

        return FrameCaptureResponse(
            image_url=frame_url,
            timestamp=request.timestamp,
            video_id=video.id
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to capture frame: {str(e)}"
        )


@router.post("/template", response_model=AIJobResponse)
async def generate_template_video(
    request: I2VTemplateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate video from image using template prompt (Motion/Style templates)
    Cost: 20 credits
    Duration: 5-10 seconds
    Credits deducted only on success
    """
    CREDITS_REQUIRED = 20

    # Check credits
    if current_user.credits < CREDITS_REQUIRED:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. Required: {CREDITS_REQUIRED}, Available: {current_user.credits}"
        )

    ai_job = None
    try:
        # Create AI job record (no credit deduction yet)
        ai_job = AIJob(
            user_id=current_user.id,
            job_type="i2v_template",
            status="processing",
            input_data={
                "image_url": request.image_url,
                "template": request.template,
                "prompt": request.prompt,
                "duration": request.duration
            },
            credits_used=CREDITS_REQUIRED
        )
        db.add(ai_job)
        db.commit()
        db.refresh(ai_job)

        # Generate video using Replicate
        replicate_service = get_replicate_service()
        result = replicate_service.generate_i2v_template(
            image_url=request.image_url,
            prompt=request.prompt,
            duration=request.duration
        )

        # Success: Deduct credits
        current_user.credits -= CREDITS_REQUIRED

        # Create new video record (processing state)
        new_video = Video(
            user_id=current_user.id,
            title=f"Template: {request.template}",
            video_url=result['output_url'],
            thumbnail_url=result.get('thumbnail_url', result['output_url']),
            s3_key=f"templates/{ai_job.id}.mp4",
            duration_seconds=request.duration,
            status="processing"
        )
        db.add(new_video)
        db.flush()

        # Update job with result
        ai_job.status = "completed"
        ai_job.output_data = {
            "video_url": result['output_url'],
            "model": result['model'],
            "video_id": str(new_video.id)
        }

        db.commit()
        db.refresh(ai_job)

        return ai_job

    except Exception as e:
        # Mark job as failed (no credit deduction)
        if ai_job:
            ai_job.status = "failed"
            ai_job.error_message = str(e)
            db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate video: {str(e)}"
        )


@router.post("/glitch/animate", response_model=AIJobResponse)
async def generate_glitch_animate(
    request: GlitchAnimateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Apply template video's motion to user's image (Glitch - Animate)
    Cost: 30 credits
    Duration: 5-10 seconds
    Creates glitch relationship record
    Credits deducted only on success
    """
    CREDITS_REQUIRED = 30

    # Check credits
    if current_user.credits < CREDITS_REQUIRED:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. Required: {CREDITS_REQUIRED}, Available: {current_user.credits}"
        )

    # Verify template video exists
    template_video = db.query(Video).filter(Video.id == request.template_video_id).first()
    if not template_video:
        raise HTTPException(status_code=404, detail="Template video not found")

    ai_job = None
    try:
        # Create AI job record (no credit deduction yet)
        ai_job = AIJob(
            user_id=current_user.id,
            job_type="glitch_animate",
            status="processing",
            input_data={
                "template_video_id": str(request.template_video_id),
                "template_video_url": template_video.video_url,
                "user_image_url": request.user_image_url,
                "prompt": request.prompt
            },
            credits_used=CREDITS_REQUIRED
        )
        db.add(ai_job)
        db.commit()
        db.refresh(ai_job)

        # Generate video using Replicate
        replicate_service = get_replicate_service()
        result = replicate_service.generate_glitch_animate(
            template_video_url=template_video.video_url,
            user_image_url=request.user_image_url,
            prompt=request.prompt
        )

        # Success: Deduct credits
        current_user.credits -= CREDITS_REQUIRED

        # Create new video record for glitch result (processing state)
        new_video = Video(
            user_id=current_user.id,
            title=f"Glitch from {template_video.title or 'video'}",
            video_url=result['output_url'],
            thumbnail_url=result.get('thumbnail_url', result['output_url']),
            s3_key=f"glitch/{ai_job.id}.mp4",
            duration_seconds=5,
            status="processing"
        )
        db.add(new_video)
        db.flush()

        # Record glitch relationship
        video_glitch = VideoGlitch(
            original_video_id=template_video.id,
            glitch_video_id=new_video.id,
            glitch_type="animate"
        )
        db.add(video_glitch)

        # Increment glitch_count on template video
        template_video.glitch_count += 1

        # Create notification for template video owner
        create_notification(
            db=db,
            user_id=template_video.user_id,
            notification_type="glitch",
            actor_id=current_user.id,
            target_id=template_video.id
        )

        # Update job with result (including video_id)
        ai_job.status = "completed"
        ai_job.output_data = {
            "video_url": result['output_url'],
            "model": result['model'],
            "video_id": str(new_video.id)
        }

        db.commit()
        db.refresh(ai_job)

        return ai_job

    except Exception as e:
        # Mark job as failed (no credit deduction)
        if ai_job:
            ai_job.status = "failed"
            ai_job.error_message = str(e)
            db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate glitch video: {str(e)}"
        )


@router.post("/glitch/replace", response_model=AIJobResponse)
async def generate_glitch_replace(
    request: GlitchReplaceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Replace template video's subject with user's image (Glitch - Replace)
    Cost: 30 credits
    Duration: 5-10 seconds
    Creates glitch relationship record
    Credits deducted only on success
    """
    CREDITS_REQUIRED = 30

    # Check credits
    if current_user.credits < CREDITS_REQUIRED:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. Required: {CREDITS_REQUIRED}, Available: {current_user.credits}"
        )

    # Verify template video exists
    template_video = db.query(Video).filter(Video.id == request.template_video_id).first()
    if not template_video:
        raise HTTPException(status_code=404, detail="Template video not found")

    ai_job = None
    try:
        # Create AI job record (no credit deduction yet)
        ai_job = AIJob(
            user_id=current_user.id,
            job_type="glitch_replace",
            status="processing",
            input_data={
                "template_video_id": str(request.template_video_id),
                "template_video_url": template_video.video_url,
                "user_image_url": request.user_image_url,
                "prompt": request.prompt
            },
            credits_used=CREDITS_REQUIRED
        )
        db.add(ai_job)
        db.commit()
        db.refresh(ai_job)

        # Generate video using Replicate
        replicate_service = get_replicate_service()
        result = replicate_service.generate_glitch_replace(
            template_video_url=template_video.video_url,
            user_image_url=request.user_image_url,
            prompt=request.prompt
        )

        # Success: Deduct credits
        current_user.credits -= CREDITS_REQUIRED

        # Create new video record for glitch result (processing state)
        new_video = Video(
            user_id=current_user.id,
            title=f"Glitch from {template_video.title or 'video'}",
            video_url=result['output_url'],
            thumbnail_url=result.get('thumbnail_url', result['output_url']),
            s3_key=f"glitch/{ai_job.id}.mp4",
            duration_seconds=5,
            status="processing"
        )
        db.add(new_video)
        db.flush()

        # Record glitch relationship
        video_glitch = VideoGlitch(
            original_video_id=template_video.id,
            glitch_video_id=new_video.id,
            glitch_type="replace"
        )
        db.add(video_glitch)

        # Increment glitch_count on template video
        template_video.glitch_count += 1

        # Create notification for template video owner
        create_notification(
            db=db,
            user_id=template_video.user_id,
            notification_type="glitch",
            actor_id=current_user.id,
            target_id=template_video.id
        )

        # Update job with result (including video_id)
        ai_job.status = "completed"
        ai_job.output_data = {
            "video_url": result['output_url'],
            "model": result['model'],
            "video_id": str(new_video.id)
        }

        db.commit()
        db.refresh(ai_job)

        return ai_job

    except Exception as e:
        # Mark job as failed (no credit deduction)
        if ai_job:
            ai_job.status = "failed"
            ai_job.error_message = str(e)
            db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate glitch video: {str(e)}"
        )


@router.post("/music", response_model=AIJobResponse)
async def generate_music(
    request: MusicGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate music
    Cost: 5 credits
    Credits deducted only on success
    """
    CREDITS_REQUIRED = 5

    # Check credits
    if current_user.credits < CREDITS_REQUIRED:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. Required: {CREDITS_REQUIRED}, Available: {current_user.credits}"
        )

    ai_job = None
    try:
        # Create AI job record (no credit deduction yet)
        ai_job = AIJob(
            user_id=current_user.id,
            job_type="music",
            status="processing",
            input_data={
                "prompt": request.prompt,
                "duration": request.duration
            },
            credits_used=CREDITS_REQUIRED
        )
        db.add(ai_job)
        db.commit()
        db.refresh(ai_job)

        # Generate music using Replicate
        replicate_service = get_replicate_service()
        result = replicate_service.generate_music(
            prompt=request.prompt,
            duration=request.duration
        )

        # Success: Deduct credits
        current_user.credits -= CREDITS_REQUIRED

        # Update job with result
        ai_job.status = "completed"
        ai_job.output_data = {
            "audio_url": result['output_url'],
            "model": result['model']
        }

        db.commit()
        db.refresh(ai_job)

        return ai_job

    except Exception as e:
        # Mark job as failed (no credit deduction)
        if ai_job:
            ai_job.status = "failed"
            ai_job.error_message = str(e)
            db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate music: {str(e)}"
        )


@router.post("/sticker-to-reality", response_model=AIJobResponse)
async def generate_sticker_to_reality(
    request: StickerToRealityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI Auto Integration (Sticker to Reality)
    Naturally integrate an image into a video segment
    Cost: 45 credits
    Max duration: 10 seconds
    
    Works in two modes:
    1. Glitch mode (is_glitch=True): Creates glitch relationship with template video
    2. Edit mode (is_glitch=False): Edits user's own video (uploaded or I2V generated)
    
    Credits deducted only on success
    """
    CREDITS_REQUIRED = 45

    # Check credits
    if current_user.credits < CREDITS_REQUIRED:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. Required: {CREDITS_REQUIRED}, Available: {current_user.credits}"
        )

    # Verify video exists
    source_video = db.query(Video).filter(Video.id == request.video_id).first()
    if not source_video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # If not glitch mode, verify ownership
    if not request.is_glitch and source_video.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only edit your own videos. Set is_glitch=True to glitch others' videos."
        )

    # Validate duration
    duration = request.end_time - request.start_time
    if duration > 10:
        raise HTTPException(
            status_code=400,
            detail="Duration cannot exceed 10 seconds"
        )
    if duration <= 0:
        raise HTTPException(
            status_code=400,
            detail="End time must be after start time"
        )

    ai_job = None
    try:
        # Create AI job record (no credit deduction yet)
        ai_job = AIJob(
            user_id=current_user.id,
            job_type="sticker_to_reality",
            status="processing",
            input_data={
                "video_id": str(request.video_id),
                "video_url": source_video.video_url,
                "user_image_url": request.user_image_url,
                "start_time": request.start_time,
                "end_time": request.end_time,
                "prompt": request.prompt,
                "is_glitch": request.is_glitch
            },
            credits_used=CREDITS_REQUIRED
        )
        db.add(ai_job)
        db.commit()
        db.refresh(ai_job)

        # Generate video using Replicate
        replicate_service = get_replicate_service()
        result = replicate_service.generate_sticker_to_reality(
            video_url=source_video.video_url,
            image_url=request.user_image_url,
            start_time=request.start_time,
            end_time=request.end_time,
            prompt=request.prompt
        )

        # Success: Deduct credits
        current_user.credits -= CREDITS_REQUIRED

        # Create new video record for result (processing state)
        if request.is_glitch:
            title = f"Sticker to Reality from {source_video.title or 'video'}"
        else:
            title = f"Sticker to Reality - {source_video.title or 'My Video'}"
        
        new_video = Video(
            user_id=current_user.id,
            title=title,
            video_url=result['output_url'],
            thumbnail_url=result.get('thumbnail_url', result['output_url']),
            s3_key=f"sticker/{ai_job.id}.mp4",
            duration_seconds=int(duration),
            status="processing"
        )
        db.add(new_video)
        db.flush()

        # If glitch mode, record glitch relationship
        if request.is_glitch:
            video_glitch = VideoGlitch(
                original_video_id=source_video.id,
                glitch_video_id=new_video.id,
                glitch_type="sticker_to_reality"
            )
            db.add(video_glitch)

            # Increment glitch_count on source video
            source_video.glitch_count += 1

            # Create notification for source video owner
            if source_video.user_id != current_user.id:
                create_notification(
                    db=db,
                    user_id=source_video.user_id,
                    notification_type="glitch",
                    actor_id=current_user.id,
                    target_id=source_video.id
                )

        # Update job with result (including video_id)
        ai_job.status = "completed"
        ai_job.output_data = {
            "video_url": result['output_url'],
            "model": result['model'],
            "video_id": str(new_video.id)
        }

        db.commit()
        db.refresh(ai_job)

        return ai_job

    except Exception as e:
        # Mark job as failed (no credit deduction)
        if ai_job:
            ai_job.status = "failed"
            ai_job.error_message = str(e)
            db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate sticker to reality video: {str(e)}"
        )


@router.get("/jobs/{job_id}", response_model=AIJobResponse)
async def get_ai_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI job status"""
    ai_job = db.query(AIJob).filter(
        AIJob.id == job_id,
        AIJob.user_id == current_user.id
    ).first()

    if not ai_job:
        raise HTTPException(status_code=404, detail="AI job not found")

    return ai_job


class AIJobBatchStatusRequest(BaseModel):
    """Request to check status of multiple AI jobs"""
    job_ids: List[UUID]


@router.post("/jobs/batch-status")
async def get_ai_jobs_batch_status(
    request: AIJobBatchStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get status of multiple AI jobs at once
    Maximum 50 jobs per request
    Used for polling progress of multiple ongoing jobs
    """
    # Validate batch size
    if len(request.job_ids) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 jobs per batch request"
        )

    if not request.job_ids:
        return {"jobs": {}}

    # Query all jobs for the user in one go
    jobs = db.query(AIJob).filter(
        AIJob.user_id == current_user.id,
        AIJob.id.in_(request.job_ids)
    ).all()

    # Build result dictionary
    result = {
        str(job.id): {
            "status": job.status,
            "progress": job.progress or 0,
            "result_url": job.result_url,
            "error": job.error_message
        }
        for job in jobs
    }

    # Add missing jobs as not found
    for job_id in request.job_ids:
        if str(job_id) not in result:
            result[str(job_id)] = {
                "status": "not_found",
                "progress": 0,
                "result_url": None,
                "error": "Job not found"
            }

    return {"jobs": result}
