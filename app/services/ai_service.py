import logging
from typing import Optional

from google import genai

from app.core.config import settings
from app.db.database import AsyncSessionLocal
from app.db.models import Animal

logger = logging.getLogger(__name__)


_client = genai.Client(api_key=settings.GEMINI_API_KEY)


_MODEL = "gemini-2.5-flash-lite"


def _build_prompt(animal_name: str, taxonomy_class: Optional[str]) -> str:
    context = f" (Class: {taxonomy_class})" if taxonomy_class else ""
    return (
        f"You are a concise evolutionary biologist.{context} "
        f"Write 1-2 sentences about {animal_name} highlighting its "
        f"evolutionary origins, ancestors, or interesting relatives. "
        f"Do NOT use greetings, salutations, or phrases like 'Dear'. "
        f"Return only the information."
    )


async def generate_fun_fact(
    animal_name: str,
    animal_id: int,
    taxonomy_class: Optional[str] = None,
) -> None:
    """
    Generates an evolutionary fun fact using the Google Gemini API
    (google-genai SDK) and writes it to the database.
    """
    logger.info(f"[Gemini] Starting fun_fact generation for '{animal_name}'...")

    fun_fact_text: Optional[str] = None

    # ── 1. GEMINI API CALL ────────────────────────────────────────────────────
    try:
        prompt = _build_prompt(animal_name, taxonomy_class)

        response = await _client.aio.models.generate_content(
            model=_MODEL,
            contents=prompt,
        )
        fun_fact_text = response.text.strip()
        logger.info(
            f"[Gemini] Fun fact generated for '{animal_name}': {fun_fact_text[:80]}..."
        )

    except Exception as gemini_err:
    
        logger.error(
            f"[Gemini] API call failed for '{animal_name}': {gemini_err}",
            exc_info=True,
        )
        return  

    # ── 2. WRITE TO DATABASE ─────────────────────────────────────────────────
    try:
        async with AsyncSessionLocal() as session:
            animal = await session.get(Animal, animal_id)
            if animal is None:
                logger.warning(
                    f"[Gemini] Animal id={animal_id} has been deleted, skipping save."
                )
                return

            animal.fun_fact = fun_fact_text
            await session.commit()
            logger.info(
                f"[Gemini] Fun fact for '{animal_name}' saved to DB."
            )

    except Exception as db_err:
        logger.error(
            f"[Gemini] Failed to write fun fact for '{animal_name}' to DB: {db_err}",
            exc_info=True,
        )



