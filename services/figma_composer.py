"""Figma composition service - creates ad layouts with images and text.

This service provides the data structures and helpers for composing ads in Figma.
The actual Figma operations are performed via the Figma MCP server.

Workflow:
1. Define ad specifications (size, layout, text, image placement)
2. Generate the Figma design instructions
3. Execute via Figma MCP (done by the AI agent)
"""

from dataclasses import dataclass, field
from enum import Enum


class AdSize(Enum):
    """Standard ad sizes for various platforms."""
    # Instagram
    INSTAGRAM_SQUARE = (1080, 1080)
    INSTAGRAM_PORTRAIT = (1080, 1350)
    INSTAGRAM_STORY = (1080, 1920)

    # Facebook
    FACEBOOK_FEED = (1200, 628)
    FACEBOOK_SQUARE = (1080, 1080)
    FACEBOOK_STORY = (1080, 1920)

    # Twitter/X
    TWITTER_POST = (1200, 675)
    TWITTER_CARD = (800, 418)

    # LinkedIn
    LINKEDIN_POST = (1200, 627)
    LINKEDIN_SQUARE = (1080, 1080)

    # Google Display
    GOOGLE_MEDIUM_RECTANGLE = (300, 250)
    GOOGLE_LEADERBOARD = (728, 90)
    GOOGLE_LARGE_RECTANGLE = (336, 280)

    # Telegram
    TELEGRAM_POST = (1280, 720)

    # Generic
    SQUARE = (1024, 1024)
    LANDSCAPE = (1920, 1080)
    PORTRAIT = (1080, 1920)


@dataclass
class TextElement:
    """Text element specification for Figma."""
    content: str
    role: str  # "headline", "body", "cta", "hook", etc.
    font_size: int = 48
    font_weight: str = "bold"  # "regular", "medium", "bold", "black"
    font_family: str = "Inter"
    color: str = "#000000"
    max_width: int | None = None  # For text wrapping
    position: str = "center"  # "top", "center", "bottom", "custom"
    x: int | None = None  # Custom position
    y: int | None = None
    text_align: str = "center"  # "left", "center", "right"


@dataclass
class ImageElement:
    """Image element specification for Figma."""
    image_url: str  # URL or local path
    position: str = "background"  # "background", "center", "top", "bottom", "custom"
    x: int | None = None
    y: int | None = None
    width: int | None = None  # None = auto/fill
    height: int | None = None
    opacity: float = 1.0
    corner_radius: int = 0


@dataclass
class AdSpec:
    """Complete ad specification."""
    name: str
    size: AdSize
    background_color: str = "#FFFFFF"
    texts: list[TextElement] = field(default_factory=list)
    images: list[ImageElement] = field(default_factory=list)
    padding: int = 40


