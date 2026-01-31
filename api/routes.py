"""API routes for the Ad Creative Agent tools."""

from fastapi import APIRouter, HTTPException

from api.schemas import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    GeneratedImage,
    ReferenceAnalysisRequest,
    ReferenceAnalysisResponse,
    ColorInfo,
    VideoGenerationRequest,
    VideoGenerationResponse,
    WebSearchRequest,
    WebSearchResponse,
    SearchResult,
    HealthResponse,
)
from config import get_settings
from tools.image_gen import generate_image, compare_backends
from tools.reference import analyze_reference, search_references
from tools.video_gen import generate_video
from services.image_compositor import ImageCompositor
from services.modern_compositor import ModernCompositor, DesignPreset

router = APIRouter()


# ===================
# Health Check
# ===================


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check service health and available backends."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        available_image_backends=settings.get_available_image_backends(),
        available_video_backends=settings.get_available_video_backends(),
    )


# ===================
# Image Generation
# ===================


@router.post(
    "/tools/generate-image",
    response_model=ImageGenerationResponse,
    tags=["Image Generation"],
    summary="Generate images from text prompt",
    description="Generate one or more images using AI image generation models. "
    "Supports multiple backends: DALL-E 3, Flux, SDXL, Stability AI, Ideogram.",
)
async def api_generate_image(request: ImageGenerationRequest):
    """Generate images from a text prompt."""
    result = await generate_image(
        prompt=request.prompt,
        backend=request.backend,
        size=request.size,
        style=request.style,
        quality=request.quality,
        num_images=request.num_images,
        negative_prompt=request.negative_prompt,
    )

    return ImageGenerationResponse(
        success=result["success"],
        images=[
            GeneratedImage(
                url=img["url"],
                filename=img["filename"],
                backend=img["backend"],
                revised_prompt=img.get("revised_prompt"),
            )
            for img in result.get("images", [])
        ],
        error=result.get("error"),
        metadata=result.get("metadata", {}),
    )


@router.post(
    "/tools/compare-backends",
    response_model=dict,
    tags=["Image Generation"],
    summary="Compare image generation backends",
    description="Generate the same image with multiple backends for comparison.",
)
async def api_compare_backends(
    prompt: str,
    backends: list[str] | None = None,
    size: str = "1024x1024",
    quality: str = "standard",
):
    """Compare outputs from multiple image generation backends."""
    return await compare_backends(
        prompt=prompt,
        backends=backends,
        size=size,
        quality=quality,
    )


# ===================
# Reference Analysis
# ===================


@router.post(
    "/tools/analyze-reference",
    response_model=ReferenceAnalysisResponse,
    tags=["Reference"],
    summary="Analyze a reference image (Technical)",
    description="Analyze a reference image to extract TECHNICAL data: dominant colors (hex), dimensions, format. "
    "Use Dify Vision for creative analysis (style/mood).",
)
async def api_analyze_reference(request: ReferenceAnalysisRequest):
    """Analyze a reference image."""
    result = await analyze_reference(
        image_url=str(request.image_url) if request.image_url else None,
        image_base64=request.image_base64,
        analysis_type=request.analysis_type,
        context=request.context,
    )

    if not result.get("success"):
        return ReferenceAnalysisResponse(
            success=False,
            error=result.get("error", "Analysis failed"),
        )

    return ReferenceAnalysisResponse(
        success=True,
        # Style description is now handled by Dify, but we return a technical summary
        style_description=result.get("dify_context", "Analysis complete"),
        dominant_colors=[
            ColorInfo(
                hex=c.get("hex", "#000000"),
                name="Color", # Name extraction removed to avoid complexity
                percentage=c.get("percentage", 0.0),
            )
            for c in result.get("dominant_colors", [])
        ],
        composition_notes=f"{result.get('width')}x{result.get('height')} px",
        text_detected=False, # Removed OCR
        mood="Neutral", # Removed mood analysis
        suggested_prompt_elements=[], # Removed prompt suggestion
    )


@router.post(
    "/tools/search-references",
    response_model=WebSearchResponse,
    tags=["Reference"],
    summary="Search for reference images",
    description="Search the web for reference images based on a query. "
    "Can search for specific ad styles, platforms, or general image references.",
)
async def api_search_references(request: WebSearchRequest):
    """Search for reference images on the web."""
    result = await search_references(
        query=request.query,
        num_results=request.num_results,
        image_type=request.image_type,
    )

    return WebSearchResponse(
        success=result.get("success", False),
        results=[
            SearchResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                image_url=r.get("image_url"),
                thumbnail_url=r.get("thumbnail_url"),
                source=r.get("source"),
            )
            for r in result.get("results", [])
        ],
        error=result.get("error"),
    )


# ===================
# Video Generation (Phase 4)
# ===================


