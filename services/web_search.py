"""Web search service for finding reference images."""

import httpx

from config import get_settings


class WebSearchService:
    """Search the web for reference images using Serper API."""

    SERPER_API_URL = "https://google.serper.dev/images"

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.serper_api_key

    async def search_images(
        self,
        query: str,
        num_results: int = 5,
        image_type: str | None = None,
    ) -> dict:
        """
        Search for images on the web.

        Args:
            query: Search query
            num_results: Number of results to return
            image_type: Type of images (photo, clipart, lineart, etc.)

        Returns:
            Dict with search results or error
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "Serper API key not configured. Set SERPER_API_KEY in .env",
                "results": [],
            }

        try:
            payload = {
                "q": query,
                "num": min(num_results, 20),
            }

            if image_type:
                payload["type"] = image_type

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.SERPER_API_URL,
                    headers={
                        "X-API-KEY": self.api_key,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=30.0,
                )

                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Serper API error: {response.status_code}",
                        "results": [],
                    }

                data = response.json()
                images = data.get("images", [])

                results = []
                for img in images[:num_results]:
                    results.append(
                        {
                            "title": img.get("title", ""),
                            "url": img.get("link", ""),
                            "image_url": img.get("imageUrl", ""),
                            "thumbnail_url": img.get("thumbnailUrl", ""),
                            "source": img.get("source", ""),
                        }
                    )

                return {
                    "success": True,
                    "results": results,
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "results": [],
            }

    async def search_ads(
        self,
        query: str,
        platform: str | None = None,
        num_results: int = 5,
    ) -> dict:
        """
        Search specifically for ad examples.

        Args:
            query: Product or brand to search for
            platform: Target platform (instagram, facebook, google, etc.)
            num_results: Number of results

        Returns:
            Dict with search results
        """
        # Enhance query for ad search
        search_query = f"{query} advertisement"
        if platform:
            search_query = f"{query} {platform} ad example"

        return await self.search_images(search_query, num_results)
