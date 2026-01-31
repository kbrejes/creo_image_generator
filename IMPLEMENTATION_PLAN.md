# Implementation Plan: Creo Image Generator Update

## Overview
This plan covers three main objectives:
1. Fix the production pipeline (server 502 error)
2. Clean up dify folder and outdated files
3. Implement 4 visual format types with safe zones and CTA buttons

---

## Phase 0: Auto-Approval Setup

### How to Let Claude Work Autonomously

Run Claude Code with the `--dangerously-skip-permissions` flag:

```bash
claude --dangerously-skip-permissions
```

This allows me to:
- Run bash commands without asking
- Edit/write files without asking
- Make HTTP requests
- SSH into servers

**Alternative (more controlled)**: Use `/allowed-tools` to add specific permissions during the session.

---

## Phase 1: Fix Production Server (502 Error)

### Problem
- `https://creo.yourads.io/health` returns 502 Bad Gateway
- Caddy reverse proxy is up, but FastAPI container is down

### Steps
1. SSH into VPS: `ssh root@185.241.151.190`
2. Check Docker status: `docker ps -a`
3. Check logs: `docker logs creo-api`
4. Restart container: `cd ~/creo_image_generator && docker-compose up -d --build`
5. Verify: `curl https://creo.yourads.io/health`

### Success Criteria
- `/health` returns `{"status": "healthy", ...}`
- `/tools/generate-image` responds to POST requests

---

## Phase 2: Cleanup Dify Folder

### Files to DELETE (22 files)
```
dify/
├── ad_creative_v2.yml          # Old version
├── ad_creative_v3.yml          # Old version
├── ad_creative_v4.yml          # Old version
├── ad_creative_v6_auto_fetch.yml  # Old version
├── ad_creative_workflow.yml    # Old version
├── workflow_final.yml          # Old version
├── workflow_v2.yml             # Old version
├── ad_creative_agent.yml       # Replaced by v5
├── ADD_URL_FETCHING.md         # Outdated doc
├── DEBUG_V4.md                 # Outdated doc
├── HOW_TO_ADD_CONTENT_EXTRACTION.md
├── QUICK_SETUP.md
├── QUICK_START.md
├── READY_TO_DEPLOY.md
├── SETUP_GUIDE.md
├── V4_ENHANCEMENTS.md
├── V4_USAGE_FIX.md
├── V5_CONTENT_EXTRACTION.md
├── V5_URL_WORKFLOW.md
├── V5_USAGE_GUIDE.md
├── V6_AUTO_FETCH_SETUP.md
└── WORKFLOW_GUIDE.md
```

### Files to KEEP (5 items)
```
dify/
├── ad_creative_v5_content.yml  # Rename to ad_creative_agent.yml
├── ad_creative_agent.json      # Keep for reference
├── creo_tool_schema.json       # OpenAPI schema
├── DIFY_SETUP.md               # Main setup doc
└── prompts/                    # LLM prompts folder
    ├── content_extraction.md
    ├── copy_generation_meme.md
    └── image_prompt_builder.md
```

### Steps
1. Delete old workflow versions
2. Delete outdated documentation
3. Rename v5_content.yml → ad_creative_agent.yml
4. Update references in remaining files

---

## Phase 3: Implement 4 Visual Formats

### Current State
- `image_compositor.py` has 2 modes: white bg / AI bg
- 6 size presets (instagram_square, story, portrait, etc.)
- Text overlay with hook, body, CTA

### New Architecture

#### Format Selection
Add `format_type` parameter to compose endpoints:
```python
format_type: str = "meme"  # Options: "text_only", "meme", "stickers", "split"
```

#### Format 1: Text Only (exists, minor update)
- White background
- Black text (hook, body, CTA)
- Even vertical distribution
- **Update**: Add safe zone margins

#### Format 2: Meme Style (exists, minor update)
- AI-generated or white background
- Text overlay
- **Update**: Add safe zone margins

#### Format 3: Text + Stickers (NEW)
- White background with text
- Stickers/memes scattered in free space
- Sticker sources:
  - Pre-loaded library (bundled PNGs)
  - Web search via Serper API
  - AI-generated cutouts
  - User uploads (future)

**Implementation:**
```python
async def compose_with_stickers(
    text: str,
    sticker_query: str = "",  # e.g., "reaction meme", "pointing"
    sticker_urls: list[str] = [],  # Direct URLs
    sticker_positions: str = "auto",  # auto, corners, sides
    ...
)
```

#### Format 4: Split Screen (NEW)
- 50/50 split with ~15° angled divider
- Left: Input image (AI or uploaded)
- Right: Solid color background (white default, user-selectable)
- Text on right side
- CTA spanning bottom (full width)

**Implementation:**
```python
async def compose_split(
    image_source: str,
    hook_text: str,
    body_text: str = "",
    cta_text: str = "",
    right_bg_color: str = "white",  # Or hex like "#FF5733"
    divider_angle: int = 15,  # Degrees
    ...
)
```

### Safe Zones Implementation

Add to `ImageCompositor`:
```python
SAFE_ZONES = {
    "tiktok": {
        "top": 160,
        "bottom": 480,
        "left": 120,
        "right": 120,
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
    "none": {  # For square/feed posts
        "top": 40,
        "bottom": 40,
        "left": 40,
        "right": 40,
    },
}
```

Add parameter:
```python
safe_zone: str = "auto"  # auto, tiktok, instagram_reels, instagram_story, none
```

### CTA Button Implementation