class FigmaComposer:
    """Generates Figma design instructions from ad specifications."""

    # Meme-style presets
    MEME_STYLE = {
        "background_color": "#FFFFFF",
        "headline_font": "Impact",
        "headline_color": "#000000",
        "headline_size": 64,
        "body_font": "Arial",
        "body_color": "#333333",
    }

    # Professional B2B presets
    B2B_STYLE = {
        "background_color": "#F8F9FA",
        "headline_font": "Inter",
        "headline_color": "#1A1A2E",
        "headline_size": 48,
        "body_font": "Inter",
        "body_color": "#4A4A68",
    }

    def create_meme_ad_spec(
        self,
        size: AdSize,
        image_url: str,
        hook_text: str,
        body_text: str | None = None,
        cta_text: str | None = None,
    ) -> AdSpec:
        """Create a meme-style ad specification."""
        texts = [
            TextElement(
                content=hook_text,
                role="hook",
                font_size=self.MEME_STYLE["headline_size"],
                font_weight="bold",
                font_family=self.MEME_STYLE["headline_font"],
                color=self.MEME_STYLE["headline_color"],
                position="top",
                text_align="center",
            )
        ]

        if body_text:
            texts.append(TextElement(
                content=body_text,
                role="body",
                font_size=32,
                font_weight="regular",
                font_family=self.MEME_STYLE["body_font"],
                color=self.MEME_STYLE["body_color"],
                position="bottom",
                text_align="center",
            ))

        if cta_text:
            texts.append(TextElement(
                content=cta_text,
                role="cta",
                font_size=24,
                font_weight="bold",
                font_family="Arial",
                color="#0066FF",
                position="bottom",
                text_align="center",
            ))

        images = [
            ImageElement(
                image_url=image_url,
                position="center",
            )
        ]

        return AdSpec(
            name="meme_ad",
            size=size,
            background_color=self.MEME_STYLE["background_color"],
            texts=texts,
            images=images,
        )

    def create_b2b_ad_spec(
        self,
        size: AdSize,
        image_url: str | None,
        headline: str,
        subheadline: str | None = None,
        body: str | None = None,
        cta: str | None = None,
    ) -> AdSpec:
        """Create a professional B2B ad specification."""
        texts = [
            TextElement(
                content=headline,
                role="headline",
                font_size=self.B2B_STYLE["headline_size"],
                font_weight="bold",
                font_family=self.B2B_STYLE["headline_font"],
                color=self.B2B_STYLE["headline_color"],
                position="top",
                text_align="left",
            )
        ]

        if subheadline:
            texts.append(TextElement(
                content=subheadline,
                role="subheadline",
                font_size=24,
                font_weight="medium",
                font_family=self.B2B_STYLE["body_font"],
                color=self.B2B_STYLE["body_color"],
                position="top",
                text_align="left",
            ))

        if body:
            texts.append(TextElement(
                content=body,
                role="body",
                font_size=18,
                font_weight="regular",
                font_family=self.B2B_STYLE["body_font"],
                color=self.B2B_STYLE["body_color"],
                position="center",
                text_align="left",
            ))

        if cta:
            texts.append(TextElement(
                content=cta,
                role="cta",
                font_size=20,
                font_weight="bold",
                font_family=self.B2B_STYLE["body_font"],
                color="#FFFFFF",
                position="bottom",
                text_align="center",
            ))

        images = []
        if image_url:
            images.append(ImageElement(
                image_url=image_url,
                position="background",
                opacity=0.15,
            ))

        return AdSpec(
            name="b2b_ad",
            size=size,
            background_color=self.B2B_STYLE["background_color"],
            texts=texts,
            images=images,
        )

    def spec_to_figma_instructions(self, spec: AdSpec) -> str:
        """Convert an AdSpec to natural language instructions for Figma MCP."""
        width, height = spec.size.value

        instructions = f"""Create a new Figma frame with these specifications:

## Frame Setup
- Name: "{spec.name}"
- Size: {width}x{height} pixels
- Background color: {spec.background_color}
- Padding: {spec.padding}px on all sides

## Images
"""
        for i, img in enumerate(spec.images, 1):
            instructions += f"""
### Image {i}
- Source: {img.image_url}
- Position: {img.position}
- Opacity: {img.opacity * 100}%
"""
            if img.corner_radius:
                instructions += f"- Corner radius: {img.corner_radius}px\n"

        instructions += "\n## Text Elements\n"

        for i, text in enumerate(spec.texts, 1):
            instructions += f"""
### Text {i} ({text.role})
- Content: "{text.content}"
- Font: {text.font_family} {text.font_weight}
- Size: {text.font_size}px
- Color: {text.color}
- Position: {text.position}
- Alignment: {text.text_align}
"""
            if text.max_width:
                instructions += f"- Max width: {text.max_width}px (wrap text)\n"

        instructions += """
## Layout Notes
- Ensure proper visual hierarchy
- Text should be readable and not overlap awkwardly with images
- Maintain consistent spacing between elements
"""

        return instructions

    def get_platform_sizes(self, platform: str) -> list[AdSize]:
        """Get recommended ad sizes for a platform."""
        platform_sizes = {
            "instagram": [AdSize.INSTAGRAM_SQUARE, AdSize.INSTAGRAM_STORY, AdSize.INSTAGRAM_PORTRAIT],
            "facebook": [AdSize.FACEBOOK_FEED, AdSize.FACEBOOK_SQUARE, AdSize.FACEBOOK_STORY],
            "twitter": [AdSize.TWITTER_POST, AdSize.TWITTER_CARD],
            "linkedin": [AdSize.LINKEDIN_POST, AdSize.LINKEDIN_SQUARE],
            "google": [AdSize.GOOGLE_MEDIUM_RECTANGLE, AdSize.GOOGLE_LEADERBOARD],
            "telegram": [AdSize.TELEGRAM_POST, AdSize.INSTAGRAM_SQUARE],
        }
        return platform_sizes.get(platform.lower(), [AdSize.SQUARE])
