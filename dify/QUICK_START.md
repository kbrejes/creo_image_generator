# 🚀 Quick Start Guide - Ad Creative Workflow

## 📦 What You Have

### Files Ready to Use
- ✅ `ad_creative_v3.yml` - Working version with fixed fonts
- ✅ `ad_creative_v4.yml` - Enhanced with custom inputs
- ✅ API running at https://creo.yourads.io

### What Works Now
- ✅ Large, readable text overlays (120pt / 60pt / 48pt)
- ✅ Custom font (LiberationSans-Bold) properly scaling
- ✅ Full pipeline: Copy → Image → Compose
- ✅ Both Flux and SDXL backends available

---

## 🎯 V3 vs V4 Comparison

| Feature | V3 (Simple) | V4 (Enhanced) |
|---------|-------------|---------------|
| **Input** | Just product description | 6 custom inputs |
| **Copy Control** | AI only | AI + custom hook override |
| **Image Backend** | Flux only | Flux or SDXL choice |
| **Font Sizes** | Fixed (120/60/48) | Fixed (adjustable in code) |
| **Audience Targeting** | ❌ | ✅ |
| **Style Selection** | ❌ | ✅ (4 styles) |
| **Complexity** | Beginner | Intermediate |

**Recommendation:** Start with V3, upgrade to V4 when you need more control.

---

## 🏃 Quick Start (V3)

### 1. Import to Dify
1. Go to https://dify.yourads.io
2. Click "Create Workflow" or "Import"
3. Upload `ad_creative_v3.yml`
4. Click "Run"

### 2. Test It
```
Input: "AI writing assistant for busy entrepreneurs"
```

Expected output:
- ✅ 3 copy variations in JSON
- ✅ Generated image with excited person
- ✅ Final composed ad with large bold text

### 3. Verify Output
Check the Answer node should show:
- Final image URL with text overlay
- Hook text used
- All copy variations

---

## 🔧 Advanced Start (V4)

### 1. Import V4
Upload `ad_creative_v4.yml` to Dify

### 2. Fill Input Variables
```yaml
Product: "AI writing assistant"
Audience: "content creators and marketers"
Style: "Professional"
Custom Hook: "" (leave empty for AI)
Font Scale: 1.0
Backend: "flux"
```

### 3. Test Variations

**Test 1: AI Everything**
```
Product: "Online fitness coaching"
(All others empty)
```

**Test 2: Custom Hook**
```
Product: "Eco-friendly water bottles"
Custom Hook: "SAVE THE PLANET!"
Style: "Urgent"
```

**Test 3: Different Backend**
```
Product: "Mobile banking app"
Backend: "sdxl"
```

---

## 📊 Node-by-Node Output Guide

### Visual Flow
```
Start → Generate Copy → Parse Copy → Build Prompt → Generate Image
  ↓         (LLM)        (Code)       (LLM)         (HTTP)
  ↓
Parse Image → Compose Ad → Parse Final → Answer
  (Code)       (HTTP)        (Code)      (Output)
```

### What Each Node Does