Add to `ImageCompositor`:
```python
async def _draw_cta_button(
    self,
    draw: ImageDraw.ImageDraw,
    img: Image.Image,
    text: str,
    position: tuple[int, int],
    font: ImageFont.FreeTypeFont,
    button_color: str = "auto",  # auto = extract from image
    text_color: str = "white",
    corner_radius: int = 20,
    padding: tuple[int, int] = (40, 20),  # horizontal, vertical
):
    """Draw CTA as rounded rectangle button."""
```

Add parameter:
```python
cta_style: str = "text"  # text, button
```

### Updated Size Presets

```python
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
    # Custom (passed as WxH string)
    # "1200x800" -> (1200, 800)
}
```

---

## Phase 4: Update API Endpoints

### New Endpoint: `/tools/compose-format`
Unified endpoint supporting all 4 formats:

```python
@router.post("/tools/compose-format")
async def api_compose_format(
    # Core
    format_type: str = "meme",  # text_only, meme, stickers, split
    hook_text: str = "",
    body_text: str = "",
    cta_text: str = "",

    # Image source (for meme/split)
    image_url: str = "",
    image_prompt: str = "",  # Generate if no URL

    # Stickers (for stickers format)
    sticker_query: str = "",
    sticker_urls: str = "",  # JSON array

    # Split options
    right_bg_color: str = "white",
    divider_angle: int = 15,

    # Sizing
    output_size: str = "instagram_square",
    custom_size: str = "",  # "1200x800"
    safe_zone: str = "auto",

    # CTA
    cta_style: str = "text",  # text, button
    cta_button_color: str = "auto",

    # Text styling
    text_color: str = "white",
    bold_hook: str = "yes",
):
```

### Keep existing endpoints for backward compatibility
- `/tools/compose-ad` - single image
- `/tools/compose-batch` - batch variations

---

## Phase 5: Update Dify Workflow

After backend is ready, update `ad_creative_agent.yml`:

1. Add format selection dropdown in Start node:
```yaml
- label: "Visual Format"
  type: select
  variable: format_type
  options:
    - "Meme Style (text over image)"
    - "Text Only (white background)"
    - "Text + Stickers"
    - "Split Screen (photo left, text right)"
```

2. Add new input fields:
```yaml
- label: "Right Side Color (for split format)"
  type: text-input
  variable: right_bg_color

- label: "Sticker Theme (for stickers format)"
  type: text-input
  variable: sticker_query

- label: "CTA Style"
  type: select
  variable: cta_style
  options:
    - "Text"
    - "Button"
```

3. Update HTTP node to use new endpoint

---

## Phase 6: Testing Plan

### Local Testing (I can do this)
1. Start local server: `python main.py`
2. Run test suite: `python test_workflow.py`
3. Test each format with curl commands
4. Verify output images

### Test Cases

| Test | Format | Input | Expected |
|------|--------|-------|----------|
| 1 | text_only | hook + body + cta | White bg, black text, centered |
| 2 | meme | hook + cta + image_url | Image bg, white text, safe zones |
| 3 | stickers | hook + sticker_query="pointing" | White bg + scattered stickers |
| 4 | split | hook + image_url | 50/50 split, angled divider |
| 5 | button | cta_style=button | Rounded rect CTA |
| 6 | safe_zone | safe_zone=tiktok | 160px top, 480px bottom margin |

### Production Testing
After deployment:
1. Run `python test_workflow.py` against production
2. Test via Dify workflow
3. Generate sample creatives for each format

---

## Implementation Order

```
Phase 1: Fix Server          [~5 min]
    └── SSH → restart Docker → verify

Phase 2: Cleanup             [~5 min]
    └── Delete files → rename → commit

Phase 3: Backend Changes     [~45 min]
    ├── 3.1: Add safe zones to compositor
    ├── 3.2: Add CTA button drawing
    ├── 3.3: Implement split format
    ├── 3.4: Implement stickers format
    ├── 3.5: Add new size presets
    └── 3.6: Create unified endpoint

Phase 4: Testing             [~15 min]
    ├── Local tests
    ├── Deploy to production
    └── Production tests

Phase 5: Dify Workflow       [~10 min]
    └── Update workflow with new options

Phase 6: Final Verification  [~5 min]
    └── End-to-end test via Dify
```

---

## Files to Modify

| File | Changes |
|------|---------|
| `services/image_compositor.py` | Safe zones, CTA button, split format, stickers |
| `api/routes.py` | New `/tools/compose-format` endpoint |
| `api/schemas.py` | New request/response models |
| `dify/ad_creative_agent.yml` | New format options |
| `test_workflow.py` | New test cases |

---

## Sticker Library (Phase 3.4)

### Pre-loaded Stickers
Create `assets/stickers/` folder with common reaction images:
- pointing_finger.png
- shocked_face.png
- thumbs_up.png
- fire.png
- money.png
- arrow_down.png
- star.png
- check.png

### Web Search Stickers
Use existing `services/web_search.py` to search for:
- "meme reaction transparent png"
- "pointing finger cutout"
- etc.

### AI-Generated Stickers (future)
Use DALL-E/Flux with:
- "cutout sticker of [X], transparent background, cartoon style"

---

## Ready to Execute?

Once you approve this plan, I will:
1. Fix the server first (you'll need to provide SSH password or I can use the one in .vps_config)
2. Clean up the dify folder
3. Implement all backend changes
4. Run tests locally
5. Deploy to production
6. Update Dify workflow
7. Run final tests

Estimated total time: ~1.5 hours of work
