"""FastAPI application entry point for Ad Creative Agent."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import router
from config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    settings = get_settings()

    # Ensure output directories exist
    outputs_path = Path(settings.storage_local_path)
    outputs_path.mkdir(parents=True, exist_ok=True)
    (outputs_path / "generated").mkdir(exist_ok=True)

    print(f"Ad Creative Agent starting...")
    print(f"Storage path: {outputs_path.absolute()}")
    print(f"Available image backends: {settings.get_available_image_backends()}")
    print(f"Available video backends: {settings.get_available_video_backends()}")

    yield

    # Shutdown
    print("Ad Creative Agent shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Ad Creative Agent API",
    description="""
## Ad Creative Agent - Tool API for Dify

This API provides tools for AI-powered ad creative generation, designed to be used
with Dify as the orchestration layer.

### Available Tools

**Image Generation**
- `/tools/generate-image` - Generate images using various AI backends (DALL-E 3, Flux, SDXL, etc.)
- `/tools/compare-backends` - Generate the same prompt with multiple backends for comparison

**Reference Analysis**
- `/tools/analyze-reference` - Analyze reference images for style, colors, composition
- `/tools/search-references` - Search the web for reference images

**Copywriting**
- `/tools/generate-copy` - Generate ad copy variations (headlines, body, CTAs)

**Video Generation** (Phase 4)
- `/tools/generate-video` - Generate short videos from prompts or images

### Integration with Dify

1. Deploy this API on a server accessible to your Dify instance
2. In Dify, create a new tool using the OpenAPI import feature
3. Point it to `{your-api-url}/tools/openapi.json`
4. The tools will be available in your Dify workflows

### Configuration

Configure backends via environment variables in `.env`:
- `OPENAI_API_KEY` - For DALL-E 3 and GPT-4 Vision
- `REPLICATE_API_TOKEN` - For Flux and SDXL
- `STABILITY_API_KEY` - For Stability AI
- `IDEOGRAM_API_KEY` - For Ideogram
- `SERPER_API_KEY` - For web search
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware (needed for Dify to call the API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Also mount routes at root for simpler access
app.include_router(router)

# Serve generated files
settings = get_settings()
outputs_path = Path(settings.storage_local_path)
outputs_path.mkdir(parents=True, exist_ok=True)
app.mount("/files", StaticFiles(directory=str(outputs_path)), name="files")


@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API info."""
    settings = get_settings()
    return {
        "name": "Ad Creative Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "dify_import": "/tools/openapi.json",
        "available_backends": {
            "image": settings.get_available_image_backends(),
            "video": settings.get_available_video_backends(),
        },
    }


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
