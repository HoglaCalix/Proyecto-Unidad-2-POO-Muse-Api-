
from fastapi import FastAPI
from bson import ObjectId
from models.art_type import Art_Type
from utils.mongodb import get_collection
from fastapi import APIRouter, HTTPException
from pipelines.art_type_pipelines import get_art_type_pipeline

art_type_collection = get_collection("art_type")
art_collection = get_collection("art")

async def get_all_art_types() -> list:
    try:
        art_types = []
        for doc in art_type_collection.find():
            doc["id_arttype"] = str(doc["_id"])
            del doc["_id"]
            catalog_type = Art_Type(**doc)
            art_types.append(catalog_type)
        return art_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving art types: {str(e)}")
    
async def get_art_type_by_id(art_type_id: str) -> Art_Type:
    try:
        doc = art_type_collection.find_one({"_id": ObjectId(art_type_id)})
        if not doc.get("active", True):
            raise HTTPException(status_code=404, detail="Art type not found or inactive")
        if not doc:
            raise HTTPException(status_code=404, detail="Art type not found")
        doc["_id"] = str(doc["_id"])
        del doc["_id"]
        return Art_Type(**doc)
   
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving art type: {str(e)}")
    
async def create_art_type(art_type: Art_Type) -> Art_Type:
    try:
        art_type.arttypetname = art_type.arttypetname.strip()
        art_type.typedescription = art_type.typedescription.strip()

        existing_type = art_type_collection.find_one({
            "arttypetname": art_type.arttypetname,
            "typedescription": art_type.typedescription
        })
        if existing_type:
            raise HTTPException(
                status_code=400,
                detail="An art type with this name and description already exists"
            )
        
        art_type_dict = art_type.model_dump(exclude={"id_arttype"})
        inserted = art_type_collection.insert_one(art_type_dict)
        art_type.id_arttype = str(inserted.inserted_id)
        return art_type
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating art type: {str(e)}")
    

async def update_art_type(art_type_id: str, art_type: Art_Type) -> Art_Type:
    try:
        art_type.arttypetname = art_type.arttypetname.strip()
        art_type.typedescription = art_type.typedescription.strip()
        existing_type = art_type_collection.find_one({
        "arttypetname": art_type.arttypetname,
        "typedescription": art_type.typedescription,
        "_id": {"$ne": ObjectId(art_type_id)}
        })
        if existing_type:
            raise HTTPException(status_code=400, detail="An art type with this name and description already exists")
        
        result = art_type_collection.update_one({"_id": ObjectId(art_type_id)}, {"$set": art_type.model_dump(exclude={"id_arttype"})})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Art type not found or no changes made")
        
        return await get_art_type_by_id(art_type_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating art type: {str(e)}")
    
async def deactivate_art_type(art_type_id: str) -> dict:
    try:
        count = art_collection.count_documents({"id_art_type": art_type_id, "active": True})
        if count > 0:
            raise HTTPException(
                status_code=400,
                detail="Cant deactivate art type because there are active arts associated with it"
            )
        result = art_type_collection.update_one({"_id": ObjectId(art_type_id)}, {"$set": {"active": False}})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Art type not found or already inactive")
        
        return {"message": "Art type deactivated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating art type: {str(e)}")
    

