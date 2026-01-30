# How to Add Content Extraction to V4

## 🎯 Goal
Turn your V4 workflow into V5 by adding automatic content extraction.

---

## ✅ Quick Method: Modify V4 in Dify UI

### Step 1: Add Content Input Field

1. Open your V4 workflow in Dify
2. Click on **Start** node
3. **Add new variable:**
   ```
   Label: "Content Source (paste website copy, email, or product description)"
   Variable name: content_source
   Type: paragraph (multi-line text)
   Required: false
   ```

4. **Keep existing fields** or make them optional:
   - Product/Service → Optional
   - Target Audience → Optional
   - Ad Style → Keep
   - Custom Hook → Keep
   - Image Generator → Keep

### Step 2: Add Content Extraction Node

1. **Add new LLM node** between Start (Node 1) and Generate Copy (Node 2)
2. **Name it:** "Extract Info"
3. **Connect:** Start → Extract Info → Generate Copy

**System Prompt:**
```
You are an expert content analyzer. Extract key information from the provided content.

Analyze and extract:
1. Product/Service name and type
2. Target audience/customer
3. Main benefits (3-5 key points)
4. Pain points addressed
5. Unique value proposition
6. Any social proof (numbers, testimonials)

Output JSON only:
{
  "product": "...",
  "audience": "...",
  "benefits": ["...", "...", "..."],
  "pain_points": ["...", "..."],
  "value_prop": "...",
  "social_proof": "..."
}
```

**User Prompt:**
```
Content to analyze:
{{#1.content_source#}}

If content is empty, use these manual inputs instead:
- Product: {{#1.product#}}
- Audience: {{#1.audience#}}
```

**Variables to add:**
- content_source (from Node 1)
- product (from Node 1)
- audience (from Node 1)

**Outputs:**
Define these output variables:
- product (string)
- audience (string)
- benefits (string)
- value_prop (string)

### Step 3: Update Generate Copy Node

1. Click on **Generate Copy** node (currently Node 2, will be Node 3)
2. **Update User Prompt** to use extracted info:

**Old prompt:**
```
Product: {{#1.product#}}
Target Audience: {{#1.audience#}}
Desired Style: {{#1.style#}}

Additional Instructions: {{#sys.query#}}
```

**New prompt:**
```
Product: {{#2.product#}}
Target Audience: {{#2.audience#}}
Key Benefits: {{#2.benefits#}}
Value Proposition: {{#2.value_prop#}}
Desired Style: {{#1.style#}}

Additional Instructions: {{#sys.query#}}
```

3. **Update Variables** in Generate Copy node:
   - Add: product (from Node 2 - Extract Info)
   - Add: audience (from Node 2)
   - Add: benefits (from Node 2)
   - Add: value_prop (from Node 2)
   - Keep: style (from Node 1 - Start)
   - Keep: query (from sys)

---

## 🎨 Usage

### With Content Extraction:
```
Content Source: [Paste full landing page copy or email]
Ad Style: Professional
Custom Hook: (leave empty)

Message: "create 3 variations"
```

### Without Content (Manual):
```
Content Source: (leave empty)
Product: Your product name
Audience: Your target audience
Ad Style: Professional

Message: "create ad"
```

---

## 🔄 Alternative: Simpler Approach

If the above is too complex, **just update Generate Copy prompt** in V4:

**New System Prompt:**
```
You are an expert ad copywriter for "ugly ads" / meme-style ads.

If source content is provided, extract product info from it first.
Otherwise, use the manual inputs provided.

Generate 3 ad copy variations with:
- hook: Provocative opening (SHORT, 5-10 words max)
- body: Value proposition (2-3 sentences with benefits)
- cta: Call to action (2-4 words)

Output JSON only.
```

**New User Prompt:**
```
Source Content (if provided):
{{#1.content_source#}}

Manual Inputs:
- Product: {{#1.product#}}
- Audience: {{#1.audience#}}
- Style: {{#1.style#}}

Additional Instructions: {{#sys.query#}}
```

This way, the LLM will extract info automatically if content is provided, or use manual inputs if not.

---

## 📊 Test Cases

### Test 1: From Content
```
Content Source:
"TaskMaster - All-in-one productivity tool for remote teams.
Tasks, docs, chat, and calendar in one place.
Join 50,000+ teams saving 10+ hours per week."

Ad Style: Professional
Message: "create ad"
```

**Expected:**
- Extracts: TaskMaster, remote teams, productivity benefits
- Generates relevant ad copy

### Test 2: Manual Override
```
Content Source: (empty)
Product: My Custom Product
Audience: Entrepreneurs
Ad Style: Urgent
Message: "create ad"
```

**Expected:**
- Uses manual inputs
- Works like V4

---

## 🚀 Which Approach?

**Complex (Full Extraction Node):**
- ✅ Better extraction quality
- ✅ Reusable extracted data
- ✅ Easier to debug
- ❌ More setup work

**Simple (Updated Prompt):**
- ✅ Quick 5-minute setup
- ✅ Works immediately
- ❌ Less control over extraction

**I recommend: Start with Simple, upgrade to Complex if needed.**

Want me to create the fully automated DSL file for you? Or try the simple approach first?
