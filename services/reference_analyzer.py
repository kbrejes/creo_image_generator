"""Reference image analysis service using pure Python (no LLMs).

Extracts technical data like dimensions, format, and dominant colors.
"""

import io
import base64
import httpx
from PIL import Image

class ReferenceAnalyzer:
    """Analyzes reference images for technical properties."""

    def __init__(self):
        # No API keys needed!
        pass

    async def analyze(
        self,
        image_url: str | None = None,
        image_base64: str | None = None,
        analysis_type: str = "technical", # Default to technical
        context: str | None = None,       # Ignored
    ) -> dict:
        """
        Analyze a reference image for technical properties.

        Returns:
            Dict with width, height, format, mode, dominant_colors
        """
        if not image_url and not image_base64:
            return {
                "success": False,
                "error": "Either image_url or image_base64 must be provided",
            }

        try:
            # 1. Load Image
            img = None
            if image_url:
                async with httpx.AsyncClient() as client:
                    response = await client.get(str(image_url))
                    response.raise_for_status()
                    image_data = response.content
                    img = Image.open(io.BytesIO(image_data))
            else:
                # Handle base64
                if "base64," in image_base64:
                    image_base64 = image_base64.split("base64,")[1]
                image_data = base64.b64decode(image_base64)
                img = Image.open(io.BytesIO(image_data))

            # 2. Extract Technical Stats
            stats = {
                "success": True,
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "aspect_ratio": round(img.width / img.height, 2)
            }

            # 3. Extract Dominant Colors (Quantization)
            # Resize for speed and to reduce noise
            small_img = img.resize((150, 150))
            # Convert to P mode (palette) with 5 colors
            result_img = small_img.convert('P', palette=Image.Palette.ADAPTIVE, colors=5)
            
            # Get the palette
            palette = result_img.getpalette()
            color_counts = sorted(result_img.getcolors(), reverse=True)
            
            dominant_colors = []
            total_pixels = sum(count for count, _ in color_counts)

            for i in range(min(5, len(color_counts))):
                count, index = color_counts[i]
                # palette is [r, g, b, r, g, b...]
                r = palette[index * 3]
                g = palette[index * 3 + 1]
                b = palette[index * 3 + 2]
                
                hex_code = "#{:02x}{:02x}{:02x}".format(r, g, b)
                percentage = round((count / total_pixels) * 100, 1)
                
                dominant_colors.append({
                    "hex": hex_code,
                    "rgb": [r, g, b],
                    "percentage": percentage
                })

            stats["dominant_colors"] = dominant_colors
            
            # Add specific guidance for Dify
            stats["dify_context"] = f"Image is {stats['width']}x{stats['height']} ({stats['aspect_ratio']}:1). Dominant colors: {', '.join([c['hex'] for c in dominant_colors])}."

            return stats

        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}",
            }