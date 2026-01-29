"""Reference image analysis and search tools."""

from services.reference_analyzer import ReferenceAnalyzer
from services.web_search import WebSearchService


async def analyze_reference(
    image_url: str | None = None,
    image_base64: str | None = None,
    analysis_type: str = "full",
    context: str | None = None,
) -> dict:
    """
    Analyze a reference image to extract style, colors, composition, etc.

    Args:
        image_url: URL of the image to analyze
        image_base64: Base64-encoded image data (alternative to URL)
        analysis_type: Type of analysis (full, style, colors, composition, text)
        context: Additional context to focus the analysis

    Returns:
        Dict with analysis results
    """
    if not image_url and not image_base64:
        return {
            "success": False,
            "error": "Either image_url or image_base64 must be provided",
        }

    analyzer = ReferenceAnalyzer()
    result = await analyzer.analyze(
        image_url=image_url,
        image_base64=image_base64,
        analysis_type=analysis_type,
        context=context,
    )

    # Transform to match API schema
    if result.get("success"):
        return {
            "success": True,
            "style_description": result.get("style_description"),
            "dominant_colors": result.get("dominant_colors", []),
            "composition_notes": result.get("raw_analysis"),  # Full analysis as composition notes
            "text_detected": None,  # Would need specific extraction
            "mood": result.get("mood"),
            "suggested_prompt_elements": result.get("suggested_prompt_elements", []),
            "raw_analysis": result.get("raw_analysis"),
        }
    else:
        return {
            "success": False,
            "error": result.get("error", "Analysis failed"),
        }


async def search_references(
    query: str,
    num_results: int = 5,
    image_type: str | None = None,
    platform: str | None = None,
) -> dict:
    """
    Search the web for reference images.

    Args:
        query: Search query (e.g., "minimalist tech ad", "luxury perfume advertisement")
        num_results: Number of results to return (1-20)
        image_type: Type of images (photo, illustration, etc.)
        platform: If searching for ads, specify platform (instagram, facebook, etc.)

    Returns:
        Dict with search results
    """
    search_service = WebSearchService()

    if platform:
        # Use ad-specific search
        result = await search_service.search_ads(
            query=query,
            platform=platform,
            num_results=num_results,
        )
    else:
        result = await search_service.search_images(
            query=query,
            num_results=num_results,
            image_type=image_type,
        )

    # Transform to match API schema
    if result.get("success"):
        return {
            "success": True,
            "results": [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "image_url": r.get("image_url"),
                    "thumbnail_url": r.get("thumbnail_url"),
                    "source": r.get("source"),
                }
                for r in result.get("results", [])
            ],
        }
    else:
        return {
            "success": False,
            "results": [],
            "error": result.get("error", "Search failed"),
        }