@router.post(
    "/tools/generate-video",
    response_model=VideoGenerationResponse,
    tags=["Video Generation"],
    summary="Generate video from prompt or image",
    description="Generate a short video from a text prompt or animate a source image. "
    "Note: This feature is planned for Phase 4.",
)
async def api_generate_video(request: VideoGenerationRequest):
    """Generate a video from prompt or image."""
    result = await generate_video(
        prompt=request.prompt,
        source_image_url=request.source_image_url,
        backend=request.backend,
        duration=request.duration,
        aspect_ratio=request.aspect_ratio,
    )

    return VideoGenerationResponse(
        success=result.get("success", False),
        video_url=result.get("video_url"),
        thumbnail_url=result.get("thumbnail_url"),
        duration=result.get("duration"),
        backend=result.get("backend"),
        error=result.get("error"),
    )


# ===================
# Image Compositor
# ===================

@router.post(
    "/tools/compose-ad",
    tags=["Compositing"],
    summary="Compose final ad with text overlay",
    description="Add text overlay to generated image using Pillow. Fully automated.",
)
async def api_compose_ad(
    image_url: str,
    hook_text: str,
    body_text: str = "",
    cta_text: str = "",
    output_size: str = "instagram_square",
    font_name: str = "impact",
    font_style: str = "",  # "bold", "clean", "modern"
    hook_font_size: int = 120,
    body_font_size: int = 60,
    cta_font_size: int = 48,
    text_color: str = "",
    cta_emoji: str = "",
    bold_hook: str = "",
):
    """Compose final ad with text overlay."""
    # Determine text and outline colors
    # Default: white text with black outline (for dark/AI backgrounds)
    # Black option: black text with white outline (for light/white backgrounds)
    if text_color and "black" in text_color.lower():
        actual_text_color = "black"
        outline_color = "white"
    else:
        actual_text_color = "white"
        outline_color = "black"

    # Parse boolean toggles from string
    use_cta_emoji = cta_emoji and "yes" in cta_emoji.lower()
    use_bold_hook = not bold_hook or "yes" in bold_hook.lower()  # Default to yes

    # Map font_style to font_name
    style_to_font = {"bold": "impact", "clean": "liberation", "modern": "arial_bold"}
    if font_style:
        font_style_lower = font_style.lower().replace(" (default)", "")
        font_name = style_to_font.get(font_style_lower, font_name)

    compositor = ImageCompositor()
    return await compositor.compose(
        image_source=image_url,
        hook_text=hook_text,
        body_text=body_text,
        cta_text=cta_text,
        output_size=output_size,
        font_name=font_name,
        hook_font_size=hook_font_size,
        body_font_size=body_font_size,
        cta_font_size=cta_font_size,
        text_color=actual_text_color,
        outline_color=outline_color,
        cta_emoji=use_cta_emoji,
        bold_hook=use_bold_hook,
    )


@router.post(
    "/tools/compose-format",
    tags=["Compositing"],
    summary="Compose ad with selectable format",
    description="""Unified composition endpoint supporting 4 visual formats:
    - text_only: White background with black text
    - meme: AI/uploaded image with text overlay (default)
    - stickers: White background with text and scattered sticker images
    - split: 50/50 split with image on left, text on colored background on right
    """,
)
async def api_compose_format(
    format_type: str = "meme",
    hook_text: str = "",
    body_text: str = "",
    cta_text: str = "",
    image_url: str = "",
    output_size: str = "instagram_square",
    text_color: str = "white",
    right_bg_color: str = "white",
    divider_angle: int = 15,
    sticker_urls: str = "",
    cta_style: str = "text",
    cta_button_color: str = "auto",
    safe_zone: str = "auto",
    bold_hook: str = "yes",
):
    """
    Compose an ad image with the selected format type.

    Format types:
    - text_only: Clean white background with centered black text
    - meme: Image (AI or uploaded) with text overlay
    - stickers: White background with text and sticker images in corners
    - split: 50/50 split screen with angled divider

    CTA styles:
    - text: Regular text (default)
    - button: Rounded rectangle button

    Safe zones:
    - auto: Automatically detect based on output_size
    - tiktok: Large bottom margin for TikTok UI
    - instagram_reels: Instagram Reels margins
    - instagram_story: Instagram Story margins
    - none: Minimal padding only
    """
    import json

    # Parse sticker URLs
    sticker_list = []
    if sticker_urls:
        try:
            sticker_list = json.loads(sticker_urls)
        except json.JSONDecodeError:
            sticker_list = [s.strip() for s in sticker_urls.split(",") if s.strip()]

    use_bold_hook = not bold_hook or "yes" in bold_hook.lower()

    compositor = ImageCompositor()
    return await compositor.compose_format(
        format_type=format_type,
        hook_text=hook_text,
        body_text=body_text,
        cta_text=cta_text,
        image_url=image_url,
        output_size=output_size,
        text_color=text_color,
        right_bg_color=right_bg_color,
        divider_angle=divider_angle,
        sticker_urls=sticker_list,
        cta_style=cta_style,
        cta_button_color=cta_button_color,
        safe_zone=safe_zone,
        bold_hook=use_bold_hook,
    )


