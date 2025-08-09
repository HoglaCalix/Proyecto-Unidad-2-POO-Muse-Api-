def get_art_type_pipeline() -> list:
    return [
        {
            "$addFields": {
                "id": {"$toString": "$_id"}
            }
        },
        {
            "$lookup": {
                "from": "art",
                "localField": "id",
                "foreignField": "id_art_type",  # Este campo debe coincidir con el campo en 'art'
                "as": "artworks"
            }
        },
        {
            "$project": {
                "_id": 0,
                "id": 1,
                "arttypetname": 1,
                "typedescription": 1,
                "active": 1,
                "artworks": 1
            }
        }
    ]
