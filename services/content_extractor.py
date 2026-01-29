"""Content extraction service - extracts info from URLs, files, and raw text."""

import httpx
from openai import AsyncOpenAI
from pathlib import Path

from config import get_settings


class ContentExtractor:
    """Extracts and summarizes content from various sources for ad creation."""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def extract_from_url(self, url: str) -> dict:
        """
        Extract key information from a website URL.

        Returns:
            Dict with product_name, description, key_benefits, target_audience, tone
        """
        try:
            # Fetch the webpage
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    follow_redirects=True,
                    timeout=30.0,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; AdCreativeBot/1.0)"}
                )
                response.raise_for_status()
                html_content = response.text

            # Use LLM to extract structured info
            return await self._extract_with_llm(html_content, source_type="website")

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to extract from URL: {str(e)}"
            }

    async def extract_from_file(self, file_path: str) -> dict:
        """
        Extract key information from a file (txt, md, pdf, etc.).
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}

            # Read file content
            content = path.read_text(encoding="utf-8", errors="ignore")

            return await self._extract_with_llm(content, source_type="document")

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to extract from file: {str(e)}"
            }

    async def extract_from_text(self, text: str) -> dict:
        """
        Extract key information from raw text input.
        """
        return await self._extract_with_llm(text, source_type="text")

    async def _extract_with_llm(self, content: str, source_type: str) -> dict:
        """Use LLM to extract structured information from content."""

        # Truncate if too long
        max_chars = 15000
        if len(content) > max_chars:
            content = content[:max_chars] + "\n\n[Content truncated...]"

        extraction_prompt = f"""Analyze this {source_type} and extract key information for creating ad creatives.

CONTENT:
{content}

Extract and return a JSON object with:
{{
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
}}

Be specific and actionable. If something isn't clear from the content, make a reasonable inference based on context."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You extract structured marketing information from content. Always respond with valid JSON."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.3,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            result["success"] = True
            result["source_type"] = source_type
            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"LLM extraction failed: {str(e)}"
            }
