"""Ideogram image generation backend."""

import httpx

from backends.base import ImageBackend, GenerationResult
from config import get_settings


class IdeogramBackend(ImageBackend):
    """Ideogram image generation backend - excellent for text in images."""

    name = "ideogram"
    display_name = "Ideogram"
    supports_negative_prompt = True
    supports_image_to_image = False
    supports_inpainting = False

    default_size = "1024x1024"
    supported_sizes = [
        "512x512",
        "768x768",
        "1024x1024",
        "1024x768",
        "768x1024",
        "1536x1024",
        "1024x1536",
    ]
    supported_qualities = ["standard", "high"]

    # Ideogram style presets
    STYLE_PRESETS = [
        "auto",
        "general",
        "realistic",
        "design",
        "render_3d",
        "anime",
    ]

    API_BASE = "https://api.ideogram.ai"

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.ideogram_api_key

    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str | None = None,
        negative_prompt: str | None = None,
        **kwargs,
    ) -> GenerationResult:
        """Generate an image using Ideogram API."""
        try:
            # Parse size
            size = self.validate_size(size)
            width, height = map(int, size.split("x"))

            # Determine aspect ratio from size
            aspect_ratio = self._get_aspect_ratio(width, height)

            # Build request payload
            payload = {
                "image_request": {
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "model": "V_2" if quality == "high" else "V_2_TURBO",
                    "magic_prompt_option": "AUTO",
                }
            }

            # Add style if provided and valid
            if style and style.upper() in [s.upper() for s in self.STYLE_PRESETS]:
                payload["image_request"]["style_type"] = style.upper()

            # Add negative prompt
            if negative_prompt:
                payload["image_request"]["negative_prompt"] = negative_prompt

            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.API_BASE}/generate",
                    headers={
                        "Api-Key": self.api_key,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=120.0,
                )

                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    return GenerationResult(
                        success=False,
                        error=f"Ideogram API error: {response.status_code} - {error_data}",
                    )

                data = response.json()
                images = data.get("data", [])

                if not images:
                    return GenerationResult(
                        success=False,
                        error="No images returned from Ideogram",
                    )

                # Get the first image URL
                image_url = images[0].get("url")
                if not image_url:
                    return GenerationResult(
                        success=False,
                        error="No image URL in response",
                    )

                # Download the image
                img_response = await client.get(image_url)
                img_response.raise_for_status()
                image_data = img_response.content

                return GenerationResult(
                    success=True,
                    image_data=image_data,
                    image_url=image_url,
                    revised_prompt=images[0].get("prompt"),
                    metadata={
                        "model": payload["image_request"]["model"],
                        "aspect_ratio": aspect_ratio,
                        "style": style,
                        "is_image_safe": images[0].get("is_image_safe"),
                    },
                )

        except Exception as e:
            return GenerationResult(
                success=False,
                error=f"Ideogram generation failed: {str(e)}",
            )

    def _get_aspect_ratio(self, width: int, height: int) -> str:
        """Convert width/height to Ideogram aspect ratio string."""
        ratio = width / height

        # Map to supported aspect ratios
        aspect_ratios = {
            1.0: "ASPECT_1_1",
            1.33: "ASPECT_4_3",
            0.75: "ASPECT_3_4",
            1.78: "ASPECT_16_9",
            0.56: "ASPECT_9_16",
            2.35: "ASPECT_21_9",
            0.43: "ASPECT_9_21",
            1.5: "ASPECT_3_2",
            0.67: "ASPECT_2_3",
        }

        # Find closest match
        closest_ratio = min(aspect_ratios.keys(), key=lambda x: abs(x - ratio))
        return aspect_ratios[closest_ratio]
