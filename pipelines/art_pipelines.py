from bson import ObjectId

def validate_art_type_pipeline(art_type_id: str) -> list:
    
    return [
        {
            "$match": {
                "_id": ObjectId(art_type_id),
                "active": True
                
            }},
            {"$project": {
                "id_art_type": {"$toString": "$art_type_id"},
                "description": "$description",
                "arttypetname": "$arttypetname",
                "active": "$active",
                "image_url": "$image_url"
            }}

    ]

def get_all_arts_with_types_pipeline(skip: int, limit: int) -> list:
    return  [
        {"$addFields": {
            "id_art_type": {"$toObjectId": "$id_art_type"},
        }},
        
        {"$lookup": {
            "from":"art_type",
            "localField": "id_art_type",
            "foreignField": "_id",
            "as": "art_type"
        }},
        {"$unwind": "$art_type"},

        
        {"$project": {
            "id_art": {"$toString": "$_id"},
            "id": {"$toString": "$_id"},
            "id_art_type": {"$toString": "$id_art_type"},
            "id_art_type_status": "$art_type.active",
            "description": "$description",
            "arttypetname": "$art_type.arttypetname",
            "active": "$active",
            "title": "$title", 
            "creation_date": "$creation_date"
            , "image_url": "$image_url"
        }},
        
        {"$skip": skip},
        {"$limit": limit


    }
    ]
