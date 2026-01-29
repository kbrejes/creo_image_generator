# Dify Workflow Setup - Meme Ad Generator

## Prerequisites

- FastAPI server running: `python main.py` (https://creo.yourads.io)
- Dify self-hosted instance
- Any LLM configured (Claude, GPT-4, etc.)

---

## Step 1: Create New App

1. Open Dify
2. Click **"Create Blank App"**
3. Select **"Chatflow"**
4. Name: `Meme Ad Generator`
5. Click Create

---

## Step 2: Add "Analyze Input" Node

1. Click **+** after Start node
2. Select **LLM**
3. Configure:

**Title:** `Analyze Input`

**Model:** Select your preferred model

**SYSTEM Prompt:**
```
You analyze user requests for ad creation. Extract key info and respond with JSON only, no other text.
```

**USER Prompt:**
```
Analyze this ad request:

{{#sys.query#}}

Return JSON only:
{
  "product_name": "name of product/service/channel",
  "description": "what it is/does",
  "target_audience": "who it's for",
  "pain_points": ["problem 1", "problem 2"],
  "tone": "casual",
  "platform": "instagram"
}
```

4. Click **Save**

---

## Step 3: Add "Generate Copy" Node

1. Click **+** after Analyze Input
2. Select **LLM**
3. Configure:

**Title:** `Generate Copy`

**SYSTEM Prompt:**
```
You write meme-style ad copy. Short, punchy, internet humor.

Rules:
- Hook text goes at TOP of meme image (attention-grabbing, ALL CAPS)
- Body text goes at BOTTOM (optional punchline, can be empty)
- CTA is the call to action
- Keep it casual and relatable
- Be funny but not cringe

Respond with JSON only, no other text.
```

**USER Prompt:**
```
Create meme ad copy for:

{{#1711234567890.text#}}

Return JSON only:
{
  "hook": "TOP TEXT IN CAPS - attention grabbing",
  "body": "bottom text or empty string",
  "cta": "call to action"
}
```

> **Note:** Replace `1711234567890` with the actual node ID of "Analyze Input" (hover over the node to see its ID)

4. Click **Save**

---

## Step 4: Add "Image Prompt" Node

1. Click **+** (add parallel to Generate Copy, or after it)
2. Select **LLM**
3. Configure:

**Title:** `Image Prompt`

**SYSTEM Prompt:**
```
You create prompts for AI image generation.

CRITICAL RULES:
1. NEVER include text, words, or letters in the prompt
2. Focus on facial expressions, reactions, situations
3. Make it meme-style and relatable
4. End every prompt with: NO TEXT NO WORDS NO LETTERS
```

**USER Prompt:**
```
Create a meme-style image prompt based on:

{{#1711234567890.text#}}

Focus on a funny reaction face or relatable situation.
Return ONLY the prompt, nothing else. End with "NO TEXT NO WORDS NO LETTERS"
```

4. Click **Save**

---

## Step 5: Add "Generate Image" HTTP Node

1. Click **+** after Image Prompt
2. Select **HTTP Request**
3. Configure:

**Title:** `Generate Image`

**Method:** `POST`

**URL:** `https://creo.yourads.io/tools/generate-image`

**Headers:**
| Key | Value |
|-----|-------|
| Content-Type | application/json |

**Body Type:** JSON

**Body:**
```json
{
  "prompt": "{{#1711234567891.text#}}",
  "backend": "flux",
  "size": "1024x1024",
  "negative_prompt": "text, words, letters, writing, watermark, logo"
}
```

> Replace `1711234567891` with Image Prompt node ID

4. Click **Save**

---

## Step 6: Add "Compose Ad" HTTP Node

1. Click **+** after Generate Image
2. Select **HTTP Request**
3. Configure:

**Title:** `Compose Ad`

**Method:** `POST`

**URL:**
```
https://creo.yourads.io/pipeline/compose
```

**Params (Query Parameters):**

| Key | Value |
|-----|-------|
| image_url | `{{#1711234567892.body.images[0].url#}}` |
| hook_text | `{{#1711234567893.text.hook#}}` |
| body_text | `{{#1711234567893.text.body#}}` |
| cta_text | `{{#1711234567893.text.cta#}}` |
| output_size | instagram_square |

> Replace node IDs:
> - `1711234567892` = Generate Image node
> - `1711234567893` = Generate Copy node

4. Click **Save**

---

## Step 7: Add Response Node

1. Click **+** after Compose Ad
2. Select **LLM**
3. Configure:

**Title:** `Format Response`

**USER Prompt:**
```
Here's the generated meme ad:

🖼️ **Your Ad:** {{#1711234567894.body.url#}}

📝 **Copy Used:**
- Hook: {{#1711234567893.text.hook#}}
- Body: {{#1711234567893.text.body#}}
- CTA: {{#1711234567893.text.cta#}}

Format this nicely for the user. Include the image URL as a clickable link.
Ask if they want:
- Different copy variations
- Different meme style
- Different platform size
```

4. Click **Save**

---

## Step 8: Connect to End

1. Drag from Format Response to **End** node
2. Set End output to: `{{#1711234567895.text#}}` (Format Response node)

---

## Step 9: Test It!

1. Click **"Run"** or **"Debug"**
2. Enter test message:
```
Create a meme ad for my free Telegram channel about B2B lead generation and cold email tips
```

3. Watch each node execute
4. Final output should include the composed ad URL

---

## Troubleshooting

### "Connection refused" on HTTP nodes
```bash
# Make sure FastAPI is running
cd /path/to/creo_image_generator
python main.py
```

### Image generation fails
- Check Replicate credit: https://replicate.com/account/billing
- Check `.env` has `REPLICATE_API_TOKEN`

### JSON parsing errors in LLM nodes
- Add "Respond with JSON only" to prompts
- Use a smarter model (Claude 3.5, GPT-4)

### Node IDs
- Hover over any node to see its ID
- Replace placeholder IDs in this guide with your actual IDs

---

## Quick Reference

| Endpoint | Purpose |
|----------|---------|
| `POST /tools/generate-image` | Generate meme image (no text) |
| `POST /pipeline/compose` | Add text overlay |
| `GET /health` | Check server status |

---

## Example Flow

**Input:** "Meme ad for my SaaS that automates cold emails"

**Output:**
- Image: Shocked office worker face
- Hook: "WHEN THE AI WRITES BETTER COLD EMAILS THAN YOU"
- Body: "and it only took 5 seconds"
- CTA: "Try it free →"
