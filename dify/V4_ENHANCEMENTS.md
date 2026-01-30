# Ad Creative Workflow v4 - Enhancements Summary

## What's New in V4

### ✅ Custom Input Variables

The Start node now accepts these inputs:

1. **Product/Service** (Required)
   - Main product description
   - Used by AI to generate relevant copy and images

2. **Target Audience** (Optional)
   - Who this ad is for (e.g., "marketers", "fitness enthusiasts")
   - Helps AI tailor the messaging

3. **Ad Style** (Optional)
   - Select from: Humorous, Professional, Urgent, Educational
   - Influences the tone of generated copy

4. **Custom Hook Text** (Optional)
   - Override AI-generated hook with your own text
   - If provided, this will be used instead of AI copy
   - Example: "LIMITED TIME OFFER!"

5. **Font Size Scale** (Optional)
   - Number multiplier for font sizes (default: 1.0)
   - 1.5 = 50% larger text
   - 0.8 = 20% smaller text
   - **Note**: Currently not automatically applied - see manual adjustment below

6. **Image Generator** (Optional)
   - Choose between "flux" (default) or "sdxl"
   - Flux: Better quality, slower
   - SDXL: Faster, good quality

---

## How to Use V4

### Basic Usage
1. Import `ad_creative_v4.yml` into Dify
2. Fill in at minimum the "Product/Service" field
3. Leave others empty to use AI defaults
4. Run workflow

### Advanced Usage

**Example 1: Full Control**
```
Product: AI writing assistant for content creators
Audience: Social media managers and bloggers
Style: Professional
Custom Hook: WRITE 10X FASTER
Backend: flux
```

**Example 2: Quick Test**
```
Product: Eco-friendly water bottles
(Leave all others empty)
```

**Example 3: Custom Hook Override**
```
Product: Online fitness coaching
Custom Hook: GET FIT IN 30 DAYS!
Style: Urgent
```

---

## Testing Your Workflow

### 1. Test Each Node Output

In Dify, run the workflow and click on each node to inspect:

**Node 2 (Generate Copy)**
- Should output JSON with 3 variations + best
- Check if style/audience influenced the copy
- Example output:
```json
{
  "variations": [...],
  "best": {
    "hook": "STOP WASTING TIME!",
    "body": "AI writes your content in seconds",
    "cta": "Try Free"
  }
}
```

**Node 3 (Parse Copy)**
- Should extract hook, body, cta
- If custom_hook was provided, hook should match your input
- Check `using_custom_hook` output (true/false)

**Node 4 (Build Prompt)**
- Should output image description
- Check for: person, emotion, background color
- Should NOT include text/words in prompt

**Node 5 (Generate Image)**
- Check response body for success=true
- Verify image URL is accessible
- Response includes backend used (flux/sdxl)

**Node 6 (Parse Image)**
- Should extract clean image URL
- URL should start with https://creo.yourads.io

**Node 7 (Compose Ad)**
- Should return success=true
- Final image URL should be different (in /composed/)
- Size should be 1080x1080

**Node 8 (Parse Final)**
- Returns final_url, raw_url, hook, all_copy
- All fields should be populated

---

## Manual Font Size Adjustment

Since Dify doesn't support mathematical expressions in params, to change font sizes:

1. Edit the workflow in Dify
2. Click on "Compose Ad" node (Node 7)
3. Find the `params` field
4. Modify these values:
   ```
   hook_font_size:120    ← Change to 150 for larger
   body_font_size:60     ← Change to 75 for larger
   cta_font_size:48      ← Change to 60 for larger
   ```

**Recommended Sizes:**
- **Small**: hook=80, body=48, cta=32
- **Default**: hook=120, body=60, cta=48
- **Large**: hook=160, body=80, cta=64
- **X-Large**: hook=200, body=100, cta=80

---

## Intermediate Editing (Between Nodes)

### Option 1: Manual Pause & Edit

1. Run workflow and let it complete
2. Note the outputs from each node
3. If you want different copy:
   - Go back to Node 3 (Parse Copy)
   - Set `custom_hook` parameter manually in code
4. Re-run from that node forward

### Option 2: Add Question Nodes (Advanced)

To add interactive review points:

