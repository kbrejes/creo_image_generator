"""Flux image generation backend via Replicate API."""

import httpx
import replicate

from backends.base import ImageBackend, GenerationResult
from config import get_settings


class FluxBackend(ImageBackend):
    """Flux image generation backend via Replicate."""

    name = "flux"
    display_name = "Flux (via Replicate)"
    supports_negative_prompt = True
    supports_image_to_image = True
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

    # Flux model versions on Replicate
    MODELS = {
        "schnell": "black-forest-labs/flux-schnell",  # Fast
        "dev": "black-forest-labs/flux-dev",  # Higher quality
        "pro": "black-forest-labs/flux-1.1-pro",  # Best quality
    }

    def __init__(self, model_variant: str = "schnell"):
        settings = get_settings()
        self.api_token = settings.replicate_api_token
        self.model_variant = model_variant
        self.model = self.MODELS.get(model_variant, self.MODELS["schnell"])

    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str | None = None,
        negative_prompt: str | None = None,
        **kwargs,
    ) -> GenerationResult:
        """Generate an image using Flux via Replicate."""
        try:
            # Parse size
            size = self.validate_size(size)
            width, height = map(int, size.split("x"))

            # Select model based on quality
            model = self.model
            if quality == "high" and self.model_variant == "schnell":
                model = self.MODELS["dev"]

            # Build input parameters
            input_params = {
                "prompt": prompt,
                "num_outputs": 1,
                "output_format": "png",
                "aspect_ratio": self._get_aspect_ratio(width, height),
            }

            # Flux Schnell has different parameters than dev/pro
            is_schnell = "schnell" in model

            if not is_schnell:
                # Only dev/pro support these parameters
                if negative_prompt:
                    input_params["negative_prompt"] = negative_prompt
                input_params["guidance_scale"] = kwargs.get("guidance_scale", 7.5)
                input_params["num_inference_steps"] = kwargs.get(
                    "num_inference_steps", 28
                )

            # Run the model
            client = replicate.Client(api_token=self.api_token)
            output = client.run(model, input=input_params)

            # Output is typically a list of URLs
            if isinstance(output, list):
                image_url = str(output[0])
            else:
                image_url = str(output)

            # Download the image
            async with httpx.AsyncClient() as http_client:
                img_response = await http_client.get(image_url)
                img_response.raise_for_status()
                image_data = img_response.content

            return GenerationResult(
                success=True,
                image_data=image_data,
                image_url=image_url,
                metadata={
                    "model": model,
                    "size": size,
                    "quality": quality,
                    "guidance_scale": input_params.get("guidance_scale"),
                    "num_inference_steps": input_params.get("num_inference_steps"),
                },
            )

        except Exception as e:
            return GenerationResult(
                success=False,
                error=f"Flux generation failed: {str(e)}",
            )

    def _get_aspect_ratio(self, width: int, height: int) -> str:
        """Convert width/height to Flux aspect ratio string."""
        ratio = width / height

        # Map to supported aspect ratios
        aspect_ratios = {
            1.0: "1:1",
            1.78: "16:9",
            0.56: "9:16",
            1.33: "4:3",
            0.75: "3:4",
            2.33: "21:9",
            0.43: "9:21",
            1.5: "3:2",
            0.67: "2:3",
        }

        # Find closest match
        closest_ratio = min(aspect_ratios.keys(), key=lambda x: abs(x - ratio))
        return aspect_ratios[closest_ratio]
