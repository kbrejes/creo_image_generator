# Ad Creative Agent

A conversational AI agent that creates high-quality ad creatives (images, copy, video) with human-like decision-making capabilities. Designed to work with Dify as the orchestration layer.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DIFY (Self-Hosted)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Ad Creative Agent Workflow              │   │
│  │                                                      │   │
│  │  [User Input] → [LLM: Analyze Brief] → [Tool Call]  │   │
│  │                         ↓                            │   │
│  │              [LLM: Critique & Refine]               │   │
│  │                         ↓                            │   │
│  │              [Return Creative + Explanation]         │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                    HTTP Tool Calls                          │
└────────────────────────────┼────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│              This API (FastAPI Backend)                     │
├─────────────┬─────────────┬─────────────┬──────────────────┤
│  Image Gen  │  Reference  │   Copy      │   Video          │
│  Tools      │  Tools      │   Tools     │   Tools          │
└─────────────┴─────────────┴─────────────┴──────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required for image generation (at least one)
OPENAI_API_KEY=sk-...        # For DALL-E 3
REPLICATE_API_TOKEN=r8_...   # For Flux, SDXL
STABILITY_API_KEY=sk-...     # For Stability AI
IDEOGRAM_API_KEY=...         # For Ideogram

# Required for reference analysis
OPENAI_API_KEY=sk-...        # Also used for GPT-4 Vision

# Optional for web search
SERPER_API_KEY=...           # For searching reference images
```

### 3. Run the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 4. View API Docs

Open `http://localhost:8000/docs` for interactive API documentation.

## API Endpoints

### Image Generation

**POST** `/tools/generate-image`

Generate images from text prompts using various AI backends.

```json
{
  "prompt": "Professional product photo of wireless earbuds on marble surface, soft lighting",
  "backend": "dalle3",
  "size": "1024x1024",
  "quality": "hd",
  "num_images": 1
}
```

### Reference Analysis

**POST** `/tools/analyze-reference`

Analyze reference images to extract style, colors, and composition.

```json
{
  "image_url": "https://example.com/reference.jpg",
  "analysis_type": "full",
  "context": "tech product advertisement"
}
```

### Ad Copy Generation

**POST** `/tools/generate-copy`

Generate ad copy variations with headlines, body text, and CTAs.

```json
{
  "product_name": "AirPods Pro",
  "product_description": "Premium wireless earbuds with noise cancellation",
  "target_audience": "tech-savvy professionals",
  "tone": "premium",
  "platform": "instagram",
  "num_variations": 3
}
```

### Web Search

**POST** `/tools/search-references`

Search the web for reference images.

```json
{
  "query": "minimalist tech ad instagram",
  "num_results": 5
}
```

## Supported Backends

### Image Generation

| Backend | API Key | Best For |
|---------|---------|----------|
| DALL-E 3 | `OPENAI_API_KEY` | Photorealistic, creative interpretation |
| Flux | `REPLICATE_API_TOKEN` | Fast generation, good quality |
| SDXL | `REPLICATE_API_TOKEN` | Detailed, artistic |
| Stability AI | `STABILITY_API_KEY` | Consistent style, inpainting |
| Ideogram | `IDEOGRAM_API_KEY` | Text in images, logos |

### Video Generation (Phase 4)

| Backend | API Key | Status |
|---------|---------|--------|
| Runway ML | `RUNWAY_API_KEY` | Planned |
| Pika | `PIKA_API_KEY` | Planned |
| Kling | `KLING_API_KEY` | Planned |

## Dify Integration

### Import Tools

1. In Dify, go to **Tools** > **Create Tool**
2. Select **Import from URL**
3. Enter: `http://your-api-url/tools/openapi.json`

### Workflow Template

See `dify/ad_creative_agent.yml` for a complete workflow template with:
- Brief analysis
- Reference handling
- Smart prompt crafting
- Image generation
- Self-critique and refinement

## Project Structure

```
creo_image_generator/
├── main.py                   # FastAPI entry point
├── config.py                 # Configuration management
├── requirements.txt          # Dependencies
├── .env.example              # Environment template
│
├── api/
│   ├── routes.py             # API endpoints
│   └── schemas.py            # Request/response models
│
├── tools/                    # Tool implementations
│   ├── image_gen.py          # Image generation
│   ├── reference.py          # Reference analysis
│   ├── copywriting.py        # Ad copy generation
│   └── video_gen.py          # Video generation (Phase 4)
│
├── backends/                 # Image generation backends
│   ├── base.py               # Abstract interface
│   ├── openai_dalle.py       # DALL-E 3
│   ├── replicate_flux.py     # Flux via Replicate
│   ├── stability.py          # Stability AI
│   └── ideogram.py           # Ideogram
│
├── services/
│   ├── storage.py            # File storage (local/S3)
│   ├── reference_analyzer.py # Vision-based analysis
│   └── web_search.py         # Reference image search
│
├── dify/
│   └── ad_creative_agent.yml # Dify workflow template
│
└── outputs/                  # Generated files
```

## Development

### Running in Development Mode

```bash
DEBUG=true python main.py
```

### Adding a New Backend

1. Create a new file in `backends/` (e.g., `backends/midjourney.py`)
2. Inherit from `ImageBackend` base class
3. Implement the `generate()` method
4. Add to `backends/__init__.py`
5. Update `tools/image_gen.py` to include the new backend

## License

MIT
