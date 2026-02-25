import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_UNSPLASH_URL = "https://api.unsplash.com/search/photos"


async def _search_unsplash(query: str, client: httpx.AsyncClient) -> Optional[str]:
   
    response = await client.get(
        _UNSPLASH_URL,
        params={
            "query": query,
            
            
        },
        headers={"Authorization": f"Client-ID {settings.UNSPLASH_ACCESS_KEY}"},
    )
    if response.status_code != 200:
        logger.warning(f"[Image] Unsplash HTTP {response.status_code} → '{query}'")
        return None

    results = response.json().get("results", [])
    if not results:
        return None

    return results[0].get("urls", {}).get("regular")


async def fetch_animal_image_url(animal_name: str) -> Optional[str]:
    if not settings.UNSPLASH_ACCESS_KEY:
        logger.warning("[Image] UNSPLASH_ACCESS_KEY is not defined, skipping image.")
        return None

    queries = [
        animal_name, 
        f"{animal_name} animal",              
        f"{animal_name} wildlife",    
                                 
    ]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            for query in queries:
                url = await _search_unsplash(query, client)
                if url:
                    logger.info(f"[Image] '{animal_name}' → query='{query}' → {url[:70]}...")
                    return url

        logger.warning(f"[Image] No Unsplash results found for '{animal_name}' in any query.")
        return None

    except Exception as e:
        logger.warning(f"[Image] Unsplash error for '{animal_name}': {e}")
        return None
