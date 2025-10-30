from pydantic import BaseModel, Field


class ImageUploadRequest(BaseModel):
    """Request to get presigned upload URL for image"""
    file_type: str = Field(..., description="MIME type (e.g., 'image/jpeg', 'image/png')")


class ImageUploadResponse(BaseModel):
    """Response with presigned upload URL for image"""
    upload_url: str
    file_key: str
    file_url: str
