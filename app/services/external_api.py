from typing import Any

import httpx

from app.core.config import settings


_API_NINJAS_BASE = "https://api.api-ninjas.com/v1/animals"

_TAXONOMY_LEVELS = ["kingdom", "phylum", "class", "order", "family", "genus"]


async def fetch_animal_data(animal_name: str) -> dict[str, Any]:
   
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            _API_NINJAS_BASE,
            params={"name": animal_name},
            headers={"X-Api-Key": settings.API_NINJAS_KEY},
        )

    if response.status_code != 200:
        return {}

    data = response.json()
    if not data:
        return {}

    animal          = data[0]
    taxonomy        = animal.get("taxonomy", {})
    characteristics = animal.get("characteristics", {})
    locations_list  = animal.get("locations", [])

  
    hierarchy = [
        taxonomy[level]
        for level in _TAXONOMY_LEVELS
        if taxonomy.get(level)
    ]

    
    locations_str = ", ".join(locations_list) if locations_list else None

    return {
        "proper_name":        animal.get("name"),         
        "scientific_name":    taxonomy.get("scientific_name"),
        "taxonomy_class":     taxonomy.get("class"),
        "locations":          locations_str,
        "temperament":        characteristics.get("temperament"),
        "lifespan":           characteristics.get("lifespan"),
        "weight":             characteristics.get("weight"),
        "taxonomy_hierarchy": hierarchy,
    }
