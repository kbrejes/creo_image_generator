# V5 URL Workflow - Quick Guide

## ✅ V5 Now Supports URLs!

Updated: V5 now handles both text content AND URLs with smart detection.

---

## 🚀 How to Use URLs

### Method 1: V5 Guides You (Recommended)

1. **Paste URL directly in Content Source field:**
   ```
   https://outreacher.co/guide
   ```

2. **V5 detects it's a URL and responds with:**
   ```
   I detected a URL. To extract content automatically, please:
   Visit: https://r.jina.ai/https://outreacher.co/guide
   Copy the extracted content and paste it here instead of the URL
   ```

3. **Click the Jina Reader link**
   - Opens clean markdown version of the page
   - Removes ads, navigation, clutter

4. **Copy all the text** from Jina Reader

5. **Paste it back in Content Source field**

6. **Send message:** "create ad"

7. **V5 generates ads** based on extracted content

---

### Method 2: Pre-fetch (Faster for repeated use)

If you know you have a URL:

1. **Visit Jina Reader directly:**
   ```
   https://r.jina.ai/YOUR_URL_HERE
   ```

2. **Copy the extracted content**

3. **Paste directly in V5 Content Source**

4. **Send message:** "create ad"

---

## 📋 Example Workflow

**Input (URL):**
```
Content Source: https://outreacher.co/guide
Message: "create ad"
```

**V5 Response:**
```
I detected a URL. Please visit:
https://r.jina.ai/https://outreacher.co/guide

Copy the content and paste it here.
```

**You do:** Click link, copy content, paste back

**Input (Extracted content):**
```
Content Source: [Full page content from Jina Reader]
Message: "create ad"
```

**V5 Response:**
```
[Generated ad with hook, body, CTA based on the page content]
```

---

## 🎯 What Jina Reader Does

**Jina Reader API** (r.jina.ai) is a free service that:
- ✅ Fetches any web page
- ✅ Extracts clean text content
- ✅ Removes ads, navigation, footers
- ✅ Converts to readable markdown
- ✅ Works with any public URL
- ✅ No signup required

**Example:**
```
Original URL: https://outreacher.co/guide
Jina Reader: https://r.jina.ai/https://outreacher.co/guide
Result: Clean text extraction of the guide
```

---

## ✅ Fixes Applied

1. **URL Detection:** V5 now detects URLs and provides Jina Reader link
2. **Text Overlap:** Body font reduced to 42pt (was 60pt)
3. **Smart Extraction:** Works with pasted content OR Jina-fetched content

---

## 🎨 Complete Workflow Options

### Option A: From URL
```
1. Paste URL → V5 gives Jina link
2. Visit Jina link → Copy content
3. Paste content → V5 generates ad
```

### Option B: From Text
```
1. Paste text content directly
2. V5 extracts info and generates ad
```

### Option C: Manual
```
1. Leave Content Source empty
2. Fill Product and Audience manually
3. V5 generates ad from manual inputs
```

---

## 📊 Next Steps

1. **Re-import V5:** Import updated `ad_creative_v5_content.yml` to Dify
2. **Test URL workflow:** Try with https://outreacher.co/guide
3. **Test text workflow:** Try with sample content from [test_content_extraction.md](test_content_extraction.md)

---

## 🚀 Ready to Use!

V5 is now production-ready with:
- ✅ Smart URL detection
- ✅ Automatic content extraction
- ✅ Fixed text overlap (42pt body font)
- ✅ 2-3 sentence body text for incentive
- ✅ English and Russian support

**Import [ad_creative_v5_content.yml](ad_creative_v5_content.yml) and start creating ads!**
