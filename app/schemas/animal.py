from typing import List, Optional

from pydantic import BaseModel, ConfigDict


# ── INPUT SCHEMA ─────────────────────────────────────────────────────────────
class AnimalCreate(BaseModel):
    name: str



# ── OUTPUT SCHEMA ────────────────────────────────────────────────────────────
class AnimalRead(BaseModel):
    id: int
    name: str
    ancestor_id: Optional[int] = None
    fun_fact: Optional[str] = None
    scientific_name:  Optional[str] = None
    taxonomy_class:   Optional[str] = None
    image_url:        Optional[str] = None
    locations:        Optional[str] = None
    temperament:      Optional[str] = None
    lifespan:         Optional[str] = None
    weight:           Optional[str] = None

    model_config = ConfigDict(from_attributes=True)



class AnimalCreateResponse(BaseModel):
    animal: AnimalRead
    background_task_status: str  



class AnimalLineageItem(BaseModel):
    id: int
    name: str
    ancestor_id: Optional[int] = None
    depth: int 

    model_config = ConfigDict(from_attributes=True)



class LineageResponse(BaseModel):
    animal_name: str        
    total_generations: int    
    lineage: List[AnimalLineageItem]  


# ── LCA SCHEMA ───────────────────────────────────────────────────────────────

class LCAResponse(BaseModel):
    common_ancestor: AnimalRead   
    animal1_distance: int         
    animal2_distance: int         
    total_distance: int          
