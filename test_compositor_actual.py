"""Test the actual compositor service - saves locally for review."""

import asyncio
import io
from PIL import Image
from services.image_compositor import ImageCompositor


async def test_actual_compositor():
    compositor = ImageCompositor()

    # Sample copy
    hook = "B2B-лидген в 2026. Работает без спама."
    body = "С 2014 года я занимаюсь только холодными продажами. Сейчас один человек с нейросетью и Clay делает объем работы, на который раньше нужен был отдел."
    cta = "Прочитать гайд"

    # Create white background image
    target_size = (1080, 1080)
    img = Image.new("RGB", target_size, color="white")

    # Use the internal compose logic directly
    from PIL import ImageDraw

    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Get margins
    margins = compositor._get_safe_zone("instagram_square", "auto")
    left_margin = margins["left"]
    right_margin = margins["right"]
    max_text_width = width - left_margin - right_margin

    # Font sizes
    HOOK_SIZE = 76
    BODY_SIZE = 40
    CTA_SIZE = 50

    # Fonts
    hook_font = compositor._find_font("impact", HOOK_SIZE, text=hook)
    body_font = compositor._find_font("liberation", BODY_SIZE, text=body)
    cta_font = compositor._find_font("liberation", CTA_SIZE, text=cta)

    # Wrap text
    hook_lines = compositor._wrap_text(hook.upper(), hook_font, max_text_width)
    body_lines = compositor._wrap_text(body, body_font, max_text_width)
    cta_lines = [cta.upper()]

    # Calculate heights
    hook_height = sum(hook_font.getbbox(line)[3] - hook_font.getbbox(line)[1] + 6 for line in hook_lines)
    body_height = sum(body_font.getbbox(line)[3] - body_font.getbbox(line)[1] + 8 for line in body_lines)
    cta_height = sum(cta_font.getbbox(line)[3] - cta_font.getbbox(line)[1] + 6 for line in cta_lines)

    total_text_height = hook_height + body_height + cta_height
    gap_size = 70
    total_content_height = total_text_height + (gap_size * 2)

    print(f"Hook: {hook_height}px ({len(hook_lines)} lines)")
    print(f"Body: {body_height}px ({len(body_lines)} lines)")
    print(f"CTA: {cta_height}px ({len(cta_lines)} lines)")
    print(f"Total text: {total_text_height}px")
    print(f"Gaps: {gap_size * 2}px")
    print(f"Total content: {total_content_height}px")

    # Center vertically
    y_offset = (height - total_content_height) // 2
    print(f"Start Y: {y_offset}px")

    # Draw hook
    for line in hook_lines:
        bbox = hook_font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y_offset), line, font=hook_font, fill="black")
        y_offset += bbox[3] - bbox[1] + 6

    y_offset += gap_size

    # Draw body
    for line in body_lines:
        bbox = body_font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y_offset), line, font=body_font, fill="#333333")
        y_offset += bbox[3] - bbox[1] + 8

    y_offset += gap_size

    # Draw CTA
    for line in cta_lines:
        bbox = cta_font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y_offset), line, font=cta_font, fill="black")
        y_offset += bbox[3] - bbox[1] + 6

    # Save locally
    output_path = "/Users/kirill/Documents/Dev Dev Dev/ACTIVE/creo_image_generator/test_compositor_result.png"
    img.save(output_path)
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    asyncio.run(test_actual_compositor())
