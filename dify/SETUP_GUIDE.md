# Dify Workflow Setup Guide

## Overview

This guide walks you through creating an Ad Creative Agent workflow in Dify that:
1. Takes user input (URL, text, or description)
2. Extracts product information
3. Generates meme-style ad copy
4. Calls the FastAPI backend to generate images
5. Returns everything to the user

## Prerequisites

- FastAPI backend running at `https://creo.yourads.io`
- Dify self-hosted instance
- At least one LLM configured in Dify (Claude, GPT-4, etc.)

---

## Step 1: Create New Workflow

1. Open your Dify instance
2. Click **"Create Blank App"** (or **Studio** → **Create**)
3. Select **"Chatflow"** (conversational workflow)
4. Name it: **"Ad Creative Agent"**

---

## Step 2: Add Start Node

The Start node is created automatically. Configure it:

- **Input variable name**: `user_input`
- **Description**: "Describe your product or paste a URL"

---

## Step 3: Add Content Extraction Node (LLM)

1. Click **"+"** to add a node
2. Select **"LLM"**
3. Configure:

**Name**: `Extract Content`

**Model**: Select your preferred model (Claude 3.5 Sonnet recommended)

**System Prompt**:
```
You extract structured marketing information from content. Always respond with valid JSON only, no other text.
```

**User Prompt**:
```
Analyze this content and extract key information for creating ad creatives.

USER INPUT:
{{#start.user_input#}}

Return a JSON object with these exact fields:
{
    "product_name": "Name of the product/service/brand",
    "description": "Clear, concise description (2-3 sentences)",
    "key_benefits": ["benefit 1", "benefit 2", "benefit 3"],
    "target_audience": "Who this is for",
    "pain_points_solved": ["pain point 1", "pain point 2"],
    "tone": "Brand tone (casual/professional/playful)",
    "industry": "Industry category"
}

If the input is a URL, infer information from the URL/domain name.
If information is unclear, make reasonable inferences based on context.
```

**Output variable**: `product_info`

---

## Step 4: Add Copy Generation Node (LLM)

1. Add another **"LLM"** node
2. Connect it after "Extract Content"
3. Configure:

**Name**: `Generate Copy`

**Model**: Same as before

**System Prompt**:
```
You write meme-style ad copy that's informal, relatable, and slightly unpolished.

Rules:
- Use internet slang appropriately (don't overdo it)
- Self-aware humor works well
- Short, punchy phrases
- Feels like a friend recommending something, not a corporation
- Emojis OK but use sparingly (1-2 max)
- ALL CAPS for emphasis occasionally
- The copy will be overlaid on a meme image

CRITICAL: Respond with valid JSON only. No markdown, no explanation, just the JSON object.
```

**User Prompt**:
```
Create 3 variations of meme-style ad copy based on this product info:

{{#llm.product_info#}}

Platform: Telegram / Instagram

Each variation needs:
- hook: Attention-grabbing text for TOP of meme image (short, punchy)
- body: Text for BOTTOM of image (1 sentence max, can be empty "")
- cta: Call to action (informal, like "link in bio" or "join free")

Return ONLY this JSON structure:
{
    "variations": [
        {"hook": "TOP TEXT HERE", "body": "bottom text here", "cta": "call to action"},
        {"hook": "SECOND HOOK", "body": "second body", "cta": "second cta"},
        {"hook": "THIRD HOOK", "body": "third body", "cta": "third cta"}
    ]
}
```

**Output variable**: `copy_variations`

---

## Step 5: Add Image Prompt Builder Node (LLM)

1. Add another **"LLM"** node
2. Connect it (can run parallel to copy generation)
3. Configure:

**Name**: `Build Image Prompt`

**System Prompt**:
```
You create prompts for AI image generation.

CRITICAL RULES:
1. NEVER include text, words, letters, or writing in the prompt
2. Focus on visual elements only
3. Always end prompts with: NO TEXT NO WORDS NO LETTERS
4. Keep prompts under 200 words
```

