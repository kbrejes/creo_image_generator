"""Pydantic schemas for API request/response models."""

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


# ===================
# Image Generation
# ===================


class ImageGenerationRequest(BaseModel):
    """Request model for image generation."""

    prompt: str = Field(
        ...,
        description="The prompt describing the image to generate",
        min_length=1,
        max_length=4000,
    )
    backend: str | None = Field(
        default=None,
        description="Image generation backend to use (dalle3, flux, sdxl, stability, ideogram). "
        "If not specified, the best available backend will be chosen.",
    )
    size: str = Field(
        default="1024x1024",
        description="Image size in format WxH. Common sizes: 1024x1024, 1792x1024, 1024x1792",
    )
    style: str | None = Field(
        default=None,
        description="Style preset (e.g., 'vivid', 'natural' for DALL-E 3)",
    )
    quality: str = Field(
        default="standard",
        description="Quality level (standard, hd)",
    )
    num_images: int = Field(
        default=1,
        description="Number of images to generate",
        ge=1,
        le=4,
    )
    negative_prompt: str | None = Field(
        default=None,
        description="What to avoid in the image (not supported by all backends)",
    )


class GeneratedImage(BaseModel):
    """A single generated image."""

    url: str = Field(..., description="URL to access the generated image")
    filename: str = Field(..., description="Filename of the generated image")
    backend: str = Field(..., description="Backend used to generate this image")
    revised_prompt: str | None = Field(
        default=None,
        description="The prompt as revised by the backend (if applicable)",
    )


class ImageGenerationResponse(BaseModel):
    """Response model for image generation."""

    success: bool = Field(..., description="Whether generation was successful")
    images: list[GeneratedImage] = Field(
        default_factory=list, description="List of generated images"
    )
    error: str | None = Field(default=None, description="Error message if failed")
    metadata: dict = Field(
        default_factory=dict, description="Additional metadata about the generation"
    )


# ===================
# Reference Analysis
# ===================


class ReferenceAnalysisRequest(BaseModel):
    """Request model for reference image analysis."""

    image_url: HttpUrl | None = Field(
        default=None, description="URL of the reference image to analyze"
    )
    image_base64: str | None = Field(
        default=None, description="Base64-encoded image data"
    )
    analysis_type: Literal["full", "style", "colors", "composition", "text"] = Field(
        default="full",
        description="Type of analysis to perform (Legacy parameter, now always technical)",
    )
    context: str | None = Field(
        default=None,
        description="Additional context (Ignored in technical mode)",
    )


class ColorInfo(BaseModel):
    """Information about a color in the image."""

    hex: str = Field(..., description="Hex color code")
    name: str | None = Field(default=None, description="Human-readable color name")
    percentage: float = Field(..., description="Approximate percentage of image")


class ReferenceAnalysisResponse(BaseModel):
    """Response model for reference analysis."""

    success: bool = Field(..., description="Whether analysis was successful")
    style_description: str | None = Field(
        default=None, description="Technical summary of image properties"
    )
    dominant_colors: list[ColorInfo] = Field(
        default_factory=list, description="Dominant colors in the image"
    )
    composition_notes: str | None = Field(
        default=None, description="Dimensions and aspect ratio"
    )
    text_detected: bool | None = Field(
        default=False, description="Whether text was detected (always false in technical mode)"
    )
    mood: str | None = Field(default=None, description="Overall mood (always Neutral in technical mode)")
    suggested_prompt_elements: list[str] = Field(
        default_factory=list,
        description="Empty list (Creative suggestions moved to Dify)",
    )
    error: str | None = Field(default=None, description="Error message if failed")


# ===================
# Video Generation (Phase 4)
# ===================


class VideoGenerationRequest(BaseModel):
    """Request model for video generation."""

    prompt: str = Field(..., description="The prompt describing the video to generate")
    source_image_url: str | None = Field(
        default=None, description="URL of image to animate (for image-to-video)"
    )
    backend: str | None = Field(
        default=None, description="Video generation backend (runway, pika, kling)"
    )
    duration: int = Field(
        default=4, description="Video duration in seconds", ge=2, le=16
    )
    aspect_ratio: str = Field(
        default="16:9", description="Aspect ratio (16:9, 9:16, 1:1)"
    )


class VideoGenerationResponse(BaseModel):
    """Response model for video generation."""

    success: bool = Field(..., description="Whether generation was successful")
    video_url: str | None = Field(default=None, description="URL to the generated video")
    thumbnail_url: str | None = Field(default=None, description="URL to video thumbnail")
    duration: float | None = Field(default=None, description="Actual video duration")
    backend: str | None = Field(default=None, description="Backend used")
    error: str | None = Field(default=None, description="Error message if failed")


# ===================
# Web Search (for references)
# ===================


class WebSearchRequest(BaseModel):
    """Request model for web image search."""

    query: str = Field(..., description="Search query for finding reference images")
    num_results: int = Field(
        default=5, description="Number of results to return", ge=1, le=20
    )
    image_type: str | None = Field(
        default=None, description="Type of images (photo, illustration, etc.)"
    )


class SearchResult(BaseModel):
    """A single search result."""

    title: str = Field(..., description="Title of the result")
    url: str = Field(..., description="URL of the page")
    image_url: str | None = Field(default=None, description="Direct image URL")
    thumbnail_url: str | None = Field(default=None, description="Thumbnail URL")
    source: str | None = Field(default=None, description="Source website")


class WebSearchResponse(BaseModel):
    """Response model for web search."""

    success: bool = Field(..., description="Whether search was successful")
    results: list[SearchResult] = Field(
        default_factory=list, description="Search results"
    )
    error: str | None = Field(default=None, description="Error message if failed")


# ===================
# Health Check
# ===================


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    available_image_backends: list[str] = Field(
        default_factory=list, description="Configured image backends"
    )
    available_video_backends: list[str] = Field(
        default_factory=list, description="Configured video backends"
    )


# ===================
# Batch Composition
# ===================


class TextVariation(BaseModel):
    """A single text variation for batch composition."""

    hook_text: str = Field(..., description="Main text at top of image")
    body_text: str | None = Field(default="", description="Secondary text at bottom")
    cta_text: str | None = Field(default="", description="Call to action text")


class BatchComposeRequest(BaseModel):
    """Request model for batch ad composition."""

    image_url: str = Field(
        ..., description="URL of the base image to use for all variations"
    )
    variations: list[TextVariation] = Field(
        ..., description="List of text variations to apply", min_length=1
    )
    output_size: str = Field(
        default="instagram_square", description="Target size preset"
    )
    font_name: str = Field(default="impact", description="Font to use")
    text_color: str = Field(default="white", description="Text fill color")
    outline_color: str = Field(default="black", description="Text outline color")


class BatchComposeResponse(BaseModel):
    """Response model for batch composition."""

    success: bool = Field(..., description="Whether batch processing was successful")
    images: list[str] = Field(
        default_factory=list, description="List of URLs for generated images"
    )
    error: str | None = Field(default=None, description="Error message if failed")