# Ad Creative Workflow Guide

## Current Workflow (v3)

### Node Flow
1. **Start** → Takes user input (product description)
2. **Generate Copy (LLM)** → Creates 3 ad copy variations with hook/body/cta
3. **Parse Copy (Code)** → Extracts the "best" variation
4. **Build Prompt (LLM)** → Creates Flux image prompt based on hook
5. **Generate Image (HTTP)** → Calls `/tools/generate-image` API
6. **Parse Image (Code)** → Extracts image URL from response
7. **Compose Ad (HTTP)** → Calls `/tools/compose-ad` to add text overlay
8. **Parse Final (Code)** → Extracts final composed image URL
9. **Answer** → Returns final image and copy to user

### Current Inputs
- **User Query**: Product/service description (e.g., "AI writing assistant for marketers")

### Current Outputs
- Final ad creative image with text overlay
- Hook text
- All copy variations (JSON)

---

## Testing the Workflow

### Test Cases

1. **Basic Product Test**
   - Input: "AI writing tool for content creators"
   - Expected: Image with excited person + "AI WRITING TOOL" text + CTA

2. **Service Test**
   - Input: "Online fitness coaching platform"
   - Expected: Image with energetic person + fitness-related hook

3. **E-commerce Test**
   - Input: "Eco-friendly water bottles"
   - Expected: Image with person + product benefit hook

4. **Edge Cases**
   - Very long product description (test text wrapping)
   - Short description (test if it generates enough context)
   - Special characters in product name

### How to Test in Dify

1. Go to your workflow in Dify
2. Click "Run" or "Preview"
3. Enter product description
4. Observe each node's output:
   - Check "Generate Copy" output for JSON format
   - Check "Build Prompt" for image description
   - Check "Generate Image" for image URL
   - Check "Compose Ad" for final image with text

---

## Adding Custom Inputs

### Available Input Options

You can add these to the **Start** node variables:

```yaml
variables:
  - label: "Product Description"
    variable: "product"
    type: "text-input"
    required: true

  - label: "Target Audience"
    variable: "audience"
    type: "text-input"
    required: false

  - label: "Ad Style"
    variable: "style"
    type: "select"
    options:
      - "Humorous"
      - "Professional"
      - "Urgent"
      - "Educational"
    required: false

  - label: "Background Color Preference"
    variable: "bg_color"
    type: "select"
    options:
      - "Bright (yellow, orange, pink)"
      - "Cool (blue, purple, teal)"
      - "Neutral (white, gray)"
    required: false

  - label: "Font Size Multiplier"
    variable: "font_multiplier"
    type: "number"
    required: false
    default: 1.0

  - label: "Custom Hook (Override AI)"
    variable: "custom_hook"
    type: "text-input"
    required: false
```

### Using Custom Inputs

Update prompts to reference these variables:
- In "Generate Copy" node: `Product: {{#1.product#}}, Audience: {{#1.audience#}}, Style: {{#1.style#}}`
- In "Build Prompt" node: Include `{{#1.bg_color#}}` preference
- In "Compose Ad" node: Use `{{#1.font_multiplier#}}` to scale font sizes

---

## Intermediate Editing (Between Nodes)

### Option 1: Question Nodes (Interactive)

Add **Question** nodes after key steps:

**After Generate Copy (Node 3)**
```yaml
- type: question
  title: "Review Copy"
  question: "Generated copy: {{#3.hook#}} / {{#3.cta#}}. Want to modify?"
  options:
    - "Use as-is"
    - "Edit hook"
    - "Edit CTA"
    - "Regenerate all"
```

**After Generate Image (Node 6)**
```yaml
- type: question
  title: "Review Image"
  question: "Image URL: {{#6.image_url#}}. Satisfied with image?"
  options:
    - "Use this image"
    - "Regenerate with different prompt"
    - "Try different style"
```

### Option 2: Parameter Override Nodes

Add **Code** nodes that check for overrides:

```python
def main(generated_hook: str, custom_hook: str) -> dict:
    # Use custom if provided, otherwise use generated
    final_hook = custom_hook if custom_hook else generated_hook
    return {"hook": final_hook}
```

### Option 3: Parallel Branches

Create multiple paths:
- Path A: Automatic (no editing)
- Path B: Manual review at each step
- User selects path at start

---

## Advanced Controls

### Font Size Control
Modify "Compose Ad" params to accept variables:
```
hook_font_size:{{#1.font_multiplier#}}*120
body_font_size:{{#1.font_multiplier#}}*60
cta_font_size:{{#1.font_multiplier#}}*48
```

### Image Backend Selection
Add to Start node:
```yaml
- label: "Image Generator"
  variable: "backend"
  type: "select"
  options:
    - "flux"
    - "sdxl"
```

Use in Generate Image params: `backend={{#1.backend#}}`

### Output Format Control
Add to Compose Ad:
```yaml
- label: "Output Size"
  variable: "output_size"
  type: "select"
  options:
    - "instagram_square"
    - "instagram_story"
    - "facebook_feed"
```

---

## Workflow Testing Checklist

- [ ] Test with 3+ different product types
- [ ] Verify JSON parsing in Parse Copy node
- [ ] Check image generation succeeds (200 OK)
- [ ] Verify text overlay is visible and properly sized
- [ ] Test with long product descriptions (50+ words)
- [ ] Test with short descriptions (5 words)
- [ ] Check error handling if API fails
- [ ] Verify all outputs are returned to user

---

## Next Steps

1. **Create v4 workflow** with input variables
2. **Add Question nodes** for interactive editing
3. **Test comprehensively** with different inputs
4. **Monitor API logs** for errors
5. **Add error handling** Code nodes

Let me know which enhancements you want to implement first!
