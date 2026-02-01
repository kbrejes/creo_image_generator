"""Modern image compositor using pictex for professional text effects."""

import io
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Literal
from PIL import Image as PILImage, ImageDraw

from pictex import Canvas, Row, Column, Text, Shadow, LinearGradient, Image as PictexImage

from services.storage import get_storage_service


class DesignPreset(str, Enum):
    """Available design presets for ad creatives."""
    NEON = "neon"           # Glowing neon text on dark background
    MINIMAL = "minimal"     # Clean, minimal with subtle shadows
    GRADIENT = "gradient"   # Gradient background with shadowed text
    BOLD = "bold"           # Bold colors, high contrast
    GLASSMORPHISM = "glass" # Frosted glass effect (semi-transparent)


class TextPosition(str, Enum):
    """Text positioning presets based on rule of thirds."""
    CENTER = "center"           # Traditional centered layout
    TOP_HEAVY = "top_heavy"     # Hook at top, body middle, CTA bottom
    BOTTOM_HEAVY = "bottom_heavy"  # Content weighted toward bottom
    LEFT_ALIGNED = "left_aligned"  # Left-aligned text
    RULE_OF_THIRDS = "rule_of_thirds"  # Classic rule of thirds


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


@dataclass
class SafeZone:
    """Safe zone margins for a format (in pixels)."""
    top: int
    bottom: int
    left: int
    right: int


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

# Output sizes with safe zones
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

# Safe zones per format (top, bottom, left, right in pixels)
SAFE_ZONES = {
    "instagram_square": SafeZone(top=60, bottom=60, left=60, right=60),
    "instagram_story": SafeZone(top=250, bottom=250, left=60, right=60),
    "instagram_reels": SafeZone(top=270, bottom=670, left=65, right=120),
    "instagram_portrait": SafeZone(top=80, bottom=80, left=60, right=60),
    "facebook_feed": SafeZone(top=40, bottom=40, left=60, right=60),
    "telegram": SafeZone(top=40, bottom=40, left=60, right=60),
    "tiktok": SafeZone(top=270, bottom=670, left=65, right=120),
    "youtube_thumbnail": SafeZone(top=40, bottom=40, left=60, right=60),
}

# Available fonts with Cyrillic support (Google Fonts names)
# These need to be installed on the system or downloaded
FONTS = {
    # Bold Display Fonts (Headlines)
    "montserrat": {
        "name": "Montserrat",
        "file": "Montserrat-Bold.ttf",
        "style": "geometric",
        "weight": "bold",
        "cyrillic": True,
    },
    "oswald": {
        "name": "Oswald",
        "file": "Oswald-Bold.ttf",
        "style": "condensed",
        "weight": "bold",
        "cyrillic": True,
    },
    "rubik": {
        "name": "Rubik",
        "file": "Rubik-Bold.ttf",
        "style": "rounded",
        "weight": "bold",
        "cyrillic": True,
    },
    "inter": {
        "name": "Inter",
        "file": "Inter-Bold.ttf",
        "style": "clean",
        "weight": "bold",
        "cyrillic": True,
    },
    "raleway": {
        "name": "Raleway",
        "file": "Raleway-Bold.ttf",
        "style": "elegant",
        "weight": "bold",
        "cyrillic": True,
    },
    "pt_sans": {
        "name": "PT Sans",
        "file": "PTSans-Bold.ttf",
        "style": "humanist",
        "weight": "bold",
        "cyrillic": True,
    },
    "roboto": {
        "name": "Roboto",
        "file": "Roboto-Bold.ttf",
        "style": "neutral",
        "weight": "bold",
        "cyrillic": True,
    },
    "open_sans": {
        "name": "Open Sans",
        "file": "OpenSans-Bold.ttf",
        "style": "neutral",
        "weight": "bold",
        "cyrillic": True,
    },
    "nunito": {
        "name": "Nunito",
        "file": "Nunito-Bold.ttf",
        "style": "rounded",
        "weight": "bold",
        "cyrillic": True,
    },
    "comfortaa": {
        "name": "Comfortaa",
        "file": "Comfortaa-Bold.ttf",
        "style": "rounded",
        "weight": "bold",
        "cyrillic": True,
    },
    # Condensed/Impact Fonts
    "anton": {
        "name": "Anton",
        "file": "Anton-Regular.ttf",
        "style": "impact",
        "weight": "black",
        "cyrillic": True,
    },
    "russo_one": {
        "name": "Russo One",
        "file": "RussoOne-Regular.ttf",
        "style": "sporty",
        "weight": "bold",
        "cyrillic": True,
    },
    "jost": {
        "name": "Jost",
        "file": "Jost-Bold.ttf",
        "style": "geometric",
        "weight": "bold",
        "cyrillic": True,
    },
    "manrope": {
        "name": "Manrope",
        "file": "Manrope-Bold.ttf",
        "style": "modern",
        "weight": "bold",
        "cyrillic": True,
    },
    "bebas_neue": {
        "name": "Bebas Neue",
        "file": "BebasNeue-Regular.ttf",
        "style": "display",
        "weight": "bold",
        "cyrillic": False,  # Limited Cyrillic
    },
    # Clean/Minimal Fonts
    "fira_sans": {
        "name": "Fira Sans",
        "file": "FiraSans-Bold.ttf",
        "style": "technical",
        "weight": "bold",
        "cyrillic": True,
    },
    "source_sans": {
        "name": "Source Sans 3",
        "file": "SourceSans3-Bold.ttf",
        "style": "clean",
        "weight": "bold",
        "cyrillic": True,
    },
    "ibm_plex": {
        "name": "IBM Plex Sans",
        "file": "IBMPlexSans-Bold.ttf",
        "style": "corporate",
        "weight": "bold",
        "cyrillic": True,
    },
    "exo2": {
        "name": "Exo 2",
        "file": "Exo2-Bold.ttf",
        "style": "futuristic",
        "weight": "bold",
        "cyrillic": True,
    },
    "play": {
        "name": "Play",
        "file": "Play-Bold.ttf",
        "style": "gaming",
        "weight": "bold",
        "cyrillic": True,
    },
}

