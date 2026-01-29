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
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux Docker
            "/System/Library/Fonts/Supplemental/Impact.ttf",  # macOS
            "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",  # Linux
            "C:\\Windows\\Fonts\\impact.ttf",  # Windows
        ],
        "arial_bold": [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux Docker
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
        ],
        "helvetica_bold": [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux Docker
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

        # Fallback to Liberation Sans Bold if available
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", size)
        except Exception:
            pass

        # Last resort - DejaVu Sans Bold
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        except Exception:
            # Final fallback - default font (will be small)
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

    def _calculate_optimal_font_size(
        self,
        text: str,
        max_font_size: int,
        min_font_size: int,
        max_width: int,
        max_height: int,
        font_name: str,
    ) -> tuple[ImageFont.FreeTypeFont, list[str]]:
        """
        Calculate optimal font size to fit text within constraints.
        Dynamically reduces font size until text fits.

        Returns:
            (font, wrapped_lines)
        """
        # Try sizes from max down to min, stepping by 1 for best fit
        for size in range(max_font_size, min_font_size - 1, -1):
            font = self._find_font(font_name, size)
            lines = self._wrap_text(text, font, max_width)

            # Calculate total height needed
            total_height = 0
            for line in lines:
                bbox = font.getbbox(line)
                line_height = bbox[3] - bbox[1]
                total_height += line_height + 5  # 5px line spacing

            # If it fits, return this size
            if total_height <= max_height:
                return font, lines

        # If nothing fits, use minimum size anyway
        font = self._find_font(font_name, min_font_size)
        lines = self._wrap_text(text, font, max_width)
        return font, lines

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
            # Get target size
            target_size = self.SIZES.get(output_size, self.SIZES["instagram_square"])

            # Load the source image or create white background
            if not image_source or image_source.lower() in ("white", "blank", "none", ""):
                # Create white background
                img = Image.new("RGB", target_size, color="white")
            elif image_source.startswith("http"):
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_source)
                    response.raise_for_status()
                    img = Image.open(io.BytesIO(response.content))

            # Resize image to fit target, maintaining aspect ratio and cropping
            img = self._resize_and_crop(img, target_size)

            # Create drawing context
            draw = ImageDraw.Draw(img)
            width, height = img.size
            max_text_width = width - (padding * 2)

            # Define safe zones - top 35% and bottom 35% of image
            # This leaves the middle 30% clear for faces/subjects
            top_zone_height = int(height * 0.35) - padding
            bottom_zone_height = int(height * 0.35) - padding
            bottom_zone_start = int(height * 0.65)

            # Uniform font sizes - max 30% difference between any two
            # CTA is largest, hook medium, body smallest
            # All sizes increased 25% for better readability
            BODY_SIZE = 55
            HOOK_SIZE = 65  # 18% larger than body
            CTA_SIZE = 70   # 27% larger than body, largest

            # Draw hook text at top
            if hook_text:
                hook_font = self._find_font(font_name, HOOK_SIZE)
                hook_lines = self._wrap_text(hook_text.upper(), hook_font, max_text_width)

                y_offset = padding
                for line in hook_lines:
                    bbox = hook_font.getbbox(line)
                    text_width = bbox[2] - bbox[0]
                    x = (width - text_width) // 2

                    self._draw_text_with_outline(
                        draw, (x, y_offset), line, hook_font,
                        fill=text_color, outline=outline_color, outline_width=outline_width
                    )
                    y_offset += bbox[3] - bbox[1] + 15  # Line spacing for hook

            # Body and CTA at bottom
            text_blocks = []

            if body_text:
                body_font = self._find_font(font_name, BODY_SIZE)
                body_lines = self._wrap_text(body_text, body_font, max_text_width)
                text_blocks.append((body_lines, body_font))

            if cta_text:
                cta_font = self._find_font(font_name, CTA_SIZE)
                cta_lines = self._wrap_text(cta_text.upper(), cta_font, max_text_width)
                text_blocks.append((cta_lines, cta_font))

            if text_blocks:

                # Calculate total actual height needed
                total_height = 0
                for lines, font in text_blocks:
                    for line in lines:
                        bbox = font.getbbox(line)
                        total_height += bbox[3] - bbox[1] + 12  # Line spacing
                    total_height += 35  # Spacing between body and CTA blocks

                # Start from bottom, working upward
                y_offset = height - padding - total_height

                for lines, font in text_blocks:
                    for line in lines:
                        bbox = font.getbbox(line)
                        text_width = bbox[2] - bbox[0]
                        x = (width - text_width) // 2

                        self._draw_text_with_outline(
                            draw, (x, y_offset), line, font,
                            fill=text_color, outline=outline_color, outline_width=outline_width
                        )
                        y_offset += bbox[3] - bbox[1] + 12  # Line spacing
                    y_offset += 35  # Space between body and CTA

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
