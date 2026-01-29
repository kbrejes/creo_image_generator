# Quick Setup - Copy Paste Everything

## NODE 1: LLM - "Analyze Input"

**SYSTEM:**
```
You analyze ad requests. Return JSON only, nothing else.
```

**USER:**
```
{{#sys.query#}}

Return JSON: {"product":"name","audience":"who","pain":["point1"],"platform":"instagram"}
```

---

## NODE 2: LLM - "Generate Copy"

**SYSTEM:**
```
Write meme ad copy. JSON only. Hook=top text CAPS, body=bottom, cta=call to action.
```

**USER:**
```
{{#Analyze Input.text#}}

Return: {"hook":"TOP TEXT","body":"bottom","cta":"action"}
```

---

## NODE 3: LLM - "Image Prompt"

**SYSTEM:**
```
Create image prompts. NO TEXT IN IMAGE EVER. End with: NO TEXT NO WORDS NO LETTERS
```

**USER:**
```
{{#Analyze Input.text#}}

Meme reaction image for this. Return prompt only.
```

---

## NODE 4: HTTP - "Generate Image"

**Method:** POST

**URL:**
```
https://creo.yourads.io/tools/generate-image
```

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "prompt": "{{#Image Prompt.text#}}",
  "backend": "flux",
  "size": "1024x1024",
  "negative_prompt": "text words letters"
}
```

---

## NODE 5: HTTP - "Compose"

**Method:** POST

**URL:**
```
https://creo.yourads.io/pipeline/compose?image_url={{#Generate Image.body.images[0].url#}}&hook_text={{#Generate Copy.text.hook#}}&body_text={{#Generate Copy.text.body#}}&cta_text={{#Generate Copy.text.cta#}}&output_size=instagram_square
```

---

## NODE 6: LLM - "Response"

**USER:**
```
Ad ready: {{#Compose.body.url#}}
Copy: {{#Generate Copy.text#}}

Format nicely, show URL, ask if they want changes.
```

---

## Connect: Start → Analyze → Copy + Image Prompt → Generate Image → Compose → Response → End