**User Prompt**:
```
Create a meme-style image prompt for an ad about:

{{#llm.product_info#}}

The image should show a funny, relatable reaction or situation that matches the product's pain points.

Focus on:
- Expressive facial reactions (shock, disbelief, enlightenment, frustration)
- Relatable office/work/life situations
- Meme aesthetic (slightly exaggerated, internet humor style)

Return ONLY the image prompt. End with "NO TEXT NO WORDS NO LETTERS"
```

**Output variable**: `image_prompt`

---

## Step 6: Add HTTP Request Node (Image Generation)

1. Add an **"HTTP Request"** node
2. Connect it after "Build Image Prompt"
3. Configure:

**Name**: `Generate Image`

**Method**: `POST`

**URL**: `https://creo.yourads.io/tools/generate-image`

**Headers**:
```
Content-Type: application/json
```

**Body** (JSON):
```json
{
    "prompt": "{{#llm_1.image_prompt#}}",
    "backend": "flux",
    "size": "1024x1024",
    "negative_prompt": "text, words, letters, writing, watermark, logo, signature"
}
```

**Output variable**: `generated_image`

---

## Step 7: Add Response Formatter Node (LLM)

1. Add final **"LLM"** node
2. Connect it after both Copy Generation and HTTP Request complete
3. Configure:

**Name**: `Format Response`

**System Prompt**:
```
You format ad creative results for users in a friendly, helpful way. Use markdown for formatting.
```

**User Prompt**:
```
Format this ad creative package for the user:

GENERATED IMAGE:
{{#http_request.generated_image#}}

COPY VARIATIONS:
{{#llm_1.copy_variations#}}

Create a response that includes:

1. Show the image URL (they can click to view)

2. Display copy variations in a nice format:

   **Option 1**
   🔝 Hook: [hook text]
   📝 Body: [body text]
   👉 CTA: [cta text]

   (repeat for all variations)

3. Quick instructions:
   - Open Figma
   - Create 1080x1080 frame
   - Add the image as background
   - Add hook text at top (Impact font, white with black outline)
   - Add body text at bottom
   - Export as PNG

4. Ask if they want:
   - More copy variations
   - Different image style
   - Different platform sizes
```

---

## Step 8: Add End Node

1. Add **"End"** node
2. Connect the Format Response output to it
3. Set output to: `{{#llm_2.text#}}`

---

## Final Workflow Structure

```
[Start]
    │
    ▼
[Extract Content - LLM]
    │
    ├──────────────────┐
    ▼                  ▼
[Generate Copy]    [Build Image Prompt]
    │                  │
    │                  ▼
    │            [HTTP: Generate Image]
    │                  │
    └────────┬─────────┘
             ▼
    [Format Response - LLM]
             │
             ▼
          [End]
```

---

## Step 9: Test the Workflow

1. Click **"Run"** or **"Debug"**
2. Enter test input:
   ```
   A free Telegram channel with tips about B2B lead generation and cold email outreach
   ```
3. Watch each node execute
4. Check the final output

---

## Troubleshooting

### "Connection refused" on HTTP node
- Make sure FastAPI is running: `python main.py`
- Check URL is correct: `https://creo.yourads.io/tools/generate-image`

### Image generation fails
- Check Replicate has credit: https://replicate.com/account/billing
- Check API token in `.env` file

### JSON parsing errors
- Add "Respond with JSON only" to system prompts
- Use a more capable model (Claude 3.5 Sonnet, GPT-4)

### Copy variations look wrong
- Adjust the system prompt
- Add examples of good output

---

## Next: Figma Integration

Once you have the workflow running, the next step is composing the final ad in Figma:

1. Download the generated image
2. Create a frame in Figma (1080x1080 for Instagram)
3. Place the image
4. Add text layers with the copy variations
5. Export

Or use the Figma MCP in Claude Code to automate this!
