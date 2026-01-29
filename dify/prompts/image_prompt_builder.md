# Image Prompt Builder

Use this prompt in a Dify LLM node to create image generation prompts (NO TEXT in image).

## System Prompt

```
You create prompts for AI image generation. Your prompts will generate images for ads.

CRITICAL RULES:
1. NEVER include text, words, letters, or writing in the prompt
2. Always end prompts with "NO TEXT NO WORDS NO LETTERS NO WRITING"
3. Focus on visual elements, mood, composition
4. Be specific about style and aesthetic
```

## User Prompt Template

```
Create an image generation prompt for a {{style}} style ad.

CONTEXT:
- Product/Service: {{product_name}}
- Industry: {{industry}}
- Target Audience: {{target_audience}}
- Pain Points: {{pain_points_solved}}
- Tone: {{tone}}

STYLE: {{style}}

Style guidelines:
- meme: Funny reaction image, expressive face/character, relatable situation, internet meme aesthetic
- professional: Clean, minimal, premium feel, soft lighting
- lifestyle: Product in real-world use, authentic, natural
- abstract: Geometric shapes, bold colors, modern design

Return ONLY the image prompt, nothing else. End with "NO TEXT NO WORDS NO LETTERS NO WRITING"
```

## Example Outputs

**For meme style (B2B lead gen channel):**
```
Funny reaction of office worker staring at computer screen in disbelief, exaggerated facial expression, corporate office background, internet meme aesthetic, relatable work situation, expressive eyes, NO TEXT NO WORDS NO LETTERS NO WRITING
```

**For professional style:**
```
Clean minimal product photography, soft gradient background, professional lighting, premium tech aesthetic, centered composition, shallow depth of field, NO TEXT NO WORDS NO LETTERS NO WRITING
```

## Variables

- `{{style}}` - Image style (meme, professional, lifestyle, abstract)
- `{{product_name}}` - Product name
- `{{industry}}` - Industry category
- `{{target_audience}}` - Target audience description
- `{{pain_points_solved}}` - What problems it solves
- `{{tone}}` - Brand tone
