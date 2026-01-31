"""Quick visual test for compositor - generates local image for review."""

import asyncio
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def find_cyrillic_font(size: int) -> ImageFont.FreeTypeFont:
    """Find a font that supports Cyrillic."""
    # Fonts with good Cyrillic support, in order of preference
    font_paths = [
        # macOS
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]

    for path in font_paths:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue

    return ImageFont.load_default()


def find_bold_font(size: int) -> ImageFont.FreeTypeFont:
    """Find a bold font that supports Cyrillic."""
    font_paths = [
        # macOS
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]

    for path in font_paths:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue

    return ImageFont.load_default()


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
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


def test_compose(bg_color="white", text_color="black", use_outline=False):
    # Canvas
    width, height = 1080, 1080
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Margins
    margin = 60
    max_text_width = width - (margin * 2)

    # Sample copy
    hook = "B2B-лидген в 2026. Работает без спама."
    body = "С 2014 года я занимаюсь только холодными продажами. Сейчас один человек с нейросетью и Clay делает объем работы, на который раньше нужен был отдел."
    cta = "Прочитать гайд"

    # Font sizes - uniform, body/CTA 10% smaller than hook
    HOOK_SIZE = 72
    BODY_SIZE = 65
    CTA_SIZE = 65

    # Load fonts (Cyrillic-compatible)
    hook_font = find_bold_font(HOOK_SIZE)
    body_font = find_cyrillic_font(BODY_SIZE)
    cta_font = find_cyrillic_font(CTA_SIZE)

    # Wrap text
    hook_lines = wrap_text(hook.upper(), hook_font, max_text_width)
    body_lines = wrap_text(body, body_font, max_text_width)
    cta_lines = [cta.upper()]

    # Calculate heights
    def calc_block_height(lines, font, line_spacing):
        total = 0
        for line in lines:
            bbox = font.getbbox(line)
            total += bbox[3] - bbox[1] + line_spacing
        return total - line_spacing  # Remove last spacing

    LINE_SPACING = 8
    hook_height = calc_block_height(hook_lines, hook_font, LINE_SPACING)
    body_height = calc_block_height(body_lines, body_font, LINE_SPACING)
    cta_height = calc_block_height(cta_lines, cta_font, LINE_SPACING)

    total_text_height = hook_height + body_height + cta_height

    # Fixed gaps between blocks (not dependent on canvas size)
    BLOCK_GAP = 70  # Fixed gap between text blocks

    # Calculate total content height
    total_content_height = total_text_height + (BLOCK_GAP * 2)  # 2 gaps between 3 blocks

    # Center vertically
    start_y = (height - total_content_height) // 2

    print(f"Canvas: {width}x{height}")
    print(f"Hook: {hook_height}px ({len(hook_lines)} lines)")
    print(f"Body: {body_height}px ({len(body_lines)} lines)")
    print(f"CTA: {cta_height}px ({len(cta_lines)} lines)")
    print(f"Total text: {total_text_height}px")
    print(f"Block gap: {BLOCK_GAP}px")
    print(f"Total content: {total_content_height}px")
    print(f"Start Y: {start_y}px")

    y = start_y

    def draw_text_with_outline(x, y, text, font, fill, outline_color, outline_width=2):
        """Draw text with thin outline."""
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        draw.text((x, y), text, font=font, fill=fill)

    outline_color = "black" if text_color == "white" else "white"
    body_color = text_color if text_color == "white" else "#333333"

    # Draw hook
    for line in hook_lines:
        bbox = hook_font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        if use_outline:
            draw_text_with_outline(x, y, line, hook_font, text_color, outline_color)
        else:
            draw.text((x, y), line, font=hook_font, fill=text_color)
        y += bbox[3] - bbox[1] + LINE_SPACING

    y += BLOCK_GAP

    # Draw body
    for line in body_lines:
        bbox = body_font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        if use_outline:
            draw_text_with_outline(x, y, line, body_font, body_color, outline_color)
        else:
            draw.text((x, y), line, font=body_font, fill=body_color)
        y += bbox[3] - bbox[1] + LINE_SPACING

    y += BLOCK_GAP

    # Draw CTA
    for line in cta_lines:
        bbox = cta_font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        if use_outline:
            draw_text_with_outline(x, y, line, cta_font, text_color, outline_color)
        else:
            draw.text((x, y), line, font=cta_font, fill=text_color)
        y += bbox[3] - bbox[1] + LINE_SPACING

    # Save
    suffix = "_dark" if bg_color != "white" else "_light"
    output_path = f"/Users/kirill/Documents/Dev Dev Dev/ACTIVE/creo_image_generator/test_output{suffix}.png"
    img.save(output_path)
    print(f"\nSaved to: {output_path}")
    return output_path


if __name__ == "__main__":
    # Test light background (no outline)
    print("=== Light Background ===")
    test_compose(bg_color="white", text_color="black", use_outline=False)

    # Test dark background (with outline)
    print("\n=== Dark Background ===")
    test_compose(bg_color="#2C3E50", text_color="white", use_outline=True)
