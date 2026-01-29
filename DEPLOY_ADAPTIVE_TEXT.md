# Deploy Adaptive Text Sizing Fix

## ✅ What's Fixed

The image compositor now automatically adapts text sizing to prevent overlap with faces and subjects in images.

---

## 🔧 Changes Made

### File Updated: `services/image_compositor.py`

**New Features:**

1. **Safe Zone System**
   - Top 30% of image: Hook text only
   - Middle 40%: Kept clear for faces/subjects
   - Bottom 30%: Body text and CTA

2. **Adaptive Font Sizing**
   - Automatically reduces font size if text doesn't fit
   - Calculates optimal size to fit within safe zones
   - Minimum sizes: 24pt (hook), 20pt (body/CTA)
   - Steps down by 2pt increments until text fits

3. **Smart Layout**
   - Proper margins and spacing
   - Text wrapping respects safe zones
   - No overlap with middle section

---

## 🚀 Deployment Steps

### Option 1: SSH to VPS and Deploy

```bash
# 1. SSH to your VPS
ssh user@dify.yourads.io

# 2. Navigate to project directory
cd /path/to/creo_image_generator

# 3. Pull latest changes (if using git)
git pull

# 4. Rebuild and restart
./deploy.sh
```

### Option 2: Deploy from Local (if configured)

```bash
# If you have SSH/rsync configured
rsync -avz /Users/kirill/Documents/Dev\ Dev\ Dev/ACTIVE/creo_image_generator/ \
  user@dify.yourads.io:/path/to/creo_image_generator/

# Then SSH and restart
ssh user@dify.yourads.io "cd /path/to/creo_image_generator && ./deploy.sh"
```

### Option 3: Manual File Copy

1. Copy `services/image_compositor.py` to VPS
2. SSH to VPS
3. Run: `docker compose restart api`

---

## 🧪 Testing After Deployment

### Test 1: Long Hook Text
```bash
curl -X POST "http://dify.yourads.io:8000/tools/compose-ad" \
  -d "image_url=https://your-image.url" \
  -d "hook_text=THIS IS A VERY LONG HOOK TEXT THAT SHOULD AUTOMATICALLY RESIZE TO FIT THE TOP ZONE" \
  -d "body_text=Short body." \
  -d "cta_text=Click Here"
```

**Expected:** Hook text automatically reduces from 120pt to fit in top 30%

### Test 2: Long Body Text
```bash
curl -X POST "http://dify.yourads.io:8000/tools/compose-ad" \
  -d "image_url=https://your-image.url" \
  -d "hook_text=SHORT HOOK" \
  -d "body_text=This is a very long body text with multiple sentences that explains the value proposition and benefits in detail. It should automatically resize to fit within the bottom safe zone without overlapping the middle section where faces typically appear." \
  -d "cta_text=Learn More"
```

**Expected:** Body text reduces from 42pt to fit in bottom 30%

### Test 3: Via Dify Workflow
1. Re-import `ad_creative_v5_content.yml` (no changes needed)
2. Generate an ad with long content
3. Check that text no longer overlaps faces

---

## 📊 How It Works

### Before (Fixed Sizes)
```
┌─────────────────────┐
│ HOOK (120pt fixed)  │ ← Could overflow
│                     │
├─────────────────────┤
│                     │
│   FACE HERE         │ ← Text overlaps!
│                     │
├─────────────────────┤
│ Body (42pt fixed)   │ ← Could overflow
│ CTA (48pt fixed)    │
└─────────────────────┘
```

### After (Adaptive Zones)
```
┌─────────────────────┐
│ HOOK (auto-sized)   │ ← Fits in top 30%
│ ✓ Fits perfectly    │
├─────────────────────┤
│                     │
│   FACE HERE         │ ← Clear middle 40%
│   ✓ No overlap!     │
│                     │
├─────────────────────┤
│ Body (auto-sized)   │ ← Fits in bottom 30%
│ CTA (auto-sized)    │
└─────────────────────┘
```

---

## 🎯 Algorithm Details

For each text block (hook, body, CTA):

1. **Allocate space**: Top 30% or Bottom 30% minus padding
2. **Try font sizes**: Start at requested size (e.g., 120pt)
3. **Wrap text**: Calculate how many lines needed
4. **Check height**: Does wrapped text fit in allocated space?
5. **Reduce if needed**: Step down by 2pt and try again
6. **Stop when fits**: Use largest size that fits
7. **Minimum**: Never go below 24pt (hook) or 20pt (body/CTA)

---

## ✅ Verification

After deployment, check:

- [ ] API container restarted successfully
- [ ] Health check passes: `curl http://dify.yourads.io:8000/health`
- [ ] Generate test ad with long text
- [ ] Verify no text overlap with middle section
- [ ] Confirm text is readable (not too small)

---

## 🐛 Troubleshooting

**Problem:** Text still overlaps
- Check that container actually restarted
- Verify `image_compositor.py` has the new code
- Check logs: `docker logs creo_image_generator-api-1`

**Problem:** Text too small to read
- The minimum sizes are 24pt (hook) and 20pt (body/CTA)
- If text is extremely long, consider shortening in the prompt

**Problem:** Container won't start
- Check logs: `docker logs creo_image_generator-api-1`
- Verify no syntax errors in Python code
- Try: `docker compose down && docker compose up -d --build`

---

## 📝 Files Changed

- ✅ `services/image_compositor.py` - Adaptive text sizing implementation
- ✅ `dify/ad_creative_v5_content.yml` - Already updated (100k char limit)

**No other changes needed!**

---

## 🎉 Ready to Deploy

The code is ready. Just deploy to your VPS and the text overlap issue will be fixed!
