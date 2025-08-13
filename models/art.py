from pydantic import BaseModel, Field
from typing import Optional
import re

class Art(BaseModel):
    id_art: Optional[str] = Field(
        default=None,
        description="MongoDB ID - Se genera automáticamente desde el _id de MongoDB, no es necesario enviarlo en POST"
    )

    title: str = Field(
        description="Art Title",
        pattern= r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]+$",
        examples=["Mona Lisa", "The Starry Night"]
    )

    description: str = Field(
        description="Art Description",
        pattern= r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]+$",
        examples=["A portrait by Leonardo da Vinci", "A painting by Vincent van Gogh"]
    )


    creation_date: str = Field(
        description="Art Creation Date",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        examples=["1503-06-01", "1889-06-01"]
    )

    id_art_type: str = Field(
        description="Art Type ID",
        pattern=r"^[a-fA-F0-9]{24}$",
        examples=["6881856e82e8d9ece92239ce", "6881dcfda1ffa94aad2abf3f"]
    )
    image_url: Optional[str] = Field(
        default=None,
        description="URL of the art image",
        pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$",
        examples=["https://example.com/image.jpg", "http://example.com/art.png"]
    )
    active: bool = Field(
        default=True,
        description="Estado activo de la obra de arte, por defecto es True"
    )
    arttypetname: Optional[str] = Field(
        default=None,
        description="Nombre del tipo de arte"
    )

class ArtWithType(BaseModel):
    id_art: str 
    title: str
    description: str
    creation_date: str
    image_url: str
    active: bool
    id_art_type: str
    arttypetname: str
    id_art_type_status: bool