1. In Dify, add a **Question** node after Node 3:
   ```yaml
   Question: "Generated hook: {{#3.hook#}}. Use this?"
   Options:
     - "Yes, continue"
     - "No, let me edit"
   ```

2. Create two paths:
   - Path A: Direct to Node 4 (continue)
   - Path B: To a Template node where you manually input hook

This requires restructuring edges - advanced Dify workflow editing.

### Option 3: Variable Override Pattern

Add a Code node that checks for variables:
```python
def main(ai_generated: str, manual_override: str) -> dict:
    final_value = manual_override if manual_override else ai_generated
    return {"result": final_value}
```

---

## Comprehensive Test Suite

### Test Cases

| Test | Input | Expected Output |
|------|-------|-----------------|
| **Basic** | "AI writing tool" | Image with excited person + hook about AI |
| **Custom Hook** | Product: "Fitness app"<br>Hook: "LOSE WEIGHT NOW!" | Image with "LOSE WEIGHT NOW!" text |
| **Style Override** | Style: Professional | More formal copy tone |
| **Backend Switch** | Backend: sdxl | Image generated with SDXL |
| **Long Text** | Hook: "This is a very long hook text that should wrap properly..." | Text wraps properly, stays visible |
| **Special Chars** | "Product: $99 Deal!" | Handles $ and ! correctly |

### Running Tests

Use the provided test script:
```bash
cd /path/to/creo_image_generator
python3 test_workflow.py
```

This tests:
- ✅ API health
- ✅ Image generation (flux/sdxl)
- ✅ Text composition
- ✅ Font size variations
- ✅ Full pipeline

---

## API Endpoint Reference

### 1. Generate Image
```
POST https://creo.yourads.io/tools/generate-image
Body: {
  "prompt": "description",
  "backend": "flux" | "sdxl",
  "size": "1024x1024"
}
```

### 2. Compose Ad
```
POST https://creo.yourads.io/tools/compose-ad
Params:
  - image_url: string
  - hook_text: string
  - body_text: string (optional)
  - cta_text: string (optional)
  - output_size: "instagram_square" | "instagram_story" | etc
  - hook_font_size: int (default: 120)
  - body_font_size: int (default: 60)
  - cta_font_size: int (default: 48)
```

---

## Troubleshooting

### Issue: Text too small
**Solution**: Edit Compose Ad node params, increase font sizes to 160/80/64

### Issue: Custom hook not working
**Solution**: Check Node 3 output - verify `using_custom_hook` is true

### Issue: Image generation fails
**Solution**: Check Node 5 response for error message. May need to retry or switch backend.

### Issue: Backend selection not working
**Solution**: Verify Node 5 body data uses `{{#1.backend#}}` not hardcoded "flux"

### Issue: Font doesn't scale
**Solution**: Font scale input variable requires manual calculation. Use the manual adjustment method above.

---

## Next Steps

1. **Import V4 workflow** into Dify
2. **Run test cases** with different inputs
3. **Adjust font sizes** manually if needed
4. **Monitor Node outputs** to verify each step
5. **Iterate on prompts** in Nodes 2 and 4 for better results

---

## Advanced: Adding More Controls

### Add Color Selection

In Node 4 (Build Prompt), update prompt:
```
Create image with {{#1.bg_color#}} background
```

Then add to Start node:
```yaml
- label: "Background Color"
  variable: bg_color
  type: select
  options:
    - "bright yellow"
    - "cool blue"
    - "vibrant pink"
```

### Add Output Format Selection

In Node 7 (Compose Ad), change params:
```
output_size:{{#1.output_format#}}
```

Add to Start node:
```yaml
- label: "Output Format"
  variable: output_format
  type: select
  options:
    - "instagram_square"
    - "instagram_story"
    - "facebook_feed"
```

---

## Summary

✅ **Done:**
- Enhanced input variables (product, audience, style, custom hook, backend)
- Custom hook override logic
- Backend selection (flux/sdxl)
- Comprehensive testing
- Documentation

⏸️ **Manual Steps Required:**
- Font size adjustment (edit params directly)
- Adding Question nodes for interactive review (advanced)

🎯 **Result:**
You now have full control over the ad creative generation process with multiple input options!
