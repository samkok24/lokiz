from typing import Dict
import uuid
import os
import shutil


class MockS3Service:
    """Mock S3 service for development without AWS"""

    def __init__(self):
        self.bucket_name = "lokiz-videos-mock"
        self.base_url = "https://mock-s3.lokiz.dev"
        self.sample_video_path = "/home/ubuntu/lokiz-backend/tests/sample.mp4"

    def generate_presigned_url(
        self,
        file_key: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate a mock presigned URL for a specific file key
        
        Args:
            file_key: S3 object key
            expiration: URL expiration time (ignored in mock)
            
        Returns:
            Presigned upload URL
        """
        return f"{self.base_url}/upload/{file_key}?mock=true"

    def generate_presigned_upload_url(
        self,
        file_type: str,
        folder: str = "videos",
        expiration: int = 3600
    ) -> Dict[str, str]:
        """
        Generate a mock presigned URL for development

        Args:
            file_type: MIME type of the file
            folder: S3 folder path
            expiration: URL expiration time (ignored in mock)

        Returns:
            Dict with 'upload_url', 'file_key', and 'file_url'
        """
        file_extension = self._get_extension_from_mime(file_type)
        file_key = f"{folder}/{uuid.uuid4()}{file_extension}"

        upload_url = f"{self.base_url}/upload/{file_key}?mock=true"
        file_url = f"{self.base_url}/{self.bucket_name}/{file_key}"

        return {
            'upload_url': upload_url,
            'file_key': file_key,
            'file_url': file_url
        }

    def download_file(self, s3_key: str, local_path: str) -> bool:
        """
        Mock download file from S3 (for development)
        Uses sample video for testing frame capture

        Args:
            s3_key: S3 object key
            local_path: Local file path to save

        Returns:
            True if successful
        """
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        # Use sample video if it exists
        if os.path.exists(self.sample_video_path):
            shutil.copy(self.sample_video_path, local_path)
            return True
        else:
            # Fallback: create empty file
            with open(local_path, 'w') as f:
                f.write('')
            return False

    def upload_file(self, local_path: str, s3_key: str) -> str:
        """
        Mock upload file to S3 (for development)
        In production, this would upload to actual S3

        Args:
            local_path: Local file path
            s3_key: S3 object key

        Returns:
            URL of uploaded file
        """
        # In mock mode, just return a mock URL
        return f"{self.base_url}/{self.bucket_name}/{s3_key}"

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


# Global instance
_mock_s3_service = MockS3Service()


def get_mock_s3_service() -> MockS3Service:
    return _mock_s3_service
