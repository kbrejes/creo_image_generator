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
        # Bold fonts
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
        # Regular fonts (non-bold)
        "arial": [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux Docker
            "/System/Library/Fonts/Supplemental/Arial.ttf",  # macOS
            "/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",  # Linux
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
        ],
        "liberation": [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux Docker
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Fallback
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
        cta_emoji: bool = False,
        bold_hook: bool = True,
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
            BODY_SIZE = 55
            HOOK_SIZE = 65  # 18% larger than body
            CTA_SIZE = 70   # 27% larger than body, largest
            MIN_FONT_SIZE = 28

            # Font selection: bold for hook (if enabled), regular for body/CTA
            bold_font = "impact"  # Bold font for hook
            regular_font = "liberation"  # Regular font for body/CTA
            hook_font_name = bold_font if bold_hook else regular_font
            body_font_name = regular_font
            cta_font_name = regular_font

            # Add emoji to CTA if enabled
            if cta_emoji and cta_text:
                cta_text = f"{cta_text} 👇"

            # Check if this is a white/blank background (no AI image with faces)
            is_white_bg = not image_source or image_source.lower() in ("white", "blank", "none", "")

            if is_white_bg:
                # === WHITE BACKGROUND: Even distribution of all text blocks ===
                # Calculate heights for all blocks first, then distribute evenly

                all_blocks = []  # [(lines, font, block_height), ...]

                # Hook block (bold if enabled, uppercase)
                if hook_text:
                    hook_font = self._find_font(hook_font_name, HOOK_SIZE)
                    hook_lines = self._wrap_text(hook_text.upper(), hook_font, max_text_width)
                    hook_height = sum(hook_font.getbbox(line)[3] - hook_font.getbbox(line)[1] + 10 for line in hook_lines)
                    all_blocks.append((hook_lines, hook_font, hook_height, 10))

                # Body block (regular font, normal case)
                if body_text:
                    body_font = self._find_font(body_font_name, BODY_SIZE)
                    body_lines = self._wrap_text(body_text, body_font, max_text_width)
                    body_height = sum(body_font.getbbox(line)[3] - body_font.getbbox(line)[1] + 12 for line in body_lines)
                    all_blocks.append((body_lines, body_font, body_height, 12))

                # CTA block (regular font, uppercase)
                if cta_text:
                    cta_font = self._find_font(cta_font_name, CTA_SIZE)
                    cta_lines = self._wrap_text(cta_text.upper(), cta_font, max_text_width)
                    cta_height = sum(cta_font.getbbox(line)[3] - cta_font.getbbox(line)[1] + 10 for line in cta_lines)
                    all_blocks.append((cta_lines, cta_font, cta_height, 10))

                # Calculate total text height and remaining space
                total_text_height = sum(block[2] for block in all_blocks)
                available_space = height - (padding * 2) - total_text_height

                # Distribute space evenly between blocks (n blocks = n-1 gaps)
                num_gaps = max(1, len(all_blocks) - 1)
                gap_size = max(40, available_space // num_gaps) if available_space > 0 else 40

                # Draw all blocks with even spacing
                y_offset = padding
                for i, (lines, font, block_height, line_spacing) in enumerate(all_blocks):
                    for line in lines:
                        bbox = font.getbbox(line)
                        text_width = bbox[2] - bbox[0]
                        x = (width - text_width) // 2

                        self._draw_text_with_outline(
                            draw, (x, y_offset), line, font,
                            fill=text_color, outline=outline_color, outline_width=outline_width
                        )
                        y_offset += bbox[3] - bbox[1] + line_spacing

                    # Add gap after block (except last one)
                    if i < len(all_blocks) - 1:
                        y_offset += gap_size

            else:
                # === AI BACKGROUND: Hook at top, body+CTA at bottom (safe zone in middle) ===

                # Draw hook text at top (bold if enabled)
                if hook_text:
                    hook_font = self._find_font(hook_font_name, HOOK_SIZE)
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
                        y_offset += bbox[3] - bbox[1] + 15

                # Body and CTA at bottom (regular font)
                max_bottom_y = height - padding
                min_body_y = bottom_zone_start + padding

                if body_text or cta_text:
                    current_body_size = BODY_SIZE

                    while current_body_size >= MIN_FONT_SIZE:
                        text_blocks = []
                        total_height = 0

                        if body_text:
                            body_font = self._find_font(body_font_name, current_body_size)
                            body_lines = self._wrap_text(body_text, body_font, max_text_width)
                            text_blocks.append((body_lines, body_font))
                            for line in body_lines:
                                bbox = body_font.getbbox(line)
                                total_height += bbox[3] - bbox[1] + 12

                        if cta_text:
                            cta_size = int(CTA_SIZE * current_body_size / BODY_SIZE)
                            cta_font = self._find_font(cta_font_name, max(cta_size, MIN_FONT_SIZE))
                            cta_lines = self._wrap_text(cta_text.upper(), cta_font, max_text_width)
                            text_blocks.append((cta_lines, cta_font))
                            if body_text:
                                total_height += 40
                            for line in cta_lines:
                                bbox = cta_font.getbbox(line)
                                total_height += bbox[3] - bbox[1] + 12

                        if total_height <= (max_bottom_y - min_body_y):
                            break
                        current_body_size -= 3

                    y_offset = max_bottom_y - total_height
                    if y_offset < min_body_y:
                        y_offset = min_body_y

                    for i, (lines, font) in enumerate(text_blocks):
                        for line in lines:
                            bbox = font.getbbox(line)
                            text_width = bbox[2] - bbox[0]
                            x = (width - text_width) // 2

                            self._draw_text_with_outline(
                                draw, (x, y_offset), line, font,
                                fill=text_color, outline=outline_color, outline_width=outline_width
                            )
                            y_offset += bbox[3] - bbox[1] + 12
                        if i < len(text_blocks) - 1:
                            y_offset += 40

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
