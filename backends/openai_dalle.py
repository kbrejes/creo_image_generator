"""DALL-E 3 image generation backend via OpenAI API."""

import httpx
from openai import AsyncOpenAI

from backends.base import ImageBackend, GenerationResult
from config import get_settings


class DallE3Backend(ImageBackend):
    """DALL-E 3 image generation backend."""

    name = "dalle3"
    display_name = "DALL-E 3"
    supports_negative_prompt = False
    supports_image_to_image = False
    supports_inpainting = False

    default_size = "1024x1024"
    supported_sizes = ["1024x1024", "1792x1024", "1024x1792"]
    supported_qualities = ["standard", "hd"]
    supported_styles = ["vivid", "natural"]

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str | None = None,
        negative_prompt: str | None = None,
        **kwargs,
    ) -> GenerationResult:
        """Generate an image using DALL-E 3."""
        try:
            # Validate parameters
            size = self.validate_size(size)
            if quality not in self.supported_qualities:
                quality = "standard"
            if style and style not in self.supported_styles:
                style = None

            # Build request parameters
            params = {
                "model": "dall-e-3",
                "prompt": prompt,
                "size": size,
                "quality": quality,
                "n": 1,  # DALL-E 3 only supports n=1
                "response_format": "url",
            }
            if style:
                params["style"] = style

            # Make API call
            response = await self.client.images.generate(**params)

            # Get the image URL and download the image
            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt

            # Download the image
            async with httpx.AsyncClient() as http_client:
                img_response = await http_client.get(image_url)
                img_response.raise_for_status()
                image_data = img_response.content

            return GenerationResult(
                success=True,
                image_data=image_data,
                image_url=image_url,
                revised_prompt=revised_prompt,
                metadata={
                    "model": "dall-e-3",
                    "size": size,
                    "quality": quality,
                    "style": style,
                },
            )

        except Exception as e:
            return GenerationResult(
                success=False,
                error=f"DALL-E 3 generation failed: {str(e)}",
            )
