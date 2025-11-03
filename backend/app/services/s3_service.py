import boto3
from botocore.exceptions import ClientError
from typing import Dict
from app.core.config import settings
import uuid


class S3Service:
    """AWS S3 service for file uploads"""

    def __init__(self):
        client_config = {
            'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY,
            'region_name': settings.S3_REGION
        }

        # Use LocalStack endpoint if configured
        if settings.S3_ENDPOINT_URL:
            client_config['endpoint_url'] = settings.S3_ENDPOINT_URL

        self.s3_client = boto3.client('s3', **client_config)
        self.bucket_name = settings.S3_BUCKET_NAME
        self.endpoint_url = settings.S3_ENDPOINT_URL

        # Create bucket if it doesn't exist (for LocalStack)
        if self.endpoint_url:
            self._ensure_bucket_exists()

    def generate_presigned_upload_url(
        self,
        file_type: str,
        folder: str = "videos",
        expiration: int = 3600
    ) -> Dict[str, str]:
        """
        Generate a presigned URL for uploading a file to S3

        Args:
            file_type: MIME type of the file (e.g., 'video/mp4')
            folder: S3 folder path
            expiration: URL expiration time in seconds (default: 1 hour)

        Returns:
            Dict with 'upload_url', 'file_key', and 'file_url'
        """
        file_extension = self._get_extension_from_mime(file_type)
        file_key = f"{folder}/{uuid.uuid4()}{file_extension}"

        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key,
                    'ContentType': file_type
                },
                ExpiresIn=expiration
            )

            # Use LocalStack endpoint if configured, otherwise use AWS S3
            if self.endpoint_url:
                file_url = f"{self.endpoint_url}/{self.bucket_name}/{file_key}"
            else:
                file_url = f"https://{self.bucket_name}.s3.{settings.S3_REGION}.amazonaws.com/{file_key}"

            return {
                'upload_url': presigned_url,
                'file_key': file_key,
                'file_url': file_url
            }
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")

    def _ensure_bucket_exists(self) -> None:
        """Ensure S3 bucket exists (for LocalStack)"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            # Bucket doesn't exist, create it
            try:
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            except ClientError:
                # Ignore error in development (LocalStack not running)
                pass
        except Exception:
            # Ignore any connection errors in development
            pass

    def _get_extension_from_mime(self, mime_type: str) -> str:
        """Get file extension from MIME type"""
        mime_to_ext = {
            'video/mp4': '.mp4',
            'video/quicktime': '.mov',
            'video/x-msvideo': '.avi',
            'video/webm': '.webm',
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'audio/mpeg': '.mp3',
            'audio/wav': '.wav'
        }
        return mime_to_ext.get(mime_type, '.bin')


# Lazy initialization to avoid connection error on import
_s3_service_instance = None


def get_s3_service() -> S3Service:
    global _s3_service_instance
    if _s3_service_instance is None:
        _s3_service_instance = S3Service()
    return _s3_service_instance
