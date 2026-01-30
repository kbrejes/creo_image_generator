# V6 Auto URL Fetch - Setup Guide

## 🎯 What V6 Does

Automatically fetches content from URLs using Jina Reader API.

**Just paste:** `https://outreacher.co/guide`
**V6 fetches and extracts:** All content automatically
**Then generates:** Relevant ads

---

## ✅ Current Status

**File ready:** `ad_creative_v6_auto_fetch.yml`

**What's updated:**
- ✅ App metadata (V6 branding)
- ✅ Content Source field (mentions URLs)
- ✅ Opening statement (explains auto-fetch)
- ⏳ Need to add: HTTP Request node for Jina

---

## 🔧 To Complete V6: Add HTTP Fetch Node in Dify

Since workflow structure is complex to edit via YAML, **add this node manually in Dify:**

### Step 1: Import V6 Base
1. Import `ad_creative_v6_auto_fetch.yml` to Dify
2. Open in workflow editor

### Step 2: Add URL Processor Code Node

**After Start node, before Generate Copy:**

1. **Add Code Node**
2. **Name:** "Process Content"
3. **Code:**

```python
import re

def main(content_source: str) -> dict:
    """
    Detects if input is URL and prepares for fetching.
    Returns: processed content or fetch instruction.
    """
    content = content_source.strip()

    # Check if it's a URL
    url_pattern = r'^https?://'
    is_url = bool(re.match(url_pattern, content))

    if is_url:
        # Return Jina API URL for fetching
        jina_url = f"https://r.jina.ai/{content}"
        return {
            "is_url": True,
            "fetch_url": jina_url,
            "original_content": content,
            "processed_content": ""  # Will be filled by HTTP request
        }
    else:
        # It's text content, pass through
        return {
            "is_url": False,
            "fetch_url": "",
            "original_content": content,
            "processed_content": content
        }
```

**Outputs:**
- `is_url` (boolean)
- `fetch_url` (string)
- `processed_content` (string)

### Step 3: Add Conditional HTTP Fetch

**Add IF/ELSE Node:**

**Condition:** `{{#2.is_url#}} == true`

**IF TRUE Branch:**
1. **Add HTTP Request Node**
2. **URL:** `{{#2.fetch_url#}}`
3. **Method:** GET
4. **Timeout:** 30s
5. **Output variable:** `fetched_content`

**IF FALSE Branch:**
- Connect directly to Generate Copy

### Step 4: Merge Results

**Add Code Node** (after HTTP and before Generate Copy):

```python
def main(is_url: bool, fetched_content: str, original_content: str, processed_content: str) -> dict:
    """
    Merges fetched or original content.
    """
    if is_url and fetched_content:
        final_content = fetched_content
    elif processed_content:
        final_content = processed_content
    else:
        final_content = original_content

    return {"final_content": final_content}
```

### Step 5: Update Generate Copy

Change Generate Copy variables to use `{{#merge_node.final_content#}}` instead of `{{#1.content_source#}}`

---

## 🚀 Simpler Alternative (Recommended)

**Since manual node adding is complex, use this workaround:**

### Update Generate Copy Prompt Only

Add preprocessing instruction:

```
TASK 0: URL Handling
If the content source is a URL (starts with http:// or https://):
- First, note that the URL is: [the URL]
- Visit https://r.jina.ai/[the URL] to fetch content
- Then proceed with extraction

If it's text content:
- Proceed directly to extraction

TASK 1: Content Extraction
...rest of prompt...
```

**Then tell users:** "If you paste a URL, first visit `https://r.jina.ai/YOUR_URL` and paste the result"

---

## 📋 Current Best Practice

**For now, V5 + Jina manual fetch works great:**

```
1. User has URL: https://outreacher.co/guide
2. User visits: https://r.jina.ai/https://outreacher.co/guide
3. Copy extracted content
4. Paste in V5 Content Source
5. Generate ads
```

**This is reliable and works immediately.**

---

## 🎯 Full Automation Coming

I can build true automation with:
- Custom API endpoint that handles URL detection
- Server-side Jina fetching
- Clean Dify integration

**Would take 30-45 min to build properly.**

For now, **recommend using V5 + manual Jina fetch** - it's fast and works perfectly!

---

## ✅ What's Ready Now

**Files:**
- ✅ `ad_creative_v5_content.yml` - Content extraction (paste text) - **USE THIS**
- ✅ `ad_creative_v6_auto_fetch.yml` - Base for auto URL (needs manual Dify setup)

**Fixes:**
- ✅ Text overlap fixed (42pt body font)
- ✅ Content extraction working
- ✅ 2-3 sentence body text

**Recommended workflow:**
Use V5 + Jina manual fetch until we build full automation.

Want me to build the server-side URL fetch endpoint for true automation?
