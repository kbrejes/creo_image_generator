# V4 Workflow - Correct Usage

## ❌ What Was Wrong

The workflow was ignoring your form inputs and using your chat message instead.

**Example of the bug:**
```
Form Fields Filled:
  Product: "Telegram Channel about B2B Outreach"
  Audience: "russian digital and b2b entrepreneurs"
  Style: "Professional"

Chat Message: "сделай креатив"

Result: Workflow used "сделай креатив" instead of form data → generic output
```

## ✅ What's Fixed

Updated workflow to properly read form variables:
- `{{#sys.query#}}` → `{{#1.product#}}` (uses form product field)
- Opening message now explains form usage

## 📋 How to Use V4 Correctly

### Step 1: Import Updated Workflow
1. Go to Dify
2. Re-import `ad_creative_v4.yml` (overwrite the old one)

### Step 2: Fill Form Fields
**Required:**
- Product/Service: `Telegram Channel about B2B Outreach`

**Optional but Recommended:**
- Target Audience: `russian digital and b2b entrepreneurs`
- Ad Style: `Professional`
- Image Generator: `flux`

**Leave Empty:**
- Custom Hook (unless you want to override)
- Font Size Scale (defaults to 1.0)

### Step 3: Send Any Message
After filling the form, send ANY message to trigger the workflow:
- ✅ "go"
- ✅ "generate"
- ✅ "create ad"
- ✅ "сделай креатив"

The actual message content doesn't matter - the workflow reads from the form fields!

## 🎯 Expected Output

With your inputs:
```
Product: "Telegram Channel about B2B Outreach"
Audience: "russian digital and b2b entrepreneurs"
Style: "Professional"
```

**Should generate:**
- Hook about B2B outreach/Telegram
- Professional tone (not humorous)
- Relevant to Russian entrepreneurs
- Example: "MASTER B2B OUTREACH!" or "TELEGRAM SECRETS FOR B2B!"

## 🔍 Verify It's Working

**Check Node 2 (Generate Copy) output:**
Should reference:
- ✅ B2B outreach
- ✅ Telegram
- ✅ Professional tone
- ✅ Russian/entrepreneur context

**If you see generic "Check this out!" text:**
- ❌ Workflow is not reading form fields
- → Re-import updated v4.yml

## 📝 Full Example

### Input Form
```yaml
Product: Telegram Channel about B2B Outreach
Audience: russian digital and b2b entrepreneurs
Style: Professional
Custom Hook: (empty)
Font Scale: (empty)
Backend: flux
```

### Chat Message
```
создай объявление
```

### Expected Copy Output
```json
{
  "best": {
    "hook": "MASTER B2B OUTREACH ON TELEGRAM",
    "body": "Join 5000+ Russian entrepreneurs learning proven outreach strategies",
    "cta": "Join Channel"
  }
}
```

### Expected Image
- Professional business person
- Solid background (blue/gray for professional)
- Excited but professional expression

### Expected Final Ad
- Large text: "MASTER B2B OUTREACH ON TELEGRAM"
- Bottom text: "Join Channel"
- White text with black outline

## 🐛 Troubleshooting

### Still Getting Generic Output?

**1. Verify form fields are filled BEFORE sending message**
   - Fill all fields first
   - Then send chat message

**2. Check Node 2 output in Dify**
   - Click on "Generate Copy" node after run
   - Look at the prompt sent to AI
   - Should show: "Product: Telegram Channel about B2B Outreach"
   - Should NOT show: "Product: создай объявление"

**3. Re-import the workflow**
   - Delete old v4 workflow in Dify
   - Import fresh copy from `ad_creative_v4.yml`

### Form Fields Not Showing?

- Make sure you imported V4, not V3
- V3 doesn't have form fields
- V4 has 6 form fields in Start node

## ✅ Test Cases

### Test 1: Your B2B Telegram Channel
```
Product: Telegram Channel about B2B Outreach
Audience: russian digital and b2b entrepreneurs
Style: Professional
Message: "go"
```
**Expected:** Professional B2B-focused ad

### Test 2: Custom Hook Override
```
Product: Telegram Channel about B2B Outreach
Audience: russian digital and b2b entrepreneurs
Style: Professional
Custom Hook: ПОЛУЧИ 100 ЛИДОВ В МЕСЯЦ
Message: "generate"
```
**Expected:** Uses your custom hook exactly

### Test 3: Different Style
```
Product: Same as above
Style: Humorous
Message: "create"
```
**Expected:** Funny/casual tone instead of professional

## 🎉 Now It Should Work!

Re-import the updated v4 workflow and try again with the same inputs. You should get a B2B-focused professional ad this time!
