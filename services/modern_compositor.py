"""Modern image compositor using pictex for professional text effects."""

import io
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import httpx
from PIL import Image as PILImage

from pictex import Canvas, Row, Column, Text, Shadow, LinearGradient, Image as PictexImage

from services.storage import get_storage_service


class DesignPreset(str, Enum):
    """Available design presets for ad creatives."""
    NEON = "neon"           # Glowing neon text on dark background
    MINIMAL = "minimal"     # Clean, minimal with subtle shadows
    GRADIENT = "gradient"   # Gradient background with shadowed text
    BOLD = "bold"           # Bold colors, high contrast
    GLASSMORPHISM = "glass" # Frosted glass effect (semi-transparent)


@dataclass
class ColorScheme:
    """Color scheme for a design preset."""
    background: str | list[str]  # Solid color or gradient colors
    hook_color: str
    body_color: str
    cta_bg: str | list[str]
    cta_text: str
    glow_color: Optional[str] = None
    stroke_color: Optional[str] = None


# Preset color schemes
PRESET_SCHEMES = {
    DesignPreset.NEON: ColorScheme(
        background="#0f0c29",
        hook_color="#ffffff",
        body_color="#e0e0e0",
        cta_bg=["#f72585", "#7209b7"],
        cta_text="#ffffff",
        glow_color="#f72585",
    ),
    DesignPreset.MINIMAL: ColorScheme(
        background="#ffffff",
        hook_color="#1a1a2e",
        body_color="#4a4a5a",
        cta_bg="#1a1a2e",
        cta_text="#ffffff",
    ),
    DesignPreset.GRADIENT: ColorScheme(
        background=["#667eea", "#764ba2"],
        hook_color="#ffffff",
        body_color="#f0f0f0",
        cta_bg=["#ff6b6b", "#ee5a5a"],
        cta_text="#ffffff",
    ),
    DesignPreset.BOLD: ColorScheme(
        background="#1e1e2f",
        hook_color="#ffffff",
        body_color="#cccccc",
        cta_bg="#ff5722",
        cta_text="#ffffff",
        stroke_color="#ff5722",
    ),
    DesignPreset.GLASSMORPHISM: ColorScheme(
        background=["#1a1a2e", "#16213e"],
        hook_color="#ffffff",
        body_color="#e0e0e0",
        cta_bg=["#ffffff33", "#ffffff22"],  # Semi-transparent
        cta_text="#ffffff",
    ),
}

# Output sizes (same as original compositor)
SIZES = {
    "instagram_square": (1080, 1080),
    "instagram_story": (1080, 1920),
    "instagram_reels": (1080, 1920),
    "instagram_portrait": (1080, 1350),
    "facebook_feed": (1200, 628),
    "telegram": (1280, 720),
    "tiktok": (1080, 1920),
    "youtube_thumbnail": (1280, 720),
}


