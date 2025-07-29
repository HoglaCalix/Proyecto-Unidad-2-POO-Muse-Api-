from fastapi  import FastAPI ,  Query
from typing import Optional, Any
from bson import ObjectId
from models.art import Art, ArtWithType
from utils.mongodb import get_collection
from fastapi import APIRouter, HTTPException , Request
from utils.security import validateadmin, validateuser
from controllers.art import (
    get_all_art,
    get_art_by_id,
    create_art,
    update_art,
    deactivate_art,
    get_all_art_with_pipeline_endpoint,
    create_art_validating_with_pipeline,
    get_average_amount_of_arts_with_pipeline,
    search_art_by_query
)



art_type_collection = get_collection("art")

router = APIRouter(prefix="/art")

@router.get("/search", response_model=list[Art])
async def search_art(
    title: Optional[str] = Query(default=None, description="Search by title"),
    active: Optional[bool] = Query(default=None, description="Filter by active status"),
    id_art_type: Optional[str] = Query(default=None, description="Filter by Art Type ID"),
    creation_date: Optional[str] = Query(default=None, description="Filter by creation date (YYYY-MM-DD)"),
    image_url: Optional[str] = Query(default=None, description="Filter by image URL"),
 
):
    return await search_art_by_query(
        title=title,
        active=active,
        id_art_type=id_art_type,
        creation_date=creation_date,
        image_url=image_url
        
    )


@router.get("/get_all_arts", response_model=list[Art])
@validateadmin
async def get_all_arts(request: Request):
    return await get_all_art()

#Estadísticas primero (rutas fijas)
@router.get("/average_amount_of_arts")
@validateuser
async def get_average_amount_of_arts(request: Request):
    return await get_average_amount_of_arts_with_pipeline()

#Obtener todos los artes con pipeline
@router.get("/with-pipeline", response_model=list[ArtWithType])
@validateadmin
async def get_all_arts_using_pipeline(request: Request):
    return await get_all_art_with_pipeline_endpoint()


#Crear un arte (con validación por pipeline)
@router.post("/validate", response_model=Art)
@validateuser
async def create_arts_using_pipelines(art: Art, request: Request):
    return await create_art_validating_with_pipeline(art, request)

# Crear arte básico
@router.post("/create_arts", response_model=Art)
@validateuser
async def create_arts(art: Art, request: Request):
    return await create_art(art, request)

#Actualizar un arte por ID
@router.put("/{art_id}", response_model=Art)
@validateadmin
async def update_arts(art_id: str, art: Art, request: Request):
    return await update_art(art_id, art)

#Eliminar un arte por ID
@router.delete("/{art_id}")
@validateadmin
async def delete_arts(art_id: str, request: Request):
    return await deactivate_art(art_id)

#Obtener un arte por ID
@router.get("/{art_id}", response_model=Art)
@validateuser
async def get_art_by_ids(art_id: str, request: Request):
    return await get_art_by_id(art_id)
