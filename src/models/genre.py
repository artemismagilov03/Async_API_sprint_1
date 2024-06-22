import uuid
from pydantic import BaseModel


class Genre(BaseModel):
    id: uuid
    name: str
 

 