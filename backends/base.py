"""Abstract base class for image generation backends."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class GenerationResult:
    """Result of an image generation request."""

    success: bool
    image_data: bytes | None = None  # Raw image bytes
    image_url: str | None = None  # URL if backend returns URL directly
    revised_prompt: str | None = None  # Prompt as modified by the backend
    error: str | None = None
    metadata: dict = field(default_factory=dict)


class ImageBackend(ABC):
    """Abstract base class for image generation backends."""

    # Backend identifier
    name: str = "base"

    # Human-readable display name
    display_name: str = "Base Backend"

    # Supported features
    supports_negative_prompt: bool = False
    supports_image_to_image: bool = False
    supports_inpainting: bool = False

    # Default and supported sizes
    default_size: str = "1024x1024"
    supported_sizes: list[str] = ["1024x1024"]

    # Quality options
    supported_qualities: list[str] = ["standard"]

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str | None = None,
        negative_prompt: str | None = None,
        **kwargs,
    ) -> GenerationResult:
        """
        Generate an image from a prompt.

        Args:
            prompt: The text prompt describing the image
            size: Image size in format WxH
            quality: Quality level (backend-specific)
            style: Style preset (backend-specific)
            negative_prompt: What to avoid (if supported)
            **kwargs: Additional backend-specific parameters

        Returns:
            GenerationResult with image data or error
        """
        pass

    def validate_size(self, size: str) -> str:
        """Validate and normalize size, returning closest supported size."""
        if size in self.supported_sizes:
            return size
        # Return default if not supported
        return self.default_size

    def get_capabilities(self) -> dict:
        """Return backend capabilities for discovery."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "supports_negative_prompt": self.supports_negative_prompt,
            "supports_image_to_image": self.supports_image_to_image,
            "supports_inpainting": self.supports_inpainting,
            "supported_sizes": self.supported_sizes,
            "supported_qualities": self.supported_qualities,
            "default_size": self.default_size,
        }
