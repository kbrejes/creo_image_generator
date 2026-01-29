"""Image generation tool endpoint."""

from backends import DallE3Backend, FluxBackend, StabilityBackend, IdeogramBackend
from backends.base import ImageBackend
from config import get_settings
from services.storage import get_storage_service


def get_backend(backend_name: str | None) -> ImageBackend | None:
    """Get the appropriate backend instance."""
    settings = get_settings()

    backend_map = {
        "dalle3": (DallE3Backend, settings.openai_api_key),
        "flux": (FluxBackend, settings.replicate_api_token),
        "sdxl": (FluxBackend, settings.replicate_api_token),  # Uses Replicate too
        "stability": (StabilityBackend, settings.stability_api_key),
        "ideogram": (IdeogramBackend, settings.ideogram_api_key),
    }

    if backend_name:
        backend_info = backend_map.get(backend_name.lower())
        if backend_info and backend_info[1]:  # Check if API key exists
            backend_class, _ = backend_info
            return backend_class()
        return None

    # Auto-select best available backend
    # Priority: dalle3 > ideogram > flux > stability
    priority_order = ["dalle3", "ideogram", "flux", "stability"]
    for name in priority_order:
        backend_info = backend_map.get(name)
        if backend_info and backend_info[1]:
            backend_class, _ = backend_info
            return backend_class()

    return None


async def generate_image(
    prompt: str,
    backend: str | None = None,
    size: str = "1024x1024",
    style: str | None = None,
    quality: str = "standard",
    num_images: int = 1,
    negative_prompt: str | None = None,
) -> dict:
    """
    Generate images using the specified or best available backend.

    Args:
        prompt: The image generation prompt
        backend: Specific backend to use (dalle3, flux, sdxl, stability, ideogram)
        size: Image size (e.g., "1024x1024")
        style: Style preset (backend-specific)
        quality: Quality level (standard, hd)
        num_images: Number of images to generate (1-4)
        negative_prompt: What to avoid in the image

    Returns:
        Dict with success status, generated images, and metadata
    """
    # Get the backend
    image_backend = get_backend(backend)

    if not image_backend:
        available = get_settings().get_available_image_backends()
        return {
            "success": False,
            "images": [],
            "error": f"No image backend available. Requested: {backend}. "
            f"Available: {available if available else 'None (configure API keys)'}",
            "metadata": {},
        }

    storage = get_storage_service()
    images = []
    errors = []

    # Generate requested number of images
    for i in range(num_images):
        result = await image_backend.generate(
            prompt=prompt,
            size=size,
            quality=quality,
            style=style,
            negative_prompt=negative_prompt,
        )

        if result.success and result.image_data:
            # Save the image
            filename, url = await storage.save(
                data=result.image_data,
                content_type="image/png",
                folder="generated",
            )

            images.append(
                {
                    "url": url,
                    "filename": filename,
                    "backend": image_backend.name,
                    "revised_prompt": result.revised_prompt,
                }
            )
        else:
            errors.append(result.error or "Unknown error")

    # Build response
    success = len(images) > 0

    return {
        "success": success,
        "images": images,
        "error": "; ".join(errors) if errors and not success else None,
        "metadata": {
            "backend_used": image_backend.name,
            "requested_size": size,
            "requested_quality": quality,
            "total_generated": len(images),
            "total_failed": len(errors),
        },
    }


async def compare_backends(
    prompt: str,
    backends: list[str] | None = None,
    size: str = "1024x1024",
    quality: str = "standard",
) -> dict:
    """
    Generate the same image with multiple backends for comparison.

    Args:
        prompt: The image generation prompt
        backends: List of backends to use (uses all available if not specified)
        size: Image size
        quality: Quality level

    Returns:
        Dict with results from each backend
    """
    settings = get_settings()
    available = settings.get_available_image_backends()

    if backends:
        # Filter to only available backends
        backends_to_use = [b for b in backends if b in available]
    else:
        backends_to_use = available

    if not backends_to_use:
        return {
            "success": False,
            "comparisons": [],
            "error": "No backends available for comparison",
        }

    comparisons = []

    for backend_name in backends_to_use:
        result = await generate_image(
            prompt=prompt,
            backend=backend_name,
            size=size,
            quality=quality,
            num_images=1,
        )

        comparisons.append(
            {
                "backend": backend_name,
                "success": result["success"],
                "image": result["images"][0] if result["images"] else None,
                "error": result.get("error"),
            }
        )

    return {
        "success": any(c["success"] for c in comparisons),
        "comparisons": comparisons,
        "metadata": {
            "backends_tested": backends_to_use,
            "successful_backends": [c["backend"] for c in comparisons if c["success"]],
        },
    }
