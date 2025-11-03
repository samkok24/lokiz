from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.image import ImageUploadRequest, ImageUploadResponse
from app.services.mock_s3_service import get_mock_s3_service

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/upload-url", response_model=ImageUploadResponse)
async def get_image_upload_url(
    request: ImageUploadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get presigned URL for image upload
    For glitch workflow - uploading user's own image
    """
    try:
        # Generate presigned URL (using mock for development)
        s3_service = get_mock_s3_service()
        upload_data = s3_service.generate_presigned_upload_url(
            file_type=request.file_type,
            folder="images"
        )

        return ImageUploadResponse(
            upload_url=upload_data['upload_url'],
            file_key=upload_data['file_key'],
            file_url=upload_data['file_url']
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate upload URL: {str(e)}"
        )