# Font size ratios using Golden Ratio (1.618)
GOLDEN_RATIO = 1.618
FONT_SIZE_RATIOS = {
    "hook": 1.0,           # Base size (largest)
    "body": 1 / GOLDEN_RATIO,  # ~0.618 of hook
    "cta": 1 / GOLDEN_RATIO * 0.9,  # Slightly smaller than body
}


class ModernCompositor:
    """Creates professional ad creatives with modern text effects using pictex."""

    def __init__(self, font_path: Optional[str] = None):
        """Initialize compositor with optional custom font."""
        self.font_path = font_path
        self.storage = get_storage_service()

    def _get_font_path(self, font_name: str) -> Optional[str]:
        """Get font file path for a font name."""
        if font_name in FONTS:
            # TODO: Implement font file resolution
            # For now, return None to use default font
            return None
        return None

    def _get_background(self, colors: str | list[str], width: int, height: int):
        """Create background - solid color or gradient."""
        if isinstance(colors, list) and len(colors) > 1:
            return LinearGradient(colors, start_point=(0.5, 0), end_point=(0.5, 1))
        return colors if isinstance(colors, str) else colors[0]

    def _calculate_font_sizes(
        self,
        width: int,
        height: int,
        output_size: str,
    ) -> dict[str, int]:
        """
        Calculate font sizes based on canvas dimensions and format.

        Uses golden ratio hierarchy:
        - Hook: largest, attention-grabbing
        - Body: ~0.618x hook size
        - CTA: slightly smaller than body
        """
        base_dimension = min(width, height)

        # Base hook size as percentage of smallest dimension
        # Larger for vertical formats, smaller for horizontal
        aspect_ratio = height / width

        if aspect_ratio > 1.5:  # Vertical (Story, Reels)
            base_percentage = 0.055  # Larger text for vertical
        elif aspect_ratio < 0.7:  # Horizontal (YouTube, Telegram)
            base_percentage = 0.065  # Compensate for smaller height
        else:  # Square or near-square
            base_percentage = 0.05

        hook_size = int(base_dimension * base_percentage)

        return {
            "hook": max(36, hook_size),  # Minimum 36px
            "body": max(20, int(hook_size * FONT_SIZE_RATIOS["body"])),
            "cta": max(18, int(hook_size * FONT_SIZE_RATIOS["cta"])),
        }

    def _get_safe_content_area(
        self,
        width: int,
        height: int,
        output_size: str,
    ) -> tuple[int, int, int, int]:
        """
        Get safe content area (x, y, width, height) within safe zones.
        """
        safe_zone = SAFE_ZONES.get(output_size, SafeZone(60, 60, 60, 60))

        content_x = safe_zone.left
        content_y = safe_zone.top
        content_width = width - safe_zone.left - safe_zone.right
        content_height = height - safe_zone.top - safe_zone.bottom

        return content_x, content_y, content_width, content_height

    def _create_hook(
        self,
        text: str,
        scheme: ColorScheme,
        font_size: int,
        max_width: int,
    ) -> Text:
        """Create hook text with appropriate effects."""
        hook = (
            Text(text)
            .font_size(font_size)
            .color(scheme.hook_color)
        )

        # Add glow effect if specified
        if scheme.glow_color:
            hook = hook.text_shadows(
                Shadow(offset=(0, 0), blur_radius=15, color=scheme.glow_color),
                Shadow(offset=(0, 0), blur_radius=40, color=scheme.glow_color + "60"),
            )
        elif scheme.stroke_color:
            hook = hook.text_stroke(3, scheme.stroke_color)
        else:
            # Default shadow for depth
            hook = hook.text_shadows(
                Shadow(offset=(0, 4), blur_radius=12, color="#00000055")
            )

        return hook

    def _create_body(
        self,
        text: str,
        scheme: ColorScheme,
        font_size: int,
        max_width: int,
    ) -> Text:
        """Create body text with subtle shadow."""
        return (
            Text(text)
            .font_size(font_size)
            .color(scheme.body_color)
            .text_shadows(Shadow(offset=(0, 2), blur_radius=6, color="#00000044"))
        )

    def _create_cta(
        self,
        text: str,
        scheme: ColorScheme,
        font_size: int,
    ) -> Text:
        """Create CTA button with pill shape."""
        cta_bg = self._get_background(scheme.cta_bg, 300, 60)

        # Calculate padding based on font size
        v_padding = max(16, int(font_size * 0.6))
        h_padding = max(32, int(font_size * 1.3))

        return (
            Text(text)
            .font_size(font_size)
            .color(scheme.cta_text)
                        .padding(v_padding, h_padding)
            .background_color(cta_bg)
            .border_radius(50)  # Pill shape
            .text_shadows(Shadow(offset=(0, 2), blur_radius=4, color="#00000033"))
        )

    def _create_floor_fade(
        self,
        width: int,
        height: int,
        intensity: float = 0.7,
    ) -> PILImage.Image:
        """
        Create a gradient overlay that darkens toward the bottom.
        This is the "floor fade" technique for text readability.
        """
        gradient = PILImage.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)

        # Start gradient from middle of image
        start_y = int(height * 0.3)

        for y in range(start_y, height):
            # Calculate opacity: 0 at start_y, increasing toward bottom
            progress = (y - start_y) / (height - start_y)
            alpha = int(255 * intensity * progress)
            draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))

        return gradient

    def compose(
        self,
        hook_text: str,
        body_text: str,
        cta_text: str,
        preset: DesignPreset = DesignPreset.NEON,
        output_size: str = "instagram_square",
        background_image_url: Optional[str] = None,
        custom_colors: Optional[ColorScheme] = None,
        font_name: str = "inter",
        text_position: TextPosition = TextPosition.CENTER,
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
            font_name: Font to use (from FONTS dict)
            text_position: Text positioning preset

        Returns:
            PNG image bytes
        """
        width, height = SIZES.get(output_size, (1080, 1080))
        scheme = custom_colors or PRESET_SCHEMES[preset]

        # Calculate font sizes using golden ratio
        font_sizes = self._calculate_font_sizes(width, height, output_size)

        # Get safe content area
        content_x, content_y, content_width, content_height = \
            self._get_safe_content_area(width, height, output_size)

        # Create text elements
        hook = self._create_hook(hook_text, scheme, font_sizes["hook"], content_width)
        body = self._create_body(body_text, scheme, font_sizes["body"], content_width)
        cta = self._create_cta(cta_text, scheme, font_sizes["cta"])

        # Calculate gaps based on content height
        gap = max(20, int(content_height * 0.03))

        # Determine vertical positioning based on text_position
        if text_position == TextPosition.TOP_HEAVY:
            justify = "start"
            top_padding = int(content_height * 0.1)
        elif text_position == TextPosition.BOTTOM_HEAVY:
            justify = "end"
            top_padding = 0
        else:
            justify = "center"
            top_padding = 0

        # Create content layout within safe area
        content = (
            Column(hook, body, cta)
            .size(content_width, content_height)
            .align_items("center")
            .justify_content(justify)
            .gap(gap)
            .padding(top_padding, 0, 0, 0)
        )

        # Create positioned container (offset by safe zone)
        positioned_content = (
            Column(content)
            .size(width, height)
            .padding(content_y, content_x, content_y, content_x)
        )

        # Create canvas
        canvas = Canvas().size(width, height)

        # Apply font
        font_path = self._get_font_path(font_name) or self.font_path
        if font_path:
            canvas = canvas.font_family(font_path)

        # Apply background
        canvas = canvas.background_color(
            self._get_background(scheme.background, width, height)
        )

        # Render
        image = canvas.render(positioned_content)

        # Convert to bytes
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
        font_name: str = "inter",
        text_position: TextPosition = TextPosition.CENTER,
    ) -> str:
        """Compose ad and upload to storage, returning URL."""
        image_bytes = self.compose(
            hook_text=hook_text,
            body_text=body_text,
            cta_text=cta_text,
            preset=preset,
            output_size=output_size,
            background_image_url=background_image_url,
            font_name=font_name,
            text_position=text_position,
        )

        _, url = await self.storage.save(image_bytes)
        return url

    def compose_with_image_overlay(
        self,
        hook_text: str,
        body_text: str,
        cta_text: str,
        background_image_bytes: bytes,
        preset: DesignPreset = DesignPreset.NEON,
        output_size: str = "instagram_square",
        darken: float = 0.5,
        use_floor_fade: bool = True,
        font_name: str = "inter",
        text_position: TextPosition = TextPosition.CENTER,
    ) -> bytes:
        """
        Compose ad with background image and darkening overlay.

        Uses floor fade technique for better text readability.

        Args:
            background_image_bytes: Pre-fetched image bytes
            darken: Overall darkening (0-1)
            use_floor_fade: Apply gradient fade toward bottom
            font_name: Font to use
            text_position: Text positioning preset
        """
        width, height = SIZES.get(output_size, (1080, 1080))
        scheme = PRESET_SCHEMES[preset]

        # Open and prepare background image
        bg_image = PILImage.open(io.BytesIO(background_image_bytes)).convert("RGBA")
        bg_image = self._resize_and_crop(bg_image, width, height)

        # Apply floor fade gradient (more natural than uniform darkening)
        if use_floor_fade:
            floor_fade = self._create_floor_fade(width, height, intensity=0.7)
            bg_image = PILImage.alpha_composite(bg_image, floor_fade)

        # Apply additional uniform darkening if needed
        if darken > 0:
            overlay = PILImage.new("RGBA", (width, height), (0, 0, 0, int(255 * darken * 0.5)))
            bg_image = PILImage.alpha_composite(bg_image, overlay)

        # Calculate font sizes
        font_sizes = self._calculate_font_sizes(width, height, output_size)

        # Get safe content area
        content_x, content_y, content_width, content_height = \
            self._get_safe_content_area(width, height, output_size)

        # For image overlays, always use white text with strong shadows
        hook = (
            Text(hook_text)
            .font_size(font_sizes["hook"])
            .color("#ffffff")
                        .text_shadows(
                Shadow(offset=(0, 0), blur_radius=20, color="#000000aa"),
                Shadow(offset=(0, 4), blur_radius=10, color="#000000cc"),
            )
        )

        body = (
            Text(body_text)
            .font_size(font_sizes["body"])
            .color("#f5f5f5")
            .text_shadows(
                Shadow(offset=(0, 0), blur_radius=12, color="#00000088"),
                Shadow(offset=(0, 2), blur_radius=6, color="#000000aa"),
            )
        )

        # CTA with preset colors
        cta_bg = self._get_background(scheme.cta_bg, 300, 60)
        v_padding = max(16, int(font_sizes["cta"] * 0.6))
        h_padding = max(32, int(font_sizes["cta"] * 1.3))

        cta = (
            Text(cta_text)
            .font_size(font_sizes["cta"])
            .color("#ffffff")
                        .padding(v_padding, h_padding)
            .background_color(cta_bg)
            .border_radius(50)
            .text_shadows(Shadow(offset=(0, 4), blur_radius=8, color="#00000066"))
        )

        # Calculate gaps and positioning
        gap = max(20, int(content_height * 0.03))

        if text_position == TextPosition.TOP_HEAVY:
            justify = "start"
            top_padding = int(content_height * 0.1)
        elif text_position == TextPosition.BOTTOM_HEAVY:
            justify = "end"
            top_padding = 0
        else:
            justify = "center"
            top_padding = 0

        # Create content layout
        content = (
            Column(hook, body, cta)
            .size(content_width, content_height)
            .align_items("center")
            .justify_content(justify)
            .gap(gap)
            .padding(top_padding, 0, 0, 0)
        )

        # Position within safe zones
        positioned_content = (
            Column(content)
            .size(width, height)
            .padding(content_y, content_x, content_y, content_x)
        )

        # Render text on transparent background
        text_canvas = Canvas().size(width, height)

        font_path = self._get_font_path(font_name) or self.font_path
        if font_path:
            text_canvas = text_canvas.font_family(font_path)

        text_image = text_canvas.render(positioned_content)
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
            new_height = target_height
            new_width = int(img_width * (target_height / img_height))
        else:
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
    font: str = "inter",
) -> bytes:
    """Quick function to create a modern ad creative."""
    compositor = ModernCompositor()
    return compositor.compose(
        hook_text=hook,
        body_text=body,
        cta_text=cta,
        preset=DesignPreset(preset),
        output_size=size,
        font_name=font,
    )


def get_available_fonts() -> dict:
    """Return available fonts with their metadata."""
    return FONTS


def get_available_sizes() -> dict:
    """Return available output sizes."""
    return SIZES


def get_safe_zones() -> dict:
    """Return safe zones for all formats."""
    return {k: {"top": v.top, "bottom": v.bottom, "left": v.left, "right": v.right}
            for k, v in SAFE_ZONES.items()}
