import replicate
from typing import Dict, Any, Optional
from app.core.config import settings


class ReplicateService:
    """Service for interacting with Replicate API"""

    def __init__(self):
        self.client = replicate.Client(api_token=settings.REPLICATE_API_TOKEN)

    def generate_i2v_template(
        self,
        image_url: str,
        prompt: str,
        duration: int = 5
    ) -> Dict[str, Any]:
        """
        Generate video from image using I2V model with template prompt
        Used for Motion/Style templates (AI Hug, Dance Motion, etc.)

        Args:
            image_url: URL of the captured frame image
            prompt: Template prompt (e.g., "AI hug motion", "dance motion")
            duration: Video duration in seconds (5-10)

        Returns:
            Dict with 'output_url' and 'model'
        """
        model = "google/veo-3-fast"

        input_data = {
            "image": image_url,
            "prompt": prompt,
            "duration": duration
        }

        # Run the model
        output = self.client.run(model, input=input_data)

        return {
            'output_url': output if isinstance(output, str) else output[0],
            'model': model
        }

    def generate_glitch_animate(
        self,
        template_video_url: str,
        user_image_url: str,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply template video's motion to user's image using WAN 2.2 Animate
        Used for Glitch feature (Feed → Studio workflow)

        Args:
            template_video_url: URL of the template video from feed
            user_image_url: URL of user's uploaded image or captured frame
            prompt: Optional additional prompt

        Returns:
            Dict with 'output_url' and 'model'
        """
        model = "wan-video/wan-2.2-animate-animation"

        input_data = {
            "video": template_video_url,
            "image": user_image_url
        }

        if prompt:
            input_data["prompt"] = prompt

        # Run the model
        output = self.client.run(model, input=input_data)

        return {
            'output_url': output if isinstance(output, str) else output[0],
            'model': model
        }

    def generate_glitch_replace(
        self,
        template_video_url: str,
        user_image_url: str,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Replace template video's subject with user's image using WAN 2.2 Replace
        Used for Glitch feature (Feed → Studio workflow)

        Args:
            template_video_url: URL of the template video from feed
            user_image_url: URL of user's uploaded image or captured frame
            prompt: Optional additional prompt

        Returns:
            Dict with 'output_url' and 'model'
        """
        model = "wan-video/wan-2.2-animate-replace"

        input_data = {
            "video": template_video_url,
            "image": user_image_url
        }

        if prompt:
            input_data["prompt"] = prompt

        # Run the model
        output = self.client.run(model, input=input_data)

        return {
            'output_url': output if isinstance(output, str) else output[0],
            'model': model
        }

    def generate_sticker_to_reality(
        self,
        video_url: str,
        image_url: str,
        start_time: float,
        end_time: float,
        prompt: str
    ) -> Dict[str, Any]:
        """
        AI Auto Integration (Sticker to Reality)
        Naturally integrate an image into a video segment with automatic background removal,
        context analysis (movement, lighting, shadows)

        Args:
            video_url: URL of the template video
            image_url: URL of the image to integrate
            start_time: Start time in seconds
            end_time: End time in seconds (max 10 seconds from start)
            prompt: User's instruction for how to integrate the image

        Returns:
            Dict with 'output_url' and 'model'
        """
        # Using Luma Dream Machine for video modification
        model = "luma/modify-video"

        input_data = {
            "video": video_url,
            "image": image_url,
            "start_time": start_time,
            "end_time": end_time,
            "prompt": prompt,
            "remove_background": True,  # Automatic background removal
            "context_aware": True  # Analyze movement, lighting, shadows
        }

        # Run the model
        output = self.client.run(model, input=input_data)

        return {
            'output_url': output if isinstance(output, str) else output[0],
            'model': model
        }

    def generate_music(
        self,
        prompt: str,
        duration: int = 60
    ) -> Dict[str, Any]:
        """
        Generate music using Suno AI Bark

        Args:
            prompt: Text prompt for music generation (e.g., "upbeat electronic beat")
            duration: Music duration in seconds (default: 60)

        Returns:
            Dict with 'output_url' and 'model'
        """
        model = "suno-ai/bark"

        input_data = {
            "prompt": prompt,
            "duration": duration
        }

        # Run the model
        output = self.client.run(model, input=input_data)

        return {
            'output_url': output if isinstance(output, str) else output[0],
            'model': model
        }


# Global instance
_replicate_service = ReplicateService()


def get_replicate_service() -> ReplicateService:
    return _replicate_service
