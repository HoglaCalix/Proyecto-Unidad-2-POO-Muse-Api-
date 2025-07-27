from pydantic import BaseModel, Field
from typing import Optional
import re

class Art_Type(BaseModel):
    id_arttype: Optional[str] = Field(
        default=None,
        description="MongoDB ID - Se genera automáticamente desde el _id de MongoDB, no es necesario enviarlo en POST"
    )

    arttypetname: str = Field(
        description="Art Type Name",
        pattern= r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]+$",
        examples=["Painting", "Sculpture"]
    )

    typedescription: str = Field(
        description="Art Type Description",
        pattern= r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]+$",
        examples=["A type of art that involves applying pigment to a surface", "A three-dimensional work of art created by shaping materials"]
    )
    active: bool = Field(
        default=True,
        description="Estado activo del tipo de arte, por defecto es True"
    )