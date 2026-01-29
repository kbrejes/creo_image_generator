# Content Extraction Prompt

Use this prompt in a Dify LLM node to extract product/service information from user input.

## System Prompt

```
You extract structured marketing information from content. Always respond with valid JSON.
```

## User Prompt Template

```
Analyze this content and extract key information for creating ad creatives.

CONTENT:
{{input_content}}

Extract and return a JSON object with:
{
    "product_name": "Name of the product/service/brand",
    "company_name": "Company name if different from product",
    "description": "Clear, concise description (2-3 sentences)",
    "key_benefits": ["benefit 1", "benefit 2", "benefit 3"],
    "target_audience": "Who this is for",
    "unique_selling_points": ["USP 1", "USP 2"],
    "tone": "Brand tone (professional/casual/playful/bold/etc)",
    "industry": "Industry category",
    "keywords": ["relevant", "keywords", "for", "ads"],
    "pain_points_solved": ["pain point 1", "pain point 2"],
    "call_to_action_suggestions": ["CTA 1", "CTA 2", "CTA 3"]
}

Be specific and actionable. If something isn't clear from the content, make a reasonable inference based on context.
```

## Variables

- `{{input_content}}` - The raw text, URL content, or file content to analyze

## Output

JSON object that can be passed to the copy generation node.
