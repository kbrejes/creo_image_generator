"""Image compositor - adds text overlays to generated images."""

import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import httpx

from services.storage import get_storage_service


class ImageCompositor:
    """Composes final ad images with text overlays."""

    # Font paths (system fonts)
    FONT_PATHS = {
        "impact": [
            "/System/Library/Fonts/Supplemental/Impact.ttf",  # macOS
            "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",  # Linux
            "C:\\Windows\\Fonts\\impact.ttf",  # Windows
        ],
        "arial_bold": [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
        ],
        "helvetica_bold": [
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Helvetica.ttc",
        ],
    }

    # Ad size presets
    SIZES = {
        "instagram_square": (1080, 1080),
        "instagram_story": (1080, 1920),
        "instagram_portrait": (1080, 1350),
        "facebook_feed": (1200, 628),
        "telegram": (1280, 720),
        "twitter": (1200, 675),
    }

    def __init__(self):
        self.storage = get_storage_service()

    def _find_font(self, font_name: str, size: int) -> ImageFont.FreeTypeFont:
        """Find and load a font, with fallbacks."""
        paths = self.FONT_PATHS.get(font_name, self.FONT_PATHS["impact"])

        for path in paths:
            if Path(path).exists():
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue

        # Fallback to default
        try:
            return ImageFont.truetype("Arial", size)
        except Exception:
            return ImageFont.load_default()

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def _draw_text_with_outline(
        self,
        draw: ImageDraw.ImageDraw,
        position: tuple[int, int],
        text: str,
        font: ImageFont.FreeTypeFont,
        fill: str = "white",
        outline: str = "black",
        outline_width: int = 3,
    ):
        """Draw text with outline/stroke effect."""
        x, y = position

        # Draw outline
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline)

        # Draw main text
        draw.text((x, y), text, font=font, fill=fill)

    async def compose(
        self,
        image_source: str,  # URL or file path
        hook_text: str,
        body_text: str = "",
        cta_text: str = "",
        output_size: str = "instagram_square",
        font_name: str = "impact",
        hook_font_size: int = 72,
        body_font_size: int = 48,
        cta_font_size: int = 36,
        text_color: str = "white",
        outline_color: str = "black",
        outline_width: int = 3,
        padding: int = 40,
    ) -> dict:
        """
        Compose an ad image with text overlays.

        Args:
            image_source: URL or local path to the base image
            hook_text: Main text at top of image
            body_text: Secondary text at bottom (optional)
            cta_text: Call to action text (optional)
            output_size: Target size preset
            font_name: Font to use (impact, arial_bold)
            hook_font_size: Font size for hook text
            body_font_size: Font size for body text
            cta_font_size: Font size for CTA
            text_color: Text fill color
            outline_color: Text outline color
            outline_width: Outline thickness
            padding: Padding from edges

        Returns:
            Dict with success status and output URL
        """
        try:
            # Load the source image
            if image_source.startswith("http"):
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_source)
                    response.raise_for_status()
                    img = Image.open(io.BytesIO(response.content))
            else:
                img = Image.open(image_source)

            # Get target size
            target_size = self.SIZES.get(output_size, self.SIZES["instagram_square"])

            # Resize image to fit target, maintaining aspect ratio and cropping
            img = self._resize_and_crop(img, target_size)

            # Create drawing context
            draw = ImageDraw.Draw(img)
            width, height = img.size
            max_text_width = width - (padding * 2)

            # Load fonts
            hook_font = self._find_font(font_name, hook_font_size)
            body_font = self._find_font(font_name, body_font_size)
            cta_font = self._find_font(font_name, cta_font_size)

            # Draw hook text at top
            if hook_text:
                lines = self._wrap_text(hook_text.upper(), hook_font, max_text_width)
                y_offset = padding

                for line in lines:
                    bbox = hook_font.getbbox(line)
                    text_width = bbox[2] - bbox[0]
                    x = (width - text_width) // 2

                    self._draw_text_with_outline(
                        draw, (x, y_offset), line, hook_font,
                        fill=text_color, outline=outline_color, outline_width=outline_width
                    )
                    y_offset += bbox[3] - bbox[1] + 10

            # Draw body and CTA at bottom
            bottom_texts = []
            if body_text:
                bottom_texts.append((body_text, body_font, body_font_size))
            if cta_text:
                bottom_texts.append((cta_text, cta_font, cta_font_size))

            if bottom_texts:
                # Calculate total height needed for bottom texts
                total_height = 0
                text_blocks = []

                for text, font, _ in bottom_texts:
                    lines = self._wrap_text(text, font, max_text_width)
                    block_height = 0
                    for line in lines:
                        bbox = font.getbbox(line)
                        block_height += bbox[3] - bbox[1] + 5
                    text_blocks.append((lines, font, block_height))
                    total_height += block_height + 20

                # Start from bottom
                y_offset = height - padding - total_height

                for lines, font, _ in text_blocks:
                    for line in lines:
                        bbox = font.getbbox(line)
                        text_width = bbox[2] - bbox[0]
                        x = (width - text_width) // 2

                        self._draw_text_with_outline(
                            draw, (x, y_offset), line, font,
                            fill=text_color, outline=outline_color, outline_width=outline_width
                        )
                        y_offset += bbox[3] - bbox[1] + 5
                    y_offset += 15

            # Save to bytes
            output = io.BytesIO()
            img.save(output, format="PNG", quality=95)
            output.seek(0)

            # Save via storage service
            filename, url = await self.storage.save(
                data=output.getvalue(),
                content_type="image/png",
                folder="composed",
            )

            return {
                "success": True,
                "url": url,
                "filename": filename,
                "size": f"{width}x{height}",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Composition failed: {str(e)}",
            }

    def _resize_and_crop(self, img: Image.Image, target_size: tuple[int, int]) -> Image.Image:
        """Resize and crop image to exactly fit target size."""
        target_w, target_h = target_size
        target_ratio = target_w / target_h

        img_w, img_h = img.size
        img_ratio = img_w / img_h

        # Resize to cover target size
        if img_ratio > target_ratio:
            # Image is wider - fit height, crop width
            new_h = target_h
            new_w = int(img_w * (target_h / img_h))
        else:
            # Image is taller - fit width, crop height
            new_w = target_w
            new_h = int(img_h * (target_w / img_w))

        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Crop to center
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        right = left + target_w
        bottom = top + target_h

        return img.crop((left, top, right, bottom))