@router.post(
    "/tools/compose-batch",
    tags=["Compositing"],
    summary="Compose multiple ads from variations",
    description="Generate multiple ad creatives from a JSON array of copy variations. Supports all 4 format types.",
)
async def api_compose_batch(
    image_url: str = "",
    variations_json: str = "",  # JSON array: [{"hook": "...", "body": "...", "cta": "..."}, ...]
    output_size: str = "instagram_square",
    text_color: str = "",
    cta_emoji: str = "",
    bold_hook: str = "",
    format_type: str = "meme",
    cta_style: str = "text",
    right_bg_color: str = "white",
    safe_zone: str = "auto",
):
    """Compose multiple ads from variations array with format support."""
    import json

    # Parse variations
    try:
        variations = json.loads(variations_json) if variations_json else []
        if not isinstance(variations, list):
            return {"success": False, "error": "variations_json must be a JSON array"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Invalid JSON: {str(e)}"}

    # Determine colors
    if text_color and "black" in text_color.lower():
        actual_text_color = "black"
    else:
        actual_text_color = "white"

    use_bold_hook = not bold_hook or "yes" in bold_hook.lower()

    compositor = ImageCompositor()
    results = []

    # Process each variation using compose_format for full format support
    for v in variations:
        result = await compositor.compose_format(
            format_type=format_type,
            hook_text=v.get("hook", v.get("hook_text", "")),
            body_text=v.get("body", v.get("body_text", "")),
            cta_text=v.get("cta", v.get("cta_text", "")),
            image_url=image_url,
            output_size=output_size,
            text_color=actual_text_color,
            right_bg_color=right_bg_color,
            cta_style=cta_style,
            safe_zone=safe_zone,
            bold_hook=use_bold_hook,
        )
        if result.get("success"):
            results.append(result["url"])

    result_urls = results

    if not result_urls:
        return {
            "success": False,
            "error": "Batch composition failed or produced no results",
        }

    # Format response to include metadata for each
    results = []
    for i, url in enumerate(result_urls):
        orig_var = variations[i] if i < len(variations) else {}
        results.append({
            "index": i + 1,
            "url": url,
            "hook": orig_var.get("hook", ""),
            "body": orig_var.get("body", ""),
            "cta": orig_var.get("cta", ""),
        })

    return {
        "success": True,
        "count": len(results),
        "creatives": results,
    }


# ===================
# Modern Compositor (pictex)
# ===================


@router.post(
    "/tools/compose-modern",
    tags=["Compositing"],
    summary="Compose ad with modern text effects",
    description="""Create professional ad creatives with modern text effects using pictex.

Presets:
- neon: Glowing neon text on dark background
- minimal: Clean white background with subtle shadows
- gradient: Gradient background with shadowed text
- bold: High contrast with colored text stroke
- glass: Glassmorphism style with semi-transparent CTA

Output sizes: instagram_square, instagram_story, instagram_reels, instagram_portrait,
facebook_feed, telegram, tiktok, youtube_thumbnail
""",
)
async def api_compose_modern(
    hook_text: str,
    body_text: str = "",
    cta_text: str = "Подробнее →",
    preset: str = "neon",
    output_size: str = "instagram_square",
    background_image_url: str = "",
):
    """
    Compose an ad with modern text effects.

    Args:
        hook_text: Main headline/hook (required)
        body_text: Supporting body text
        cta_text: Call-to-action button text
        preset: Design preset (neon, minimal, gradient, bold, glass)
        output_size: Output dimensions preset
        background_image_url: Optional background image URL (will darken and overlay text)
    """
    from services.storage import get_storage_service

    try:
        # Validate preset
        try:
            design_preset = DesignPreset(preset.lower())
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid preset '{preset}'. Valid: neon, minimal, gradient, bold, glass",
            }

        compositor = ModernCompositor()

        # Choose composition method based on background image
        if background_image_url:
            image_bytes = compositor.compose_with_image_overlay(
                hook_text=hook_text,
                body_text=body_text,
                cta_text=cta_text,
                background_image_url=background_image_url,
                preset=design_preset,
                output_size=output_size,
                darken=0.5,
            )
        else:
            image_bytes = compositor.compose(
                hook_text=hook_text,
                body_text=body_text,
                cta_text=cta_text,
                preset=design_preset,
                output_size=output_size,
            )

        # Upload to storage
        storage = get_storage_service()
        filename, url = await storage.save(image_bytes)

        return {
            "success": True,
            "url": url,
            "filename": filename,
            "preset": preset,
            "output_size": output_size,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# ===================
# Dify-Specific Endpoints
# ===================


@router.get(
    "/tools/openapi.json",
    tags=["System"],
    summary="Get OpenAPI schema for Dify",
    description="Returns the OpenAPI schema in a format suitable for Dify tool import.",
)
async def get_openapi_for_dify():
    """
    Get OpenAPI schema formatted for Dify import.

    Dify can import tools from an OpenAPI schema. This endpoint provides
    the schema in the format Dify expects.
    """
    from main import app

    return app.openapi()