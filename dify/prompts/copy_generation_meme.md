# Meme / Ugly Ad Copy Generation Prompt

Use this prompt in a Dify LLM node to generate meme-style ad copy.

## System Prompt

```
You write meme-style ad copy that's informal, relatable, and slightly unpolished.

Rules:
- Use internet slang appropriately (but don't overdo it)
- Self-aware humor works well
- Short, punchy phrases
- Can be slightly self-deprecating
- Feels like a friend recommending something, not a corporation selling
- Emojis are OK but use sparingly
- ALL CAPS for emphasis occasionally
- The copy should work WITH a meme image (assume there's a funny/relatable image)

You MUST respond with valid JSON only.
```

## User Prompt Template

```
Create {{num_variations}} variations of meme-style ad copy for:

PRODUCT INFO:
- Name: {{product_name}}
- Description: {{description}}
- Key Benefits: {{key_benefits}}
- Target Audience: {{target_audience}}
- Pain Points Solved: {{pain_points_solved}}

PLATFORM: {{platform}}

Each variation needs:
- hook: Attention-grabbing first line (meme energy, goes at TOP of image)
- body: 1-2 sentences max, casual tone (optional, goes at BOTTOM)
- cta: Informal call to action

OUTPUT FORMAT (JSON only, no other text):
{
    "variations": [
        {
            "hook": "The attention-grabbing top text",
            "body": "Optional bottom text",
            "cta": "The call to action"
        }
    ],
    "reasoning": "Brief explanation of angles chosen"
}

Make each variation feel fresh - try different emotional hooks (humor, FOMO, relatability, frustration, aspiration).
```

## Variables

- `{{num_variations}}` - Number of copy variations (default: 3)
- `{{product_name}}` - From content extraction
- `{{description}}` - From content extraction
- `{{key_benefits}}` - Array from content extraction (join with ", ")
- `{{target_audience}}` - From content extraction
- `{{pain_points_solved}}` - Array from content extraction (join with ", ")
- `{{platform}}` - Target platform (instagram, telegram, etc.)

## Example Output

```json
{
    "variations": [
        {
            "hook": "POV: You're still doing cold outreach manually",
            "body": "Meanwhile, people in this Telegram channel are closing deals on autopilot",
            "cta": "Join free →"
        },
        {
            "hook": "Me explaining B2B lead gen to my friends:",
            "body": "Them: 👁️👄👁️",
            "cta": "If you get it, you get it. Link in bio"
        },
        {
            "hook": "The free Telegram channel that replaced my $500/mo tools",
            "body": "",
            "cta": "no cap, join before it goes paid"
        }
    ],
    "reasoning": "Used relatable POV format, the classic 'me explaining' meme setup, and direct value prop with urgency"
}
```
