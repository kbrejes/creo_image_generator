"""Image compositor - adds text overlays to generated images."""

import io
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import httpx
import emoji

from services.storage import get_storage_service


class ImageCompositor:
    """Composes final ad images with text overlays."""

    # Safe zone margins for different platforms (in pixels for 1080px width)
    # These keep text away from UI overlays (profile icons, like buttons, etc.)
    SAFE_ZONES = {
        "tiktok": {
            "top": 160,
            "bottom": 480,
            "left": 60,
            "right": 60,
        },
        "instagram_reels": {
            "top": 108,
            "bottom": 320,
            "left": 60,
            "right": 120,
        },
        "instagram_story": {
            "top": 250,
            "bottom": 250,
            "left": 65,
            "right": 65,
        },
        "youtube_shorts": {
            "top": 120,
            "bottom": 200,
            "left": 60,
            "right": 60,
        },
        "none": {  # For square/feed posts - just basic padding
            "top": 40,
            "bottom": 40,
            "left": 40,
            "right": 40,
        },
    }

    # Font paths (system fonts)
    # User-friendly names map to internal font names
    FONT_STYLES = {
        "bold": "impact",
        "clean": "liberation",
        "modern": "arial_bold",
        "classic": "arial",
    }

    FONT_PATHS = {
        # Bold fonts - prioritize Cyrillic support
        "impact": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux - good Cyrillic
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",  # macOS
            "/System/Library/Fonts/Supplemental/Impact.ttf",  # macOS
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux Docker
            "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",  # Linux
            "C:\\Windows\\Fonts\\impact.ttf",  # Windows
        ],
        "arial_bold": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux - good Cyrillic
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux Docker
            "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
        ],
        "helvetica_bold": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux - good Cyrillic
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux Docker
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Helvetica.ttc",
        ],
        # Regular fonts (non-bold) - prioritize Cyrillic support
        "arial": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux - good Cyrillic
            "/System/Library/Fonts/Supplemental/Arial.ttf",  # macOS
            "/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux Docker
            "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",  # Linux
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
        ],
        "liberation": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux - good Cyrillic
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux Docker
            "/System/Library/Fonts/Supplemental/Arial.ttf",  # macOS fallback
        ],
        "noto_emoji": [
            "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",  # Linux Docker
        ],
    }

    # Ad size presets
    SIZES = {
        # Instagram
        "instagram_square": (1080, 1080),
        "instagram_story": (1080, 1920),
        "instagram_reels": (1080, 1920),
        "instagram_portrait": (1080, 1350),
        "instagram_landscape": (1080, 566),
        # TikTok
        "tiktok": (1080, 1920),
        "tiktok_square": (1080, 1080),
        # Facebook
        "facebook_feed": (1200, 628),
        "facebook_story": (1080, 1920),
        # Twitter/X
        "twitter": (1200, 675),
        "twitter_portrait": (1080, 1350),
        # YouTube
        "youtube_thumbnail": (1280, 720),
        "youtube_shorts": (1080, 1920),
        # Telegram
        "telegram": (1280, 720),
    }

    # Map output sizes to safe zone profiles
    SIZE_TO_SAFE_ZONE = {
        "tiktok": "tiktok",
        "tiktok_square": "none",
        "instagram_reels": "instagram_reels",
        "instagram_story": "instagram_story",
        "youtube_shorts": "youtube_shorts",
        "facebook_story": "instagram_story",
        # All others use "none" (basic padding)
    }

    def __init__(self):
        self.storage = get_storage_service()
        self._emoji_cache: dict[tuple[str, int], Image.Image] = {}

    def _find_font(self, font_name: str, size: int, text: str = "") -> ImageFont.FreeTypeFont:
        """Find and load a font, with fallbacks."""
        paths = self.FONT_PATHS.get(font_name, self.FONT_PATHS["impact"])

        for path in paths:
            if Path(path).exists():
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue
        
        return ImageFont.load_default()

    def _emoji_render_size(self, font: ImageFont.FreeTypeFont) -> int:
        return max(12, int(font.size * 0.95))

    def _emoji_to_twemoji_url(self, emoji_char: str) -> str:
        codepoints = "-".join(f"{ord(ch):x}" for ch in emoji_char)
        return f"https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/{codepoints}.png"

    def _get_emoji_image(self, emoji_char: str, size: int) -> Image.Image | None:
        cache_key = (emoji_char, size)
        cached = self._emoji_cache.get(cache_key)
        if cached is not None:
            return cached

        url = self._emoji_to_twemoji_url(emoji_char)
        try:
            resp = httpx.get(url, timeout=5.0)
            resp.raise_for_status()
            img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
            if img.size != (size, size):
                img = img.resize((size, size), Image.Resampling.LANCZOS)
            self._emoji_cache[cache_key] = img
            return img
        except Exception:
            return None

    def _iter_text_segments(self, text: str) -> list[tuple[str, bool]]:
        entries = emoji.emoji_list(text)
        if not entries:
            return [(text, False)] if text else []

        segments: list[tuple[str, bool]] = []
        last = 0
        for entry in entries:
            start = entry.get("match_start", entry.get("location", 0))
            end = entry.get("match_end", start + len(entry["emoji"]))
            if start > last:
                segments.append((text[last:start], False))
            segments.append((entry["emoji"], True))
            last = end
        if last < len(text):
            segments.append((text[last:], False))
        return segments

    def _measure_text_mixed(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
    ) -> int:
        width = 0
        emoji_size = self._emoji_render_size(font)
        for segment, is_emoji in self._iter_text_segments(text):
            if not segment:
                continue
            if is_emoji:
                width += emoji_size
            else:
                bbox = font.getbbox(segment)
                width += bbox[2] - bbox[0]
        return width

    def _wrap_text(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        max_width: int,
    ) -> list[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            width = self._measure_text_mixed(test_line, font)

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
            font = self._find_font(font_name, size, text=text)
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
        font = self._find_font(font_name, min_font_size, text=text)
        lines = self._wrap_text(text, font, max_width)
        return font, lines

    def _draw_text_with_outline_mixed(
        self,
        img: Image.Image,
        draw: ImageDraw.ImageDraw,
        position: tuple[int, int],
        text: str,
        font: ImageFont.FreeTypeFont,
        fill: str = "white",
        outline: str = "black",
        outline_width: int = 3,
    ):
        x, y = position
        emoji_size = self._emoji_render_size(font)
        ascent, _descent = font.getmetrics()

        for segment, is_emoji in self._iter_text_segments(text):
            if not segment:
                continue
            if is_emoji:
                emoji_img = self._get_emoji_image(segment, emoji_size)
                if emoji_img is not None:
                    emoji_y = y + max(0, ascent - emoji_size)
                    img.paste(emoji_img, (x, emoji_y), emoji_img)
                else:
                    draw.text((x, y), segment, font=font, fill=fill)
                x += emoji_size
                continue

            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), segment, font=font, fill=outline)

            draw.text((x, y), segment, font=font, fill=fill)
            bbox = font.getbbox(segment)
            x += bbox[2] - bbox[0]

    def _draw_text_with_outline(
        self,
        draw: ImageDraw.ImageDraw,
        position: tuple[int, int],
        text: str,
        font: ImageFont.FreeTypeFont,
        fill: str = "white",
        outline: str = "black",
        outline_width: int = 2,
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

    def _draw_text_with_shadow(
        self,
        draw: ImageDraw.ImageDraw,
        position: tuple[int, int],
        text: str,
        font: ImageFont.FreeTypeFont,
        fill: str = "white",
        shadow_color: str = "black",
        shadow_offset: int = 4,
    ):
        """Draw text with drop shadow effect - cleaner than outline."""
        x, y = position

        # Draw shadow (offset down and right)
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)

        # Draw main text
        draw.text((x, y), text, font=font, fill=fill)

    async def batch_compose(
        self,
        image_source: str,
        variations: list[dict],
        output_size: str = "instagram_square",
        font_name: str = "impact",
        text_color: str = "white",
        outline_color: str = "black",
        **kwargs
    ) -> list[str]:
        """Compose multiple text variations on the same base image."""
        results = []
        try:
            # 1. Load the source image ONCE
            if not image_source or image_source.lower() in ("white", "blank", "none", ""):
                target_size = self.SIZES.get(output_size, self.SIZES["instagram_square"])
                base_img = Image.new("RGB", target_size, color="white")
            elif image_source.startswith("http"):
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_source)
                    response.raise_for_status()
                    base_img = Image.open(io.BytesIO(response.content))
            else:
                base_img = Image.open(image_source)

            # 2. Iterate through variations
            for var in variations:
                res = await self.compose(
                    image_source=image_source,
                    hook_text=var.get("hook_text", ""),
                    body_text=var.get("body_text", ""),
                    cta_text=var.get("cta_text", ""),
                    output_size=output_size,
                    font_name=font_name,
                    text_color=text_color,
                    outline_color=outline_color,
                    _preloaded_image=base_img.copy(),
                    **kwargs
                )
                if res.get("success"):
                    results.append(res["url"])
            return results
        except Exception as e:
            print(f"Batch composition error: {e}")
            return []

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
        outline_width: int = 2,  # Thinner outline for cleaner look
        text_style: str = "outline",  # "outline", "shadow", or "none"
        padding: int = 40,
        cta_emoji: bool = False,
        bold_hook: bool = True,
        cta_style: str = "text",
        cta_button_color: str = "auto",
        safe_zone: str = "auto",
        _preloaded_image: Image.Image | None = None,
    ) -> dict:
        """
        Compose an ad image with text overlays.
        """
        try:
            # Get target size
            target_size = self.SIZES.get(output_size, self.SIZES["instagram_square"])

            img = _preloaded_image

            if img is None:
                # Load the source image or create white background
                if not image_source or image_source.lower() in ("white", "blank", "none", ""):
                    # Create white background
                    img = Image.new("RGB", target_size, color="white")
                elif image_source.startswith("http"):
                    async with httpx.AsyncClient() as client:
                        response = await client.get(image_source)
                        response.raise_for_status()
                        img = Image.open(io.BytesIO(response.content))
                else:
                    img = Image.open(image_source)

            # Resize image to fit target, maintaining aspect ratio and cropping
            if img.size != target_size:
                img = self._resize_and_crop(img, target_size)

            # Create drawing context
            draw = ImageDraw.Draw(img)
            width, height = img.size

            # Get safe zone margins (replaces fixed padding)
            margins = self._get_safe_zone(output_size, safe_zone)
            left_margin = margins["left"]
            right_margin = margins["right"]
            top_margin = margins["top"]
            bottom_margin = margins["bottom"]

            max_text_width = width - left_margin - right_margin

            # Define safe zones - top 40% and bottom 40% of image
            # This leaves the middle 20% clear for faces/subjects (reduced gap)
            top_zone_height = int(height * 0.40) - top_margin
            bottom_zone_height = int(height * 0.40) - bottom_margin
            bottom_zone_start = int(height * 0.60)

            # Font sizes - uniform, body/CTA 10% smaller than hook
            HOOK_SIZE = 72
            BODY_SIZE = 65  # ~10% smaller
            CTA_SIZE = 65   # ~10% smaller
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
                    hook_font = self._find_font(hook_font_name, HOOK_SIZE, text=hook_text)
                    hook_lines = self._wrap_text(hook_text.upper(), hook_font, max_text_width)
                    hook_height = sum(hook_font.getbbox(line)[3] - hook_font.getbbox(line)[1] + 6 for line in hook_lines)
                    all_blocks.append(("hook", hook_lines, hook_font, hook_height, 6))

                # Body block (regular font, normal case)
                if body_text:
                    body_font = self._find_font(body_font_name, BODY_SIZE, text=body_text)
                    body_lines = self._wrap_text(body_text, body_font, max_text_width)
                    body_height = sum(body_font.getbbox(line)[3] - body_font.getbbox(line)[1] + 8 for line in body_lines)
                    all_blocks.append(("body", body_lines, body_font, body_height, 8))

                # CTA block (regular font, uppercase)
                if cta_text:
                    cta_font = self._find_font(cta_font_name, CTA_SIZE, text=cta_text)
                    cta_lines = self._wrap_text(cta_text.upper(), cta_font, max_text_width)
                    if cta_style == "button":
                        # Button needs extra height for padding
                        cta_height = cta_font.getbbox(cta_text)[3] + 50
                    else:
                        cta_height = sum(cta_font.getbbox(line)[3] - cta_font.getbbox(line)[1] + 6 for line in cta_lines)
                    all_blocks.append(("cta", cta_lines, cta_font, cta_height, 6))

                # Calculate total text height and remaining space
                total_text_height = sum(block[3] for block in all_blocks)

                # Fixed gap between blocks (70px) - centered vertically
                gap_size = 70
                num_gaps = max(1, len(all_blocks) - 1)
                total_content_height = total_text_height + (gap_size * num_gaps)

                # Determine button color for CTA
                btn_color = "#FF5722" if cta_button_color == "auto" else cta_button_color

                # Center content vertically
                y_offset = (height - total_content_height) // 2
                for i, (block_type, lines, font, block_height, line_spacing) in enumerate(all_blocks):
                    if block_type == "cta" and cta_style == "button":
                        # Draw CTA as button
                        y_offset = self._draw_cta_button(
                            img, draw, lines[0], width // 2, y_offset,
                            font, button_color=btn_color, text_color="white"
                        )
                    else:
                        for line in lines:
                            text_width = self._measure_text_mixed(line, font)
                            bbox = font.getbbox(line)
                            x = (width - text_width) // 2

                            self._draw_text_with_outline_mixed(
                                img,
                                draw,
                                (x, y_offset),
                                line,
                                font,
                                fill=text_color,
                                outline=outline_color,
                                outline_width=outline_width,
                            )
                            y_offset += bbox[3] - bbox[1] + line_spacing

                    # Add gap after block (except last one)
                    if i < len(all_blocks) - 1:
                        y_offset += gap_size

            else:
                # === AI BACKGROUND: Hook at top, body+CTA at bottom (smaller gap in middle) ===

                # Draw hook text at top (bold if enabled)
                if hook_text:
                    hook_font = self._find_font(hook_font_name, HOOK_SIZE, text=hook_text)
                    hook_lines = self._wrap_text(hook_text.upper(), hook_font, max_text_width)

                    y_offset = top_margin
                    for line in hook_lines:
                        text_width = hook_font.getbbox(line)[2] - hook_font.getbbox(line)[0]
                        bbox = hook_font.getbbox(line)
                        x = (width - text_width) // 2

                        self._draw_text_with_outline(
                            draw, (x, y_offset), line, hook_font,
                            fill=text_color, outline=outline_color, outline_width=outline_width
                        )
                        y_offset += bbox[3] - bbox[1] + 8

                # Body and CTA at bottom (regular font)
                max_bottom_y = height - bottom_margin
                min_body_y = bottom_zone_start

                if body_text or cta_text:
                    current_body_size = BODY_SIZE

                    while current_body_size >= MIN_FONT_SIZE:
                        text_blocks = []
                        total_height = 0

                        if body_text:
                            body_font = self._find_font(body_font_name, current_body_size, text=body_text)
                            body_lines = self._wrap_text(body_text, body_font, max_text_width)
                            text_blocks.append(("body", body_lines, body_font))
                            for line in body_lines:
                                bbox = body_font.getbbox(line)
                                total_height += bbox[3] - bbox[1] + 8

                        if cta_text:
                            cta_size = int(CTA_SIZE * current_body_size / BODY_SIZE)
                            cta_font = self._find_font(cta_font_name, max(cta_size, MIN_FONT_SIZE), text=cta_text)
                            cta_lines = self._wrap_text(cta_text.upper(), cta_font, max_text_width)
                            text_blocks.append(("cta", cta_lines, cta_font))
                            if body_text:
                                total_height += 25  # Reduced gap between body and CTA
                            if cta_style == "button":
                                total_height += cta_font.getbbox(cta_text)[3] + 50
                            else:
                                for line in cta_lines:
                                    bbox = cta_font.getbbox(line)
                                    total_height += bbox[3] - bbox[1] + 8

                        if total_height <= (max_bottom_y - min_body_y):
                            break
                        current_body_size -= 3

                    y_offset = max_bottom_y - total_height
                    if y_offset < min_body_y:
                        y_offset = min_body_y

                    # Determine button color
                    if cta_button_color == "auto":
                        btn_color = self._extract_dominant_color(img)
                    else:
                        btn_color = cta_button_color

                    for i, (block_type, lines, font) in enumerate(text_blocks):
                        if block_type == "cta" and cta_style == "button":
                            # Draw CTA as button
                            y_offset = self._draw_cta_button(
                                img, draw, lines[0], width // 2, y_offset,
                                font, button_color=btn_color, text_color="white"
                            )
                        else:
                            for line in lines:
                                text_width = self._measure_text_mixed(line, font)
                                bbox = font.getbbox(line)
                                x = (width - text_width) // 2

                                self._draw_text_with_outline_mixed(
                                    img,
                                    draw,
                                    (x, y_offset),
                                    line,
                                    font,
                                    fill=text_color,
                                    outline=outline_color,
                                    outline_width=outline_width,
                                )
                                y_offset += bbox[3] - bbox[1] + 8
                        if i < len(text_blocks) - 1:
                            y_offset += 25  # Reduced gap

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

    def _draw_rounded_rectangle(
        self,
        draw: ImageDraw.ImageDraw,
        xy: tuple[int, int, int, int],
        radius: int,
        fill: str,
    ):
        """Draw a rounded rectangle."""
        x1, y1, x2, y2 = xy

        # Draw main rectangle
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)

        # Draw four corners
        draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=fill)
        draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=fill)
        draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=fill)
        draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill)

    def _draw_cta_button(
        self,
        img: Image.Image,
        draw: ImageDraw.ImageDraw,
        text: str,
        center_x: int,
        y: int,
        font: ImageFont.FreeTypeFont,
        button_color: str = "#FF5722",
        text_color: str = "white",
        corner_radius: int = 25,
        padding_h: int = 50,
        padding_v: int = 20,
    ) -> int:
        """
        Draw CTA as a rounded rectangle button.
        Returns the bottom y coordinate of the button.
        """
        # Measure text
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate button dimensions
        button_width = text_width + (padding_h * 2)
        button_height = text_height + (padding_v * 2)

        # Calculate button position (centered)
        button_x1 = center_x - (button_width // 2)
        button_x2 = center_x + (button_width // 2)
        button_y1 = y
        button_y2 = y + button_height

        # Draw rounded rectangle button
        self._draw_rounded_rectangle(
            draw,
            (button_x1, button_y1, button_x2, button_y2),
            corner_radius,
            button_color,
        )

        # Draw text centered in button
        text_x = center_x - (text_width // 2)
        text_y = button_y1 + padding_v - (bbox[1])  # Adjust for font baseline
        draw.text((text_x, text_y), text, font=font, fill=text_color)

        return button_y2

    def _get_safe_zone(self, output_size: str, safe_zone: str = "auto") -> dict:
        """Get safe zone margins for the given output size."""
        if safe_zone == "auto":
            # Auto-detect based on output size
            zone_name = self.SIZE_TO_SAFE_ZONE.get(output_size, "none")
        else:
            zone_name = safe_zone if safe_zone in self.SAFE_ZONES else "none"

        return self.SAFE_ZONES[zone_name]

    def _extract_dominant_color(self, img: Image.Image) -> str:
        """Extract the dominant color from an image for button matching."""
        # Resize for faster processing
        small = img.copy()
        small.thumbnail((50, 50))

        # Get colors
        colors = small.getcolors(2500)
        if not colors:
            return "#FF5722"  # Default orange

        # Sort by frequency and get most common
        colors.sort(key=lambda x: x[0], reverse=True)

        # Skip very dark or very light colors, find a vibrant one
        for count, color in colors[:10]:
            if isinstance(color, tuple) and len(color) >= 3:
                r, g, b = color[:3]
                # Skip near-white and near-black
                if (r + g + b) > 100 and (r + g + b) < 650:
                    return f"#{r:02x}{g:02x}{b:02x}"

        return "#FF5722"  # Default orange

    async def compose_split(
        self,
        image_source: str,
        hook_text: str,
        body_text: str = "",
        cta_text: str = "",
        output_size: str = "instagram_square",
        right_bg_color: str = "white",
        divider_angle: int = 15,
        text_color: str = "black",
        cta_style: str = "text",
        cta_button_color: str = "auto",
        safe_zone: str = "auto",
    ) -> dict:
        """
        Compose a split-screen ad: image on left, text on colored background on right.
        Angled divider between the two halves.
        """
        try:
            # Get target size
            target_size = self.SIZES.get(output_size, self.SIZES["instagram_square"])
            width, height = target_size

            # Create base canvas with right side color
            canvas = Image.new("RGB", target_size, color=right_bg_color)
            draw = ImageDraw.Draw(canvas)

            # Load and process the source image
            if image_source and image_source.startswith("http"):
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_source)
                    response.raise_for_status()
                    src_img = Image.open(io.BytesIO(response.content))
            elif image_source:
                src_img = Image.open(image_source)
            else:
                # No image - use a gradient or solid color on left
                src_img = Image.new("RGB", (width // 2, height), color="#4A90E2")

            # Calculate split point (50% width)
            split_x = width // 2

            # Calculate angle offset for the divider
            angle_rad = math.radians(divider_angle)
            angle_offset = int(math.tan(angle_rad) * height / 2)

            # Resize source image to fit left half (with extra for angle)
            left_width = split_x + angle_offset + 20
            src_img = self._resize_and_crop(src_img, (left_width, height))

            # Create a mask for the angled edge (same size as src_img)
            mask = Image.new("L", (left_width, height), 255)
            mask_draw = ImageDraw.Draw(mask)

            # Draw the angled right edge by making it transparent
            # Create a polygon for the part to make transparent (right side)
            polygon = [
                (split_x + angle_offset, 0),  # Top of angle
                (left_width, 0),  # Top-right
                (left_width, height),  # Bottom-right
                (split_x - angle_offset, height),  # Bottom of angle
            ]
            mask_draw.polygon(polygon, fill=0)

            # Paste source image with mask
            canvas.paste(src_img, (0, 0), mask)

            # Get safe zone margins
            margins = self._get_safe_zone(output_size, safe_zone)

            # Text area is the right half
            text_area_left = split_x + 20
            text_area_right = width - margins["right"]
            text_area_width = text_area_right - text_area_left

            # Determine text/outline colors based on background
            if right_bg_color.lower() in ("white", "#ffffff", "#fff"):
                actual_text_color = "black"
                outline_color = "white"
            else:
                actual_text_color = text_color if text_color != "auto" else "white"
                outline_color = "black" if actual_text_color == "white" else "white"

            # Font sizes - uniform
            HOOK_SIZE = 72
            BODY_SIZE = 65
            CTA_SIZE = 65
            MIN_SIZE = 28

            # Calculate text positioning - center vertically in right half
            all_blocks = []

            if hook_text:
                hook_font = self._find_font("impact", HOOK_SIZE)
                hook_lines = self._wrap_text(hook_text.upper(), hook_font, text_area_width)
                hook_height = sum(hook_font.getbbox(line)[3] - hook_font.getbbox(line)[1] + 8 for line in hook_lines)
                all_blocks.append(("hook", hook_lines, hook_font, hook_height))

            if body_text:
                body_font = self._find_font("liberation", BODY_SIZE)
                body_lines = self._wrap_text(body_text, body_font, text_area_width)
                body_height = sum(body_font.getbbox(line)[3] - body_font.getbbox(line)[1] + 8 for line in body_lines)
                all_blocks.append(("body", body_lines, body_font, body_height))

            if cta_text:
                cta_font = self._find_font("liberation", CTA_SIZE)
                cta_lines = [cta_text.upper()]
                cta_height = cta_font.getbbox(cta_text)[3] + 40 if cta_style == "button" else cta_font.getbbox(cta_text)[3]
                all_blocks.append(("cta", cta_lines, cta_font, cta_height))

            # Calculate total height and starting Y
            total_height = sum(block[3] for block in all_blocks) + (len(all_blocks) - 1) * 30
            start_y = max(margins["top"], (height - total_height) // 2)

            # Draw text blocks
            y_offset = start_y
            text_center_x = text_area_left + (text_area_width // 2)

            for block_type, lines, font, block_height in all_blocks:
                for line in lines:
                    text_width = self._measure_text_mixed(line, font)
                    x = text_center_x - (text_width // 2)

                    if block_type == "cta" and cta_style == "button":
                        # Determine button color
                        if cta_button_color == "auto":
                            btn_color = self._extract_dominant_color(src_img)
                        else:
                            btn_color = cta_button_color

                        y_offset = self._draw_cta_button(
                            canvas, draw, line, text_center_x, y_offset,
                            font, button_color=btn_color, text_color="white"
                        )
                    else:
                        self._draw_text_with_outline_mixed(
                            canvas, draw, (x, y_offset), line, font,
                            fill=actual_text_color, outline=outline_color, outline_width=2
                        )
                        bbox = font.getbbox(line)
                        y_offset += bbox[3] - bbox[1] + 8

                y_offset += 30  # Gap between blocks

            # Save
            output = io.BytesIO()
            canvas.save(output, format="PNG", quality=95)
            output.seek(0)

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
                "format": "split",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Split composition failed: {str(e)}",
            }

    async def compose_with_stickers(
        self,
        hook_text: str,
        body_text: str = "",
        cta_text: str = "",
        sticker_urls: list[str] = None,
        output_size: str = "instagram_square",
        bg_color: str = "white",
        text_color: str = "black",
        cta_style: str = "text",
        cta_button_color: str = "#FF5722",
        safe_zone: str = "auto",
    ) -> dict:
        """
        Compose an ad with text on a solid background and stickers scattered around.
        """
        try:
            sticker_urls = sticker_urls or []

            # Get target size
            target_size = self.SIZES.get(output_size, self.SIZES["instagram_square"])
            width, height = target_size

            # Create base canvas
            canvas = Image.new("RGB", target_size, color=bg_color)
            draw = ImageDraw.Draw(canvas)

            # Get safe zone margins
            margins = self._get_safe_zone(output_size, safe_zone)

            # Text area
            text_left = margins["left"]
            text_right = width - margins["right"]
            text_width = text_right - text_left

            # Determine colors
            if bg_color.lower() in ("white", "#ffffff", "#fff"):
                actual_text_color = "black"
                outline_color = "white"
            else:
                actual_text_color = text_color
                outline_color = "black" if text_color == "white" else "white"

            # Font sizes - uniform
            HOOK_SIZE = 72
            BODY_SIZE = 65
            CTA_SIZE = 65

            # Calculate text layout first
            all_blocks = []

            if hook_text:
                hook_font = self._find_font("impact", HOOK_SIZE)
                hook_lines = self._wrap_text(hook_text.upper(), hook_font, text_width)
                hook_height = sum(hook_font.getbbox(line)[3] - hook_font.getbbox(line)[1] + 10 for line in hook_lines)
                all_blocks.append(("hook", hook_lines, hook_font, hook_height))

            if body_text:
                body_font = self._find_font("liberation", BODY_SIZE)
                body_lines = self._wrap_text(body_text, body_font, text_width)
                body_height = sum(body_font.getbbox(line)[3] - body_font.getbbox(line)[1] + 10 for line in body_lines)
                all_blocks.append(("body", body_lines, body_font, body_height))

            if cta_text:
                cta_font = self._find_font("liberation", CTA_SIZE)
                cta_height = cta_font.getbbox(cta_text)[3] + 50 if cta_style == "button" else cta_font.getbbox(cta_text)[3] + 10
                all_blocks.append(("cta", [cta_text.upper()], cta_font, cta_height))

            # Position text in center
            total_height = sum(block[3] for block in all_blocks) + (len(all_blocks) - 1) * 40
            start_y = max(margins["top"], (height - total_height) // 2)

            # Load and place stickers first (so text is on top)
            sticker_positions = [
                (margins["left"], margins["top"]),  # Top-left
                (width - margins["right"] - 150, margins["top"]),  # Top-right
                (margins["left"], height - margins["bottom"] - 150),  # Bottom-left
                (width - margins["right"] - 150, height - margins["bottom"] - 150),  # Bottom-right
            ]

            for i, url in enumerate(sticker_urls[:4]):  # Max 4 stickers
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(url, timeout=10.0)
                        response.raise_for_status()
                        sticker = Image.open(io.BytesIO(response.content)).convert("RGBA")

                        # Resize sticker to max 150x150
                        sticker.thumbnail((150, 150), Image.Resampling.LANCZOS)

                        # Get position
                        pos = sticker_positions[i % len(sticker_positions)]

                        # Paste with alpha
                        canvas.paste(sticker, pos, sticker)
                except Exception:
                    pass  # Skip failed stickers

            # Draw text
            y_offset = start_y
            center_x = width // 2

            for block_type, lines, font, block_height in all_blocks:
                for line in lines:
                    text_w = self._measure_text_mixed(line, font)
                    x = center_x - (text_w // 2)

                    if block_type == "cta" and cta_style == "button":
                        y_offset = self._draw_cta_button(
                            canvas, draw, line, center_x, y_offset,
                            font, button_color=cta_button_color, text_color="white"
                        )
                    else:
                        self._draw_text_with_outline_mixed(
                            canvas, draw, (x, y_offset), line, font,
                            fill=actual_text_color, outline=outline_color, outline_width=2
                        )
                        bbox = font.getbbox(line)
                        y_offset += bbox[3] - bbox[1] + 10

                y_offset += 40

            # Save
            output = io.BytesIO()
            canvas.save(output, format="PNG", quality=95)
            output.seek(0)

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
                "format": "stickers",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Stickers composition failed: {str(e)}",
            }

    async def compose_format(
        self,
        format_type: str = "meme",
        hook_text: str = "",
        body_text: str = "",
        cta_text: str = "",
        image_url: str = "",
        output_size: str = "instagram_square",
        text_color: str = "white",
        right_bg_color: str = "white",
        divider_angle: int = 15,
        sticker_urls: list[str] = None,
        cta_style: str = "text",
        cta_button_color: str = "auto",
        safe_zone: str = "auto",
        bold_hook: bool = True,
    ) -> dict:
        """
        Unified composition method supporting all 4 format types:
        - text_only: White background with black text
        - meme: AI/uploaded image with text overlay
        - stickers: White background with text and sticker images
        - split: 50/50 split with image left, text right
        """
        if format_type == "text_only":
            # For text_only, "auto" defaults to orange since there's no image
            btn_color = "#FF5722" if cta_button_color == "auto" else cta_button_color
            return await self.compose(
                image_source="white",
                hook_text=hook_text,
                body_text=body_text,
                cta_text=cta_text,
                output_size=output_size,
                text_color="black",
                outline_color="white",
                bold_hook=bold_hook,
                cta_style=cta_style,
                cta_button_color=btn_color,
                safe_zone=safe_zone,
            )

        elif format_type == "meme":
            return await self.compose(
                image_source=image_url,
                hook_text=hook_text,
                body_text=body_text,
                cta_text=cta_text,
                output_size=output_size,
                text_color=text_color,
                outline_color="black" if text_color == "white" else "white",
                bold_hook=bold_hook,
                cta_style=cta_style,
                cta_button_color=cta_button_color,
                safe_zone=safe_zone,
            )

        elif format_type == "stickers":
            # For stickers, "auto" defaults to orange since there's no image to extract from
            btn_color = "#FF5722" if cta_button_color == "auto" else cta_button_color
            return await self.compose_with_stickers(
                hook_text=hook_text,
                body_text=body_text,
                cta_text=cta_text,
                sticker_urls=sticker_urls or [],
                output_size=output_size,
                bg_color="white",
                text_color="black",
                cta_style=cta_style,
                cta_button_color=btn_color,
                safe_zone=safe_zone,
            )

        elif format_type == "split":
            return await self.compose_split(
                image_source=image_url,
                hook_text=hook_text,
                body_text=body_text,
                cta_text=cta_text,
                output_size=output_size,
                right_bg_color=right_bg_color,
                divider_angle=divider_angle,
                cta_style=cta_style,
                cta_button_color=cta_button_color,
                safe_zone=safe_zone,
            )

        else:
            return {
                "success": False,
                "error": f"Unknown format_type: {format_type}. Use: text_only, meme, stickers, split",
            }
