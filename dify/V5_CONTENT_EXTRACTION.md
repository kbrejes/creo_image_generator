# V5 - Content-Based Ad Generation

## 🎯 New Capability

Generate ads by feeding:
- Website URLs (landing pages, product pages, articles)
- Raw text (emails, documents, descriptions)
- Social media posts

The workflow will:
1. Extract key information automatically
2. Identify product/service, benefits, target audience
3. Generate relevant ad creatives

---

## 📋 V5 Workflow Architecture

```
Start (with content input)
  ↓
Extract Content (LLM or HTTP + LLM)
  ↓
Generate Copy (using extracted info)
  ↓
Parse Copy
  ↓
Build Image Prompt
  ↓
Generate Image
  ↓
Compose Ad
  ↓
Answer
```

---

## 🔧 Two Approaches

### Approach 1: Simple Text Input (Quick)
**Best for:** Copy-pasted text, emails, documents

**Input Fields:**
- Content Source (text area)
- Ad Style (optional)
- Custom Hook (optional)

**Process:**
```
User pastes:
"Introducing FlowSync - the ultimate project management
tool for remote teams. Automate your workflows,
collaborate in real-time, and boost productivity by 40%."

Workflow extracts:
- Product: FlowSync project management tool
- Audience: Remote teams
- Benefits: Automation, real-time collaboration, 40% productivity boost
```

### Approach 2: URL + Web Fetch (Advanced)
**Best for:** Landing pages, competitor sites, articles

**Input Fields:**
- Website URL
- Ad Style (optional)
- Custom Hook (optional)

**Process:**
```
User provides:
https://competitor.com/product

Workflow:
1. Fetches page content
2. Extracts product info
3. Generates ads
```

---

## 🚀 Implementation Plan

### Phase 1: Text Input (Today)
- ✅ Add "Content Source" text field
- ✅ Add "Extract Info" LLM node
- ✅ Update Generate Copy to use extracted info
- ✅ Keep all existing features

### Phase 2: URL Support (Later)
- Add HTTP Request node for web fetching
- Add HTML → text extraction
- Handle different content types

---

## 📝 V5 Input Fields

```yaml
1. Content Source (text area, required)
   "Paste your website copy, email, or product description"

2. Extraction Mode (select, optional)
   - "Auto-detect product info"
   - "Use as-is for context"

3. Ad Style (select, optional)
   - Humorous
   - Professional
   - Urgent
   - Educational

4. Custom Hook (text, optional)
   "Override AI-generated hook"

5. Target Audience Override (text, optional)
   "Specify if extraction missed it"

6. Image Generator (select, optional)
   - flux
   - sdxl
```

---

## 🎯 Example Usage

### Example 1: Landing Page Copy
**Input:**
```
Tired of juggling multiple tools? TaskMaster brings everything
together - tasks, docs, chat, and calendar in one place.
Join 50,000+ teams saving 10+ hours per week.
```

**Extracted:**
- Product: TaskMaster (all-in-one productivity tool)
- Audience: Teams managing multiple tools
- Benefits: Unified workspace, saves 10+ hours/week
- Social proof: 50,000+ teams

**Generated Ad:**
```
Hook: "STOP TOOL CHAOS"
Body: "TaskMaster unites tasks, docs, chat & calendar in one place.
      Join 50,000+ teams already saving 10+ hours weekly.
      Everything you need, zero switching."
CTA: "Try TaskMaster"
```

### Example 2: Email Pitch
**Input:**
```
Subject: New AI Writing Assistant for Marketers

Hi there! We built CopyGenius specifically for marketing teams
who need to create high-converting copy fast. Our AI learns
your brand voice and generates blog posts, ads, and emails
in seconds. Early access: 50% off.
```

**Extracted:**
- Product: CopyGenius AI writing assistant
- Audience: Marketing teams
- Benefits: Fast copy creation, learns brand voice, multiple formats
- Offer: 50% off early access

**Generated Ad:**
```
Hook: "MARKETING COPY IN SECONDS"
Body: "CopyGenius AI learns your brand voice and writes blogs,
      ads & emails instantly. Built for marketing teams who
      need high-converting copy fast. Early access 50% off."
CTA: "Get CopyGenius"
```

---

## 💡 Smart Extraction Features

### What V5 Will Extract:
- ✅ Product/service name
- ✅ Target audience/customer type
- ✅ Key benefits (3-5 main points)
- ✅ Pain points addressed
- ✅ Social proof (numbers, testimonials)
- ✅ Unique value proposition
- ✅ Pricing/offer details

### What It Won't Extract:
- ❌ Competitor mentions (filtered out)
- ❌ Legal disclaimers
- ❌ Navigation/UI text
- ❌ Irrelevant footer content

---

## 🔄 Workflow Comparison

| Feature | V3 | V4 | V5 |
|---------|----|----|-----|
| Input | Chat message | Form fields | Content extraction |
| Product info | Manual | Manual | Auto-extracted |
| Audience | Manual | Manual | Auto-detected |
| Benefits | AI guesses | Manual hints | From content |
| Body text | 2-3 sentences | 2-3 sentences | 2-3 sentences |
| Custom hook | ❌ | ✅ | ✅ |
| URL support | ❌ | ❌ | Coming Phase 2 |

---

## 🎨 Use Cases

### Perfect for V5:
- ✅ Competitor research → Generate ads from their landing pages
- ✅ Email campaigns → Turn pitch emails into ads
- ✅ Product launches → Use announcement copy
- ✅ Blog posts → Extract key points, make ads
- ✅ Sales decks → Convert slides to ads

### Still use V4 for:
- Manual fine-tuning
- When you know exact messaging
- Quick tests without source material

---

## 🚀 Next Steps

1. **I'll create V5 workflow** with content extraction
2. **You test with sample content** (website copy or text)
3. **We iterate** based on extraction quality
4. **Phase 2:** Add URL fetching

Ready to build V5? Send me a sample text/website you want to turn into an ad!
