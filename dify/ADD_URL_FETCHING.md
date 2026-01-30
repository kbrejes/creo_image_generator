# How to Add URL Fetching to V5

## 🎯 Goal
Make V5 fetch and extract content from URLs automatically.

---

## ✅ Quick Method: Add HTTP Request Node in Dify

### Step 1: Add URL Detection Logic

1. Open V5 workflow in Dify
2. Click on **Start** node
3. Update **Content Source** label:
   ```
   "Content Source (paste text OR enter URL)"
   ```

### Step 2: Add HTTP Fetch Node (Optional Path)

**Option A: Simple - Use Jina Reader API** (Recommended)

1. Add new **HTTP Request** node between Start and Generate Copy
2. **Name:** "Fetch URL Content"
3. **URL:** `https://r.jina.ai/{{#1.content_source#}}`
4. **Method:** GET
5. **Headers:** Leave empty

**Why Jina?** Free API that converts any URL to clean markdown text.

**Option B: Use WebFetch Tool**

If available in your Dify:
1. Add **Tool** node
2. Select "WebFetch"
3. **URL:** `{{#1.content_source#}}`
4. **Prompt:** "Extract all text content from this page"

### Step 3: Add Conditional Logic

1. Add **IF/ELSE** node after Start
2. **Condition:** Check if `{{#1.content_source#}}` starts with "http"
3. **If TRUE:** Route to Fetch URL node → Generate Copy
4. **If FALSE:** Route directly to Generate Copy (it's pasted text)

**Condition code:**
```python
def main(content_source: str) -> dict:
    is_url = content_source.strip().startswith(('http://', 'https://'))
    return {"is_url": is_url}
```

### Step 4: Update Generate Copy Node

**Update variables:**
- If from URL fetch: Use fetched content
- If pasted text: Use content_source directly

---

## 🚀 Simpler Alternative: Auto-Detect in Prompt

Just update **Generate Copy** system prompt to handle URLs:

```
TASK 0: URL Detection
If the source content starts with "http://" or "https://",
inform the user to paste the actual page content instead of the URL.
We cannot fetch URLs automatically yet.

TASK 1: Content Extraction
...rest of prompt...
```

This way the LLM will tell users when they paste a URL instead of content.

---

## 🔧 Full Automated Solution (Advanced)

I can create a **V6 workflow** with:
- Automatic URL detection
- Jina Reader integration for fetching
- Fallback to manual text input

**Would you like me to create V6 with full URL support?**

Takes ~15 min to build properly.

---

## 📝 For Now: Manual Workflow

**Current workaround:**

1. Get content from URL:
   - Visit: `https://r.jina.ai/https://outreacher.co/guide`
   - Copy the extracted text

2. Paste into V5 Content Source field

3. Generate ads as normal

**Example:**
```
# Instead of:
Content Source: https://outreacher.co/guide

# Do this:
1. Visit: https://r.jina.ai/https://outreacher.co/guide
2. Copy all the markdown text
3. Paste in Content Source field
```

---

## ✅ What's Fixed Now

- ✅ Body font reduced: 60pt → 42pt (no more overlap!)
- ⏳ URL fetching: Manual for now, automated coming in V6

**Test the font fix** - re-import v4 or v5 and generate again. Body text should be smaller and not overlap faces!

Want me to build V6 with automated URL fetching?