class ModernCompositor:
    """Creates professional ad creatives with modern text effects using pictex."""

    def __init__(self, font_path: Optional[str] = None):
        """Initialize compositor with optional custom font."""
        self.font_path = font_path
        self.storage = get_storage_service()

    def _get_background(self, colors: str | list[str], width: int, height: int):
        """Create background - solid color or gradient."""
        if isinstance(colors, list) and len(colors) > 1:
            # LinearGradient uses normalized coordinates (0-1)
            return LinearGradient(colors, start_point=(0.5, 0), end_point=(0.5, 1))
        return colors if isinstance(colors, str) else colors[0]

    def _create_hook(
        self,
        text: str,
        scheme: ColorScheme,
        font_size: int = 54,
    ) -> Text:
        """Create hook text with appropriate effects."""
        hook = Text(text).font_size(font_size).color(scheme.hook_color)

        # Add glow effect if specified
        if scheme.glow_color:
            hook = hook.text_shadows(
                Shadow(offset=(0, 0), blur_radius=10, color=scheme.glow_color),
                Shadow(offset=(0, 0), blur_radius=30, color=scheme.glow_color + "80"),
            )
        # Add stroke if specified
        elif scheme.stroke_color:
            hook = hook.text_stroke(3, scheme.stroke_color)
        else:
            # Default subtle shadow
            hook = hook.text_shadows(
                Shadow(offset=(2, 2), blur_radius=8, color="#00000066")
            )

        return hook

    def _create_body(
        self,
        text: str,
        scheme: ColorScheme,
        font_size: int = 36,
    ) -> Text:
        """Create body text with subtle shadow."""
        return (
            Text(text)
            .font_size(font_size)
            .color(scheme.body_color)
            .text_shadows(Shadow(offset=(1, 1), blur_radius=4, color="#00000044"))
        )

    def _create_cta(
        self,
        text: str,
        scheme: ColorScheme,
        font_size: int = 34,
    ) -> Text:
        """Create CTA button with pill shape."""
        cta_bg = self._get_background(scheme.cta_bg, 300, 60)

        return (
            Text(text)
            .font_size(font_size)
            .color(scheme.cta_text)
            .padding(22, 45)
            .background_color(cta_bg)
            .border_radius(40)
        )

    def compose(
        self,
        hook_text: str,
        body_text: str,
        cta_text: str,
        preset: DesignPreset = DesignPreset.NEON,
        output_size: str = "instagram_square",
        background_image_url: Optional[str] = None,
        custom_colors: Optional[ColorScheme] = None,
    ) -> bytes:
        """
        Compose an ad creative with modern text effects.

        Args:
            hook_text: Main headline/hook text
            body_text: Body/description text
            cta_text: Call-to-action button text
            preset: Design preset to use
            output_size: Output size preset name
            background_image_url: Optional background image URL
            custom_colors: Optional custom color scheme

        Returns:
            PNG image bytes
        """
        # Get dimensions
        width, height = SIZES.get(output_size, (1080, 1080))

        # Get color scheme
        scheme = custom_colors or PRESET_SCHEMES[preset]

        # Calculate font sizes based on dimensions
        base_size = min(width, height)
        hook_size = int(base_size * 0.05)  # ~54px for 1080
        body_size = int(base_size * 0.033)  # ~36px for 1080
        cta_size = int(base_size * 0.031)   # ~34px for 1080

        # Create text elements
        hook = self._create_hook(hook_text, scheme, hook_size)
        body = self._create_body(body_text, scheme, body_size)
        cta = self._create_cta(cta_text, scheme, cta_size)

        # Create content layout - full size, centered
        padding = int(base_size * 0.08)
        content = (
            Column(hook, body, cta)
            .size(width, height)
            .align_items("center")
            .justify_content("center")
            .gap(30)
            .padding(padding)
        )

        # Create canvas
        canvas = Canvas().size(width, height)

        # Apply font if specified
        if self.font_path:
            canvas = canvas.font_family(self.font_path)

        # Apply background
        if background_image_url:
            # TODO: Support background images with pictex
            # For now, use gradient/solid
            canvas = canvas.background_color(
                self._get_background(scheme.background, width, height)
            )
        else:
            canvas = canvas.background_color(
                self._get_background(scheme.background, width, height)
            )

        # Render
        image = canvas.render(content)

        # Convert to bytes via PIL
        buffer = io.BytesIO()
        image.to_pillow().save(buffer, format="PNG")
        return buffer.getvalue()

    async def compose_and_upload(
        self,
        hook_text: str,
        body_text: str,
        cta_text: str,
        preset: DesignPreset = DesignPreset.NEON,
        output_size: str = "instagram_square",
        background_image_url: Optional[str] = None,
    ) -> str:
        """Compose ad and upload to storage, returning URL."""
        image_bytes = self.compose(
            hook_text=hook_text,
            body_text=body_text,
            cta_text=cta_text,
            preset=preset,
            output_size=output_size,
            background_image_url=background_image_url,
        )

        # Upload
        _, url = await self.storage.save(image_bytes)
        return url

    def compose_with_image_overlay(
        self,
        hook_text: str,
        body_text: str,
        cta_text: str,
        background_image_url: str,
        preset: DesignPreset = DesignPreset.NEON,
        output_size: str = "instagram_square",
        darken: float = 0.5,
    ) -> bytes:
        """
        Compose ad with background image and darkening overlay.

        This uses PIL to handle the background image, then pictex for text.
        """
        width, height = SIZES.get(output_size, (1080, 1080))
        scheme = PRESET_SCHEMES[preset]

        # Download and prepare background image
        # Convert external URL to internal when running in Docker (avoid going through proxy)
        download_url = background_image_url
        if "creo.yourads.io" in background_image_url:
            download_url = background_image_url.replace(
                "https://creo.yourads.io", "http://localhost:8000"
            )
        response = httpx.get(download_url, timeout=60, follow_redirects=True)
        bg_image = PILImage.open(io.BytesIO(response.content)).convert("RGBA")

        # Resize and crop to fit
        bg_image = self._resize_and_crop(bg_image, width, height)

        # Apply darkening overlay
        if darken > 0:
            overlay = PILImage.new("RGBA", (width, height), (0, 0, 0, int(255 * darken)))
            bg_image = PILImage.alpha_composite(bg_image, overlay)

        # Convert background to bytes
        bg_buffer = io.BytesIO()
        bg_image.save(bg_buffer, format="PNG")
        bg_bytes = bg_buffer.getvalue()

        # Create text overlay with pictex (transparent background)
        base_size = min(width, height)
        hook_size = int(base_size * 0.05)
        body_size = int(base_size * 0.033)
        cta_size = int(base_size * 0.031)

        # For image overlays, always use white text with glow
        hook = (
            Text(hook_text)
            .font_size(hook_size)
            .color("#ffffff")
            .text_shadows(
                Shadow(offset=(0, 0), blur_radius=15, color="#00000088"),
                Shadow(offset=(2, 4), blur_radius=8, color="#000000aa"),
            )
        )

        body = (
            Text(body_text)
            .font_size(body_size)
            .color("#f0f0f0")
            .text_shadows(Shadow(offset=(2, 2), blur_radius=6, color="#000000aa"))
        )

        cta = (
            Text(cta_text)
            .font_size(cta_size)
            .color("#ffffff")
            .padding(22, 45)
            .background_color(self._get_background(scheme.cta_bg, 300, 60))
            .border_radius(40)
        )

        # Center the content like in compose()
        padding = int(base_size * 0.08)
        content = (
            Column(hook, body, cta)
            .size(width, height)
            .align_items("center")
            .justify_content("center")
            .gap(30)
            .padding(padding)
        )

        # Render text on transparent background
        text_canvas = Canvas().size(width, height)
        if self.font_path:
            text_canvas = text_canvas.font_family(self.font_path)

        text_image = text_canvas.render(content)

        # Convert pictex image to PIL
        text_pil = text_image.to_pillow().convert("RGBA")

        # Composite text over background
        final = PILImage.alpha_composite(bg_image, text_pil)

        # Convert to bytes
        output_buffer = io.BytesIO()
        final.save(output_buffer, format="PNG")
        return output_buffer.getvalue()

    def _resize_and_crop(
        self,
        image: PILImage.Image,
        target_width: int,
        target_height: int,
    ) -> PILImage.Image:
        """Resize and center-crop image to target dimensions."""
        img_width, img_height = image.size
        target_ratio = target_width / target_height
        img_ratio = img_width / img_height

        if img_ratio > target_ratio:
            # Image is wider - fit height, crop width
            new_height = target_height
            new_width = int(img_width * (target_height / img_height))
        else:
            # Image is taller - fit width, crop height
            new_width = target_width
            new_height = int(img_height * (target_width / img_width))

        image = image.resize((new_width, new_height), PILImage.Resampling.LANCZOS)

        # Center crop
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height

        return image.crop((left, top, right, bottom))


# Convenience function
def create_modern_ad(
    hook: str,
    body: str,
    cta: str,
    preset: str = "neon",
    size: str = "instagram_square",
) -> bytes:
    """Quick function to create a modern ad creative."""
    compositor = ModernCompositor()
    return compositor.compose(
        hook_text=hook,
        body_text=body,
        cta_text=cta,
        preset=DesignPreset(preset),
        output_size=size,
    )
