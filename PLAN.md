# Ad Creative Agent - Project Plan

## Overview
Build a conversational AI agent that creates high-quality ad creatives (images, copy, video) with human-like decision-making capabilities.

## User Profile
- Non-programmer user
- Has self-hosted Dify instance
- Wants maximum flexibility in LLM and image generation backends
- Needs all creative formats: static images, image+copy, video

---

## Architecture

### Dify-Based Design

Since you have Dify self-hosted, we'll leverage it as the orchestration layer. This gives you:
- Visual workflow builder (no code needed to modify agent behavior)
- Plug any LLM (Claude, GPT-4, Llama, etc.)
- Built-in conversation management
- Easy tool integration via HTTP endpoints

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
│              Custom Tool API (FastAPI Backend)              │
├─────────────┬─────────────┬─────────────┬──────────────────┤
│  Image Gen  │  Reference  │   Copy      │   Video          │
│  Tools      │  Tools      │   Tools     │   Tools          │
├─────────────┼─────────────┼─────────────┼──────────────────┤
│ • DALL-E 3  │ • URL fetch │ • Headlines │ • Runway ML      │
│ • Flux      │ • Local file│ • Body copy │ • Pika           │
│ • SDXL      │ • Web search│ • CTAs      │ • Kling          │
│ • Ideogram  │ • Vision    │             │                  │
│             │   analysis  │             │                  │
└─────────────┴─────────────┴─────────────┴──────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                     File Storage                            │
│  • Generated images stored locally or S3                   │
│  • Returned as URLs for Dify to display                    │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack
- **Orchestration**: Dify (your self-hosted instance)
- **Tool Backend**: Python FastAPI (exposes tools as HTTP endpoints)
- **Image Generation**: Pluggable backend system supporting multiple providers
- **Storage**: Local filesystem or S3-compatible

---

## Project Structure

```
creo_image_generator/
├── main.py                   # FastAPI application entry point
├── config.py                 # Configuration and API keys
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
│
├── api/
│   ├── __init__.py
│   ├── routes.py             # API route definitions
│   └── schemas.py            # Pydantic request/response models
│
├── tools/                    # Tools exposed as HTTP endpoints
│   ├── __init__.py
│   ├── image_gen.py          # Image generation endpoint
│   ├── reference.py          # Reference fetch/analyze endpoint
│   ├── copywriting.py        # Ad copy generation endpoint
│   └── video_gen.py          # Video generation endpoint
│
├── backends/                 # Pluggable image generation backends
│   ├── __init__.py
│   ├── base.py               # Abstract backend interface
│   ├── openai_dalle.py       # DALL-E 3 implementation
│   ├── replicate_flux.py     # Flux via Replicate
│   ├── stability.py          # Stability AI / SDXL
│   └── ideogram.py           # Ideogram API
│
├── services/
│   ├── __init__.py
│   ├── reference_analyzer.py # Vision-based reference analysis
│   ├── web_search.py         # Search for reference images
│   └── storage.py            # File storage management
│
├── dify/                     # Dify workflow exports (for version control)
│   └── ad_creative_agent.yml # Exportable Dify workflow definition
│
└── outputs/                  # Generated creatives stored here
```

---

## Key Features

### 1. Smart Agent Brain
- Uses Claude/GPT-4 as the reasoning engine
- Embedded knowledge of advertising best practices:
  - Composition rules (rule of thirds, focal points)
  - Color psychology for different industries
  - Platform-specific requirements (IG, FB, Google, etc.)
  - CTA placement and copy formulas
- Multi-step reasoning: analyze brief → research → create → critique → refine

### 2. Flexible Image Generation
- **Adapter pattern**: Easy to add new backends
- **Smart routing**: Agent picks best backend for the task
- **Comparison mode**: Generate with multiple backends, pick best

### 3. Reference-Aware Creation
- Analyze reference images with vision models
- Extract style, colors, composition from references
- Apply reference characteristics to new creatives

### 4. Iterative Refinement
- Agent critiques its own outputs
- Suggests improvements
- Can regenerate with feedback

---

## Implementation Phases

### Phase 1: Foundation (MVP)
1. Set up FastAPI backend with basic structure
2. Create image generation tool endpoint (DALL-E 3 first)
3. Create reference analysis tool endpoint
4. Set up Dify workflow that calls these tools
5. Test end-to-end: chat → generate image → return result

### Phase 2: Multi-Backend + References
1. Add Flux, SDXL, Ideogram backends
2. Smart backend selection (agent chooses best for task)
3. URL reference fetching tool
4. Web search for reference images tool
5. Vision-based reference style analysis

### Phase 3: Advanced Creative Tools
1. Ad copy generation tool (headlines, CTAs, body)
2. Platform-specific sizing (IG, FB, Google Display, etc.)
3. Batch generation (multiple variations)
4. Comparison mode (same prompt, multiple backends)

### Phase 4: Video (Future)
1. Video generation backends (Runway, Pika, Kling)
2. Image-to-video conversion
3. Animated ad support

---

## Dify Workflow Design

The Dify workflow will have these key nodes:

1. **Start Node**: Receives user message
2. **LLM Node (Brief Analysis)**:
   - Understands what user wants
   - Extracts: product, style, audience, platform, references
3. **Conditional Branches**:
   - If reference provided → Call reference analysis tool
   - If needs research → Call web search tool
4. **LLM Node (Creative Direction)**:
   - Decides composition, colors, style
   - Crafts optimal prompt for image generation
5. **HTTP Tool Node**: Calls image generation API
6. **LLM Node (Critique)**:
   - Analyzes generated image
   - Suggests improvements or approves
7. **End Node**: Returns image + explanation to user

---

## System Prompt for Ad Expertise

The LLM nodes will use a system prompt embedding advertising knowledge:
- AIDA framework (Attention, Interest, Desire, Action)
- Platform best practices (aspect ratios, text limits)
- Color psychology by industry
- Composition rules (rule of thirds, visual hierarchy)
- CTA formulas that convert

---

## Next Steps

1. Set up Python project with FastAPI
2. Create the image generation tool (DALL-E 3 backend)
3. Create the reference analysis tool
4. Guide you through creating the Dify workflow
5. Test the complete flow
6. Iterate and add more backends

---

## Design Decisions Made
- ✅ Tech stack: Python FastAPI (tool backend)
- ✅ Orchestration: Dify (self-hosted)
- ✅ LLM: Flexible via Dify (plug any model)
- ✅ Image gen: Multiple backends with flexibility
- ✅ References: URL, local files, web search (all supported)
- ✅ Formats: Images, copy, video (phased approach)
