# Debug V4 - Step-by-Step Verification

## 🔍 What I Just Fixed

### Issue 1: Wrong Variable References
**Lines 170, 280:** `{{#sys.query#}}` → `{{#1.product#}}`
- Was reading chat message instead of form field

### Issue 2: Missing Variable Declarations
**Lines 202, 323:** Added explicit variable declarations
- Dify needs these to know which variables to pass to LLM nodes

## ✅ Step-by-Step Fix Verification

### Step 1: Delete Old Workflow in Dify
1. Go to Dify
2. Find "Ad Creative Agent v4 (Enhanced)"
3. Click Delete/Remove
4. Confirm deletion

### Step 2: Import Fresh Copy
1. Download/copy the updated `ad_creative_v4.yml`
2. In Dify, click "Import DSL"
3. Upload the file
4. Wait for import to complete

### Step 3: Verify Form Fields Exist
After import, you should see these fields in the Start node:
- ✅ Product/Service (text input)
- ✅ Target Audience (text input)
- ✅ Ad Style (select)
- ✅ Custom Hook Text (text input)
- ✅ Font Size Scale (number)
- ✅ Image Generator (select)

**If you DON'T see these:** You imported V3 by mistake, not V4.

### Step 4: Test with Simple Input
Fill ONLY the required field:
```
Product/Service: "Telegram channel for B2B sales"
(Leave all others empty)
```

Send message: `"test"`

### Step 5: Check Node 2 Output
1. After workflow runs, click on "Generate Copy" node
2. Look at the prompt that was sent
3. Should say: `Product: Telegram channel for B2B sales`
4. Should NOT say: `Product: test`

**If it shows "Product: test":**
- ❌ Variables not connected properly
- → Check Node 2 has variables declared in YAML

### Step 6: Full Test with All Fields
```
Product/Service: Telegram Channel about B2B Outreach
Target Audience: russian digital and b2b entrepreneurs
Ad Style: Professional
Custom Hook: (empty)
Font Size Scale: (empty)
Image Generator: flux
```

Send: `"go"`

Expected output in Node 2:
```
Product: Telegram Channel about B2B Outreach
Target Audience: russian digital and b2b entrepreneurs
Desired Style: Professional
```

## 🐛 If It Still Doesn't Work

### Check 1: View Raw YAML in Dify
1. Open the workflow in Dify
2. Click on "Generate Copy" (Node 2)
3. Check if the prompt template shows:
   ```
   Product: {{#1.product#}}
   Target Audience: {{#1.audience#}}
   ```
4. NOT:
   ```
   Product: {{#sys.query#}}
   ```

### Check 2: View Variables List
In Node 2 settings, there should be a "Variables" section showing:
- product (from Node 1)
- audience (from Node 1)
- style (from Node 1)

If this list is empty, the import didn't work correctly.

### Check 3: Manual Fix in Dify UI
If import keeps failing:

1. Open Node 2 (Generate Copy)
2. Edit the user prompt to:
   ```
   Product: {{#1.product#}}
   Target Audience: {{#1.audience#}}
   Desired Style: {{#1.style#}}
   ```
3. Add variables manually:
   - Click "Add Variable"
   - Select Node 1 → product
   - Repeat for audience and style

## 🎯 Expected Behavior

### With Form Fields Filled
```
Input:
  Product: "Telegram B2B channel"
  Audience: "entrepreneurs"
  Style: "Professional"

Chat: "создай"

Output Copy:
  Hook: "MASTER B2B TELEGRAM OUTREACH" (relevant to product)
  NOT: "CHECK THIS OUT!" (generic)
```

### With Custom Hook
```
Input:
  Product: "Telegram B2B channel"
  Custom Hook: "ПОЛУЧИ 100 КЛИЕНТОВ"

Output:
  Hook: "ПОЛУЧИ 100 КЛИЕНТОВ" (uses custom)
  NOT: AI-generated hook
```

## 📊 Debugging Checklist

- [ ] Deleted old V4 workflow from Dify
- [ ] Imported fresh ad_creative_v4.yml
- [ ] See 6 form fields in Start node
- [ ] Filled Product field with test value
- [ ] Sent any chat message
- [ ] Node 2 output shows Product: <your input>
- [ ] NOT shows Product: <your chat message>
- [ ] Generated copy is relevant to product
- [ ] NOT generic "CHECK THIS OUT!"

## 🔄 Alternative: Use V3 Instead

If V4 keeps having issues, use V3 as a simpler alternative:

**V3 Workflow:**
- Single input via chat message
- No form fields
- Simpler, more reliable
- Just send: "Telegram channel for B2B outreach to Russian entrepreneurs"

Import `ad_creative_v3.yml` instead and try that.

## 📝 Test Output I Can Check

After you run the workflow, send me:

1. **Screenshot of Node 2 output** showing the prompt sent to AI
2. **The generated copy** from Node 3
3. **Your form inputs** (what you filled in)

This will help me diagnose exactly what's wrong.

## 💡 Quick Debug: Check Opening Statement

When you open the workflow in Dify, the opening message should say:
```
"Fill in the form fields above with your product details,
then send any message to generate your ad creative!"
```

If it says:
```
"Hey! Describe your product/service and I'll create..."
```

Then you're using the OLD v4 file. Re-import the new one.