| Node | What It Does | Output to Check |
|------|-------------|-----------------|
| **1. Start** | Takes user input | Product, audience, style |
| **2. Generate Copy** | AI writes 3 ad variations | JSON with hooks/body/cta |
| **3. Parse Copy** | Extracts best copy, applies custom hook | hook, body, cta, using_custom_hook |
| **4. Build Prompt** | Creates image generation prompt | Description for Flux/SDXL |
| **5. Generate Image** | Calls API to generate image | Image URL in /files/generated/ |
| **6. Parse Image** | Extracts clean URL | image_url (https://...) |
| **7. Compose Ad** | Adds text overlay to image | Final URL in /files/composed/ |
| **8. Parse Final** | Packages outputs | final_url, raw_url, hook, all_copy |
| **9. Answer** | Returns to user | Formatted response |

---

## 🧪 Testing Checklist

### Basic Tests (Must Pass)
- [ ] Import workflow successfully
- [ ] Run with simple product description
- [ ] Get final image with visible text
- [ ] Text is large and readable
- [ ] Image loads in browser

### V4 Advanced Tests
- [ ] Custom hook overrides AI copy
- [ ] Style selection changes tone
- [ ] Backend selection works (flux/sdxl)
- [ ] Audience influences messaging
- [ ] All node outputs are correct

### Edge Cases
- [ ] Very long product description (100+ words)
- [ ] Short description (3 words)
- [ ] Special characters ($, !, @, #)
- [ ] Empty optional fields
- [ ] All fields filled

---

## 🐛 Common Issues & Fixes

### Issue: "404 Not Found" on compose endpoint
**Cause:** Workflow using old `/pipeline/compose` URL
**Fix:** Re-import v3 or v4 (updated to `/tools/compose-ad`)

### Issue: Text still tiny
**Cause:** Font not found, falling back to default
**Fix:** Already fixed in current version (uses LiberationSans-Bold)

### Issue: Custom hook not working (V4)
**Cause:** Variable not connected in Parse Copy node
**Fix:** Check Node 3 has `custom_hook` in variables list

### Issue: Image generation timeout
**Cause:** Flux can be slow (30-60s)
**Fix:** Increase timeout in Node 5 or switch to SDXL backend

### Issue: Backend selection ignored (V4)
**Cause:** Node 5 body still has hardcoded "flux"
**Fix:** Verify body uses `{{#1.backend#}}`

---

## 📈 Performance Tips

### Faster Generation
- Use SDXL instead of Flux (20s vs 60s)
- Reduce image size to 512x512 for drafts
- Simplify prompts (shorter = faster)

### Better Quality
- Use Flux for final output
- Keep prompts detailed but under 50 words
- Test different styles to find what works

### Cost Optimization
- Test with SDXL (cheaper)
- Finalize with Flux (better quality)
- Cache successful prompts

---

## 🎨 Customization Examples

### Change Font Sizes
Edit Node 7 (Compose Ad) params:
```
hook_font_size:160   ← Make hook HUGE
body_font_size:80    ← Make body larger
cta_font_size:64     ← Make CTA prominent
```

### Add Background Color Choice
Add to V4 Start node variables:
```yaml
- label: "Background Color"
  variable: bg_color
  type: select
  options:
    - "bright yellow"
    - "cool blue"
    - "vibrant pink"
    - "clean white"
```

Then update Node 4 prompt:
```
Create image with {{#1.bg_color#}} background
```

### Add More Ad Styles
In V4 Start node, expand style options:
```yaml
options:
  - "Humorous"
  - "Professional"
  - "Urgent"
  - "Educational"
  - "Inspirational"   ← New
  - "Sarcastic"       ← New
  - "Direct Response" ← New
```

---

## 📝 API Direct Testing

### Test Image Generation
```bash
curl -X POST https://creo.yourads.io/tools/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "excited person pointing, yellow background",
    "backend": "flux",
    "size": "1024x1024"
  }'
```

### Test Text Composition
```bash
curl -X POST "https://creo.yourads.io/tools/compose-ad" \
  -d "image_url=<YOUR_IMAGE_URL>" \
  -d "hook_text=CHECK THIS OUT!" \
  -d "cta_text=Learn More" \
  -d "hook_font_size=120" \
  -d "cta_font_size=48"
```

---

## 🚦 Next Steps

### Beginner Path
1. ✅ Import V3 to Dify
2. ✅ Run 3 test variations
3. ✅ Verify text is visible
4. → Start using for real ads

### Intermediate Path
1. ✅ Import V4 to Dify
2. ✅ Test all input variables
3. ✅ Customize font sizes
4. → Add more custom inputs
5. → Build ad library

### Advanced Path
1. ✅ Master V4 inputs
2. → Add Question nodes for review steps
3. → Create multiple workflow variations
4. → Build parallel comparison workflows
5. → Integrate with external tools via webhooks

---

## 📚 Documentation

- **Full Guide**: See `WORKFLOW_GUIDE.md`
- **V4 Features**: See `V4_ENHANCEMENTS.md`
- **API Docs**: https://creo.yourads.io/docs
- **Test Script**: Run `python3 test_workflow.py`

---

## ✅ You're Ready!

**Current Status:**
- ✅ API running and tested
- ✅ Fonts fixed and scaling properly
- ✅ V3 workflow ready (simple)
- ✅ V4 workflow ready (advanced)
- ✅ Comprehensive documentation

**Action Items:**
1. Import workflow to Dify (V3 or V4)
2. Run your first test
3. Adjust font sizes if needed
4. Start creating ads! 🎉

**Need Help?**
- Check node outputs in Dify
- Review troubleshooting section above
- Run `test_workflow.py` to validate API
