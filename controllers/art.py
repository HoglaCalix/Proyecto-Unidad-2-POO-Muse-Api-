
from datetime import datetime
from fastapi import FastAPI , Query
from typing import Optional
from bson import ObjectId
from models.art import Art, ArtWithType
from utils.mongodb import get_collection
from fastapi import APIRouter, HTTPException, Request
from pipelines.art_pipelines import validate_art_type_pipeline, get_all_arts_with_types_pipeline
art_collection = get_collection("art")
art_type_collection = get_collection("art_type")


async def get_all_art_with_pipeline_endpoint(skip: int = 0, limit: int = 5) -> list[ArtWithType]:
    try:
        pipeline = get_all_arts_with_types_pipeline(skip,limit)
        arts = list(art_collection.aggregate(pipeline))
        total_count = art_collection.count_documents({"active": True})
    
        return arts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving arts: {str(e)}")


async def get_all_art() -> list[Art]:
    
    try:
        arts = []
        for doc in art_collection.find():
            doc["_id"] = str(doc["_id"])
            del doc["_id"]
            art = Art(**doc)
            arts.append(art)
        return arts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving arts: {str(e)}")
    
async def get_art_by_id(art_id: str) -> Art:
    try:
        doc = art_collection.find_one({"_id": ObjectId(art_id)})
        if not doc.get("active", True):
            raise HTTPException(status_code=404, detail="Art not found or inactive")
        if not doc:
            raise HTTPException(status_code=404, detail="Art not found")
        doc["_id"] = str(doc["_id"])
        del doc["_id"]
        return Art(**doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving art: {str(e)}")
    
async def create_art(art: Art, request: Request) -> Art:
    try:
       
        art.image_url = art.image_url.strip() 

        existing_art = art_collection.find_one({
            "image_url": art.image_url
        })
        if existing_art:
            raise HTTPException(status_code=400, detail="An artwork with this title and description already exists")
        
        art_type_id = art.id_art_type

        art_type_doc = art_type_collection.find_one({
            "_id": ObjectId(art_type_id),
            "active": True
        })

        if not art_type_doc:
            raise HTTPException(
                status_code=400,
                detail="The selected Art Type does not exist or is not active"
            )

        art_dict = art.model_dump(exclude={"id_art"})
        inserted = art_collection.insert_one(art_dict)
        art.id_art = str(inserted.inserted_id)
        return art
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating art: {str(e)}")

async def create_art_validating_with_pipeline(art: Art, author:dict) -> Art:
    try:
        art_type_pipeline = validate_art_type_pipeline(art.id_art_type)
        art_type_result = list(art_type_collection.aggregate(art_type_pipeline))

        if not art_type_result:
            raise HTTPException(status_code=404, detail="Art type not found or inactive")
    
        existing_art = art_collection.find_one({
            "image_url": art.image_url
        })
        if existing_art:
            raise HTTPException(status_code=400, detail="An artwork with this image URL already exists.")
        
        art_dict = art.model_dump(exclude={"id_art"})
        inserted = art_collection.insert_one(art_dict)
        art.id_art = str(inserted.inserted_id)
        return art
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating art: {str(e)}")
 
async def update_art(art_id: str, art: Art) -> Art:
    try:
        
        art.description = art.description.strip()
        art.title = art.title.strip()
        art.image_url = art.image_url.strip()
        existing_art = art_collection.find_one({"description": art.description, "_id": {"$ne": ObjectId(art_id)}})
        try:
            art_type_obj_id = ObjectId(art.id_art_type)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid art type ID format")

        existing_type = art_type_collection.find_one({
            "_id": art_type_obj_id,
            "active": True
        })

        if not existing_type:
            raise HTTPException(status_code=400, detail="Art type not found or inactive")


        existing_art = art_collection.find_one({
            "_id": {"$ne": ObjectId(art_id)},
            "title": art.title,
            "image_url": art.image_url,
            "description": art.description
        })
        if existing_art:
            raise HTTPException(status_code=400, detail="An artwork with this description already exists")

        
        update_result = art_collection.update_one({"_id": ObjectId(art_id)}, {"$set": art.model_dump(exclude={"id_art"})})
        
        if update_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Art not found or no changes made")
        
        return await get_art_by_id(art_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating art: {str(e)}")
    
async def deactivate_art(art_id: str):
    try:
        result = art_collection.update_one({"_id": ObjectId(art_id)}, {"$set": {"active": False}})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Art not found or already inactive")
        return {"message": "Art deactivated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating art: {str(e)}")


async def get_average_amount_of_arts_with_pipeline() -> list:
    try:
        art_collection = get_collection("art")

        pipeline = [
            {
                "$addFields": {
                    "id_art_type_obj": {"$toObjectId": "$id_art_type"}
                }
            },
            {
                "$group": {
                    "_id": "$id_art_type_obj",
                    "total_obras": {"$sum": 1}
                }
            },
            {
                "$lookup": {
                    "from": "art_type",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "art_type_info"
                }
            },
            {"$unwind": "$art_type_info"},
            {
                "$project": {
                    "_id": 0,
                    "nombre_tipo": "$art_type_info.arttypetname",
                    "total_obras": 1
                }
            },
            {"$sort": {"total_obras": -1}}
        ]

        results = list(art_collection.aggregate(pipeline))

        return {
            "arts_summary": results,
            
        }

        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating average amount of arts: {str(e)}")



async def search_art_by_query(
    title: Optional[str] = None,
    active: Optional[bool] = None,
    id_art_type: Optional[str] = None,
    creation_date: Optional[str] = None,
    image_url: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
) -> list[Art]:
    
    try:
        if not any([title, active is not None, id_art_type, creation_date, image_url]):
            raise HTTPException(
                status_code=400,
                detail="You must provide at least one filter: title, active, id_art_type, or creation_date"
            )

        filters = {}

        if title:
            filters["title"] = {"$regex": title, "$options": "i"}

        if active is not None:
            filters["active"] = active

        if id_art_type:
            filters["id_art_type"] = id_art_type
        
        if image_url:
            filters["image_url"] = {"$regex": image_url, "$options": "i"}

        if creation_date:
            try:
                datetime.strptime(creation_date, "%Y-%m-%d")  # validation
                filters["creation_date"] = creation_date
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

        cursor = art_collection.find(filters).skip(skip).limit(limit)
        results = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(Art(**doc))

        if filters and not results:
            raise HTTPException(
                status_code=404,
                detail="No artworks match the provided filter combination"
            )

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during search: {str(e)}")
