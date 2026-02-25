from typing import Any, Type, TypeVar

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


async def get_or_404(db: AsyncSession, model: Type[T], pk: int) -> T:
    obj: Any = await db.get(model, pk)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} id={pk} not found.",
        )
    return obj
