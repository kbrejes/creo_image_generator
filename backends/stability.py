"""Stability AI image generation backend."""

import httpx

from backends.base import ImageBackend, GenerationResult
from config import get_settings


class StabilityBackend(ImageBackend):
    """Stability AI image generation backend (SDXL, SD3)."""

    name = "stability"
    display_name = "Stability AI"
    supports_negative_prompt = True
    supports_image_to_image = True
    supports_inpainting = True

    default_size = "1024x1024"
    supported_sizes = [
        "512x512",
        "768x768",
        "1024x1024",
        "1152x896",
        "896x1152",
        "1216x832",
        "832x1216",
        "1344x768",
        "768x1344",
        "1536x640",
        "640x1536",
    ]
    supported_qualities = ["standard", "high"]

    # Available engines
    ENGINES = {
        "sdxl": "stable-diffusion-xl-1024-v1-0",
        "sd3": "sd3-large",
        "sd3-turbo": "sd3-turbo",
    }

    API_BASE = "https://api.stability.ai"

    def __init__(self, engine: str = "sdxl"):
        settings = get_settings()
        self.api_key = settings.stability_api_key
        self.engine = self.ENGINES.get(engine, self.ENGINES["sdxl"])

    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str | None = None,
        negative_prompt: str | None = None,
        **kwargs,
    ) -> GenerationResult:
        """Generate an image using Stability AI."""
        try:
            # Parse size
            size = self.validate_size(size)
            width, height = map(int, size.split("x"))

            # Determine steps based on quality
            steps = 30 if quality == "standard" else 50

            # Build request payload
            payload = {
                "text_prompts": [
                    {"text": prompt, "weight": 1.0},
                ],
                "cfg_scale": kwargs.get("cfg_scale", 7),
                "height": height,
                "width": width,
                "samples": 1,
                "steps": steps,
            }

            # Add negative prompt
            if negative_prompt:
                payload["text_prompts"].append(
                    {"text": negative_prompt, "weight": -1.0}
                )

            # Add style preset if provided
            if style:
                payload["style_preset"] = style

            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.API_BASE}/v1/generation/{self.engine}/text-to-image",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    json=payload,
                    timeout=120.0,
                )

                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    return GenerationResult(
                        success=False,
                        error=f"Stability API error: {response.status_code} - {error_data}",
                    )

                data = response.json()
                artifacts = data.get("artifacts", [])

                if not artifacts:
                    return GenerationResult(
                        success=False,
                        error="No images returned from Stability AI",
                    )

                # Get the first image (base64 encoded)
                import base64

                image_b64 = artifacts[0].get("base64")
                if not image_b64:
                    return GenerationResult(
                        success=False,
                        error="No image data in response",
                    )

                image_data = base64.b64decode(image_b64)

                return GenerationResult(
                    success=True,
                    image_data=image_data,
                    metadata={
                        "engine": self.engine,
                        "size": size,
                        "quality": quality,
                        "steps": steps,
                        "cfg_scale": payload["cfg_scale"],
                        "finish_reason": artifacts[0].get("finishReason"),
                    },
                )

        except Exception as e:
            return GenerationResult(
                success=False,
                error=f"Stability AI generation failed: {str(e)}",
            )
