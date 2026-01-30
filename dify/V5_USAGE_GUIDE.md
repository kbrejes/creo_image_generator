# V5 Content Extraction - Usage Guide

## ✅ V5 is Ready!

File: `ad_creative_v5_content.yml`

---

## 🎯 What V5 Does

**Automatically extracts product info from any text and generates ads.**

Paste:
- Website landing pages
- Product descriptions
- Email campaigns
- Competitor ads
- Blog posts
- Sales pitches

V5 will:
1. Extract product name, audience, benefits
2. Generate 3 ad variations
3. Create images with text overlays

---

## 📋 Input Fields

### Primary (Content-Based)
```
Content Source (paragraph):
  Paste your full website copy, landing page text,
  email content, or any product description here.

  Max 5000 characters.
```

### Optional Manual Overrides
```
Product/Service: (auto-extracted if content provided)
Target Audience: (auto-extracted if content provided)
Ad Style: Humorous / Professional / Urgent / Educational
Custom Hook: Override AI hook
Image Generator: flux / sdxl
```

---

## 🚀 Usage Examples

### Example 1: From Landing Page

**Input:**
```
Content Source:
FlowDash - The Project Management Tool Built for Speed

Tired of clunky project management software that slows your team down?
FlowDash is the lightning-fast PM tool built for modern teams who
value speed and simplicity.

✓ Set up in 5 minutes, not 5 days
✓ Real-time collaboration that actually works
✓ AI-powered task prioritization
✓ Integrated time tracking and reporting

Join 15,000+ teams who've boosted productivity by 35% with FlowDash.

Start free → No credit card required

Ad Style: Professional
Message: "create ad"
```

**Expected Output:**
```
Hook: "PROJECT MANAGEMENT AT LIGHTSPEED"
Body: "Set up in 5 minutes with AI-powered prioritization and
       real-time collaboration. Join 15,000+ teams boosting
       productivity by 35%. No credit card needed to start."
CTA: "Try FlowDash"
```

---

### Example 2: From Email Pitch

**Input:**
```
Content Source:
Subject: New AI Writing Assistant for Marketers

Hi there! We built CopyGenius specifically for marketing teams
who need to create high-converting copy fast. Our AI learns
your brand voice and generates blog posts, ads, and emails
in seconds. Early access: 50% off.

Ad Style: Urgent
Message: "emphasize the 50% off offer"
```

**Expected Output:**
```
Hook: "50% OFF AI COPYWRITING"
Body: "CopyGenius learns your brand voice and writes blogs,
       ads & emails in seconds. Built for marketing teams
       who need high-converting copy fast. Early access ends soon."
CTA: "Claim 50% Off"
```

---

### Example 3: Your B2B Channel

**Input:**
```
Content Source:
Канал "Холодные продажи в B2B"

Ежедневные разборы реальных кейсов холодного outreach в B2B сегменте.

Что внутри:
- Готовые скрипты первых касаний, которые дают отклик 15-20%
- Разборы провальных и успешных кампаний
- Тактики для российского рынка (LinkedIn, email, Telegram)
- Инструменты автоматизации outreach

Для кого: руководители отделов продаж, b2b-менеджеры,
предприниматели в digital-сфере

5000+ подписчиков уже применяют наши методики

Ad Style: Urgent
Message: "create ad"
```

**Expected Output:**
```
Hook: "15-20% ОТКЛИК В ХОЛОДНЫХ ПРОДАЖАХ"
Body: "Ежедневные кейсы и готовые скрипты для B2B outreach
       на российском рынке. 5000+ менеджеров уже применяют
       наши методики. Реальные результаты, а не теория."
CTA: "Подписаться"
```

---

### Example 4: Manual Mode (No Content)

**Input:**
```
Content Source: (leave empty)
Product: Custom CRM for real estate agents
Audience: Real estate professionals
Ad Style: Professional
Message: "create ad"
```

**Works like V4** - uses manual inputs instead of extraction.

---

## 🎨 Pro Tips

### 1. Feed Competitor Ads
```
Content Source: [Paste competitor's landing page]
Message: "highlight our advantages over them"
```

### 2. Multiple Variations
```
Content Source: [Same content]
Message: "create 3 different styles"
```

Then run 3 times with different Ad Styles.

### 3. Test Messages
```
Content Source: [Product page]
Message: "focus on pricing benefits"

vs

Message: "emphasize time savings"
```

### 4. Extract from Reviews
```
Content Source:
"I love this tool! Saved me 10 hours a week.
The automation is incredible. Worth every penny."

Message: "use customer voice"
```

---

## 📊 What Gets Extracted

### Automatically Detected:
- ✅ Product/service name
- ✅ Target customer type
- ✅ Key benefits (top 3-5)
- ✅ Pain points solved
- ✅ Social proof (numbers, testimonials)
- ✅ Unique selling points
- ✅ Offers/pricing hints

### Filtered Out:
- ❌ Legal disclaimers
- ❌ Navigation text
- ❌ Generic website copy
- ❌ Competitor mentions (unless you want them)

---

## 🔄 V5 vs V4

| Feature | V4 | V5 |
|---------|----|----|
| **Input Method** | Manual form fields | Paste content OR manual |
| **Product Info** | You type it | Auto-extracted |
| **Benefits** | AI guesses | From your content |
| **Audience** | You specify | Auto-detected |
| **Speed** | Fast | Fast (same) |
| **Control** | High | Very High |
| **Best For** | Known messaging | Research, competitors |

**Use V4:** When you know exactly what to say
**Use V5:** When you have content to analyze

---

## 🐛 Troubleshooting

### "Generated generic copy, not specific to my content"

**Cause:** Content Source field was empty or too short

**Fix:** Make sure you pasted full content (at least 100 words)

### "Extracted wrong product info"

**Cause:** Content was ambiguous or multiple products mentioned

**Fix:** Use manual Product field to override

### "Still asking for product in manual fields"

**Cause:** Both Content Source AND Product fields are empty

**Fix:** Fill at least one - either paste content OR type product name

---

## ✅ Quick Start Checklist

- [ ] Import `ad_creative_v5_content.yml` to Dify
- [ ] Paste sample content in Content Source field
- [ ] Leave Product/Audience empty (let it extract)
- [ ] Select Ad Style
- [ ] Send message: "create ad"
- [ ] Check output matches content
- [ ] Iterate with different messages

---

## 🎉 You're Ready!

V5 is now ready to import and use. Try it with:
1. Your Telegram channel description
2. A competitor's landing page
3. Your own product page

**Next:** Import `ad_creative_v5_content.yml` and test! 🚀
