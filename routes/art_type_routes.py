from fastapi  import FastAPI
from bson import ObjectId
from models.art_type import Art_Type
from utils.mongodb import get_collection
from fastapi import APIRouter, HTTPException, Request
from utils.security import validateadmin, validateuser
from controllers.art_type import (
    get_all_art_types,
    get_art_type_by_id,
    create_art_type,
    update_art_type,
    deactivate_art_type
)

art_type_collection = get_collection("art_type")

router = APIRouter(prefix="/art_type")

##Obtener todos los tipos de arte 
@router.get("/get_art_type" , response_model=list[Art_Type])
@validateuser
async def get_all_art_type(request: Request):
    return await get_all_art_types()

#Obtener un tipo de arte por su id
@router.get("/{art_type_id}", response_model=Art_Type)
@validateuser   
async def get_art_type_by_ids(art_type_id: str, request: Request):
    return await get_art_type_by_id(art_type_id)    

#Crear un nuevo tipo de arte 
@router.post("/create_art_type", response_model=Art_Type)
@validateuser
async def create_art_types(art_type: Art_Type, request: Request):
    return await create_art_type(art_type)

#Actualizar un tipo de arte por su id
@router.put("/{art_type_id}", response_model=Art_Type)
@validateuser
async def update_art_types(art_type_id: str, art_type: Art_Type, request: Request):
    return await update_art_type(art_type_id, art_type)

#Borrar un tipo de arte por su id
@router.delete("/{art_type_id}")
@validateuser
async def deactivate_art_types(art_type_id: str, request: Request):
    return await deactivate_art_type(art_type_id)