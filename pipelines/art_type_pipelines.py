from bson import ObjectId

def get_art_type_pipeline() -> list:
    return [
        {
            "$addFields": {
                "id": {"$toString": "$_id"}
            }
        },{
            "$lookup": {
                "from": "art",
                "localField": "id",
                "foreignField": "id_art_type",
                "as": "result"
            }
        },{
            "$group": {
                "_id": {
                    "id": "$id",
                    "description": "$description",
                    "active": "$active"
                },
                
            }
        },{
            "$project": {
                "_id": 0,
                "id": "$_id.id",
                "description": "$_id.description",
                "active": "$_id.active",
                
            }
        }
    ]