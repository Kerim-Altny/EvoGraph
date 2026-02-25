from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Animal
from app.schemas.animal import (
    AnimalCreate,
    AnimalCreateResponse,
    AnimalLineageItem,
    AnimalRead,
    LCAResponse,
    LineageResponse,
)
from app.services.ai_service import generate_fun_fact
from app.services.external_api import fetch_animal_data
from app.services.image_service import fetch_animal_image_url
from app.utils import get_or_404

router = APIRouter(prefix="/animals", tags=["Animals"])


# ── CREATE ───────────────────────────────────────────────────────────────────
@router.post("/", response_model=AnimalCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_animal(
    body: AnimalCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    animal_name = body.name.strip().title()

    api_data = await fetch_animal_data(animal_name)
    if not api_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No animal found on API Ninjas for '{animal_name}'. "
                   f"Try a different name or an English scientific name.",
        )

    hierarchy = api_data.get("taxonomy_hierarchy", [])
    leaf_name = api_data.get("proper_name") or animal_name

   

 
    pre_check = await db.execute(select(Animal).where(Animal.name == leaf_name))
    if pre_check.scalars().first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"'{leaf_name}' is already registered in the database.",
        )

   
    current_parent_id: int | None = None
    for taxon_name in hierarchy:
        result = await db.execute(select(Animal).where(Animal.name == taxon_name))
        existing = result.scalars().first()
        if existing:
            current_parent_id = existing.id
        else:
            node = Animal(name=taxon_name, ancestor_id=current_parent_id)
            db.add(node)
            await db.flush()
            current_parent_id = node.id

   
    result = await db.execute(select(Animal).where(Animal.name == leaf_name))
    existing_as_taxon = result.scalars().first()

    image_url = await fetch_animal_image_url(leaf_name)

    if existing_as_taxon:
        leaf_animal = existing_as_taxon
        leaf_animal.scientific_name = api_data.get("scientific_name")
        leaf_animal.taxonomy_class  = api_data.get("taxonomy_class")
        leaf_animal.locations       = api_data.get("locations")
        leaf_animal.lifespan        = api_data.get("lifespan")
        leaf_animal.weight          = api_data.get("weight")
        leaf_animal.image_url       = image_url
    else:
        leaf_animal = Animal(
            name=leaf_name,
            ancestor_id=current_parent_id,
            scientific_name=api_data.get("scientific_name"),
            taxonomy_class=api_data.get("taxonomy_class"),
            locations=api_data.get("locations"),
            temperament=api_data.get("temperament"),
            lifespan=api_data.get("lifespan"),
            weight=api_data.get("weight"),
            image_url=image_url,
        )
        db.add(leaf_animal)
        await db.flush()

    await db.commit()
    await db.refresh(leaf_animal)

    background_tasks.add_task(generate_fun_fact, leaf_animal.name, leaf_animal.id, leaf_animal.taxonomy_class)

    full_path = " → ".join(hierarchy) + f" → {leaf_name}"
    return AnimalCreateResponse(
        animal=AnimalRead.model_validate(leaf_animal),
        background_task_status=f"'{leaf_animal.name}' added! Hierarchy: {full_path}",
    )


# ── READ ALL ─────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[AnimalRead])
async def list_animals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Animal))
    return result.scalars().all()


# ── LCA (LOWEST COMMON ANCESTOR) ─────────────────────────────────────────────
@router.get("/common-ancestor", response_model=LCAResponse)
async def get_common_ancestor(
    animal1_id: int,
    animal2_id: int,
    db: AsyncSession = Depends(get_db),
):
    a1 = await get_or_404(db, Animal, animal1_id)
    a2 = await get_or_404(db, Animal, animal2_id)
    if animal1_id == animal2_id:
        raise HTTPException(status_code=400, detail="Both IDs are the same; please enter different animals.")

    cte = text("""
        WITH RECURSIVE lineage AS (
            SELECT id, name, ancestor_id, 0 AS depth
            FROM animals WHERE id = :start_id
            UNION ALL
            SELECT a.id, a.name, a.ancestor_id, l.depth + 1
            FROM animals a
            INNER JOIN lineage l ON a.id = l.ancestor_id
        )
        SELECT id, name, ancestor_id, depth FROM lineage ORDER BY depth ASC;
    """)

    res1 = await db.execute(cte, {"start_id": animal1_id})
    res2 = await db.execute(cte, {"start_id": animal2_id})
    lineage1 = res1.fetchall()
    lineage2 = res2.fetchall()

    ancestors_of_1: dict[int, int] = {row.id: row.depth for row in lineage1}
    lca_row = None
    lca_distance_from_2 = None

    for row in lineage2:
        if row.id in ancestors_of_1:
            lca_row = row
            lca_distance_from_2 = row.depth
            break

    if not lca_row:
        raise HTTPException(status_code=404, detail="No common ancestor found for these two animals.")

    lca_distance_from_1 = ancestors_of_1[lca_row.id]
    lca_animal = await db.get(Animal, lca_row.id)

    return LCAResponse(
        common_ancestor=AnimalRead.model_validate(lca_animal),
        animal1_distance=lca_distance_from_1,
        animal2_distance=lca_distance_from_2,
        total_distance=lca_distance_from_1 + lca_distance_from_2,
    )


# ── READ ONE ─────────────────────────────────────────────────────────────────
@router.get("/{animal_id}", response_model=AnimalRead)
async def get_animal(animal_id: int, db: AsyncSession = Depends(get_db)):
    return await get_or_404(db, Animal, animal_id)


# ── DELETE ────────────────────────────────────────────────────────────────────
@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_animal(animal_id: int, db: AsyncSession = Depends(get_db)):
    animal = await get_or_404(db, Animal, animal_id)
    await db.delete(animal)
    await db.commit()


# ── LINEAGE (FAMILY TREE) ─────────────────────────────────────────────────────
@router.get("/{animal_id}/lineage", response_model=LineageResponse)
async def get_lineage(animal_id: int, db: AsyncSession = Depends(get_db)):
    origin = await get_or_404(db, Animal, animal_id)

    cte_query = text("""
        WITH RECURSIVE lineage AS (
            SELECT id, name, ancestor_id, 0 AS depth
            FROM animals WHERE id = :start_id
            UNION ALL
            SELECT a.id, a.name, a.ancestor_id, l.depth + 1
            FROM animals a
            INNER JOIN lineage l ON a.id = l.ancestor_id
        )
        SELECT id, name, ancestor_id, depth FROM lineage ORDER BY depth ASC;
    """)

    result = await db.execute(cte_query, {"start_id": animal_id})
    rows = result.fetchall()

    lineage_items = [
        AnimalLineageItem(id=row.id, name=row.name, ancestor_id=row.ancestor_id, depth=row.depth)
        for row in rows
    ]

    return LineageResponse(
        animal_name=origin.name,
        total_generations=len(lineage_items) - 1,
        lineage=lineage_items,
    )
