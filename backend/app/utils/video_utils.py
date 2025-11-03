import subprocess
import os
from typing import Optional


def extract_frame_from_video(
    video_path: str,
    timestamp: float,
    output_path: str
) -> bool:
    """
    Extract a single frame from video at specified timestamp

    Args:
        video_path: Path to the input video file
        timestamp: Time in seconds to extract frame from
        output_path: Path to save the extracted frame image

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Use ffmpeg to extract frame
        command = [
            'ffmpeg',
            '-ss', str(timestamp),  # Seek to timestamp
            '-i', video_path,  # Input video
            '-frames:v', '1',  # Extract 1 frame
            '-q:v', '2',  # High quality
            '-y',  # Overwrite output file
            output_path
        ]

        subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        return os.path.exists(output_path)

    except subprocess.CalledProcessError as e:
        print(f"Error extracting frame: {e.stderr.decode()}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False


def get_video_duration(video_path: str) -> Optional[float]:
    """
    Get the duration of a video file in seconds

    Args:
        video_path: Path to the video file

    Returns:
        Duration in seconds, or None if error
    """
    try:
        command = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        duration = float(result.stdout.decode().strip())
        return duration

    except Exception as e:
        print(f"Error getting video duration: {str(e)}")
        return None
