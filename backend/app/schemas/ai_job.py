from pydantic import BaseModel, validator
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any


class AIJobCreateRequest(BaseModel):
    """AI job creation request"""
    job_type: str  # i2v_template, glitch_animate, glitch_replace, music
    input_data: Dict[str, Any]


class AIJobResponse(BaseModel):
    """AI job response"""
    id: UUID
    user_id: UUID
    job_type: str
    status: str  # pending, processing, completed, failed
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    credits_used: int
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class FrameCaptureRequest(BaseModel):
    """Frame capture request"""
    video_id: UUID
    timestamp: float  # Time in seconds


class FrameCaptureResponse(BaseModel):
    """Frame capture response"""
    image_url: str
    timestamp: float
    video_id: UUID


class I2VTemplateRequest(BaseModel):
    """I2V Template generation request (Motion/Style templates)"""
    image_url: str
    template: str  # Template name (e.g., "ai_hug", "dance_motion")
    prompt: str  # Template prompt
    duration: int = 5  # 5-10 seconds

    @validator('duration')
    def validate_duration(cls, v):
        if not 5 <= v <= 10:
            raise ValueError('Duration must be between 5 and 10 seconds')
        return v


class GlitchAnimateRequest(BaseModel):
    """Glitch Animate request (WAN 2.2 Animate)"""
    template_video_id: UUID  # Video from feed to use as template
    user_image_url: str  # User's image or captured frame
    prompt: Optional[str] = None


class GlitchReplaceRequest(BaseModel):
    """Glitch Replace request (WAN 2.2 Replace)"""
    template_video_id: UUID  # Video from feed to use as template
    user_image_url: str  # User's image or captured frame
    prompt: Optional[str] = None


class MusicGenerationRequest(BaseModel):
    """Music generation request"""
    prompt: str
    duration: int = 60


class StickerToRealityRequest(BaseModel):
    """AI Auto Integration (Sticker to Reality) request"""
    video_id: UUID  # Video to apply sticker (can be own video, I2V generated, or template for glitch)
    user_image_url: str  # User's image to integrate
    start_time: float  # Start time in seconds
    end_time: float  # End time in seconds (max 10 seconds from start)
    prompt: str  # User's instruction for how to integrate the image
    is_glitch: bool = False  # True if this is a glitch (from feed), False if editing own video

    @validator('end_time')
    def validate_duration(cls, v, values):
        if 'start_time' in values:
            duration = v - values['start_time']
            if duration > 10:
                raise ValueError('Duration cannot exceed 10 seconds')
            if duration <= 0:
                raise ValueError('End time must be after start time')
        return v
