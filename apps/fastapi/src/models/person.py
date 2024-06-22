import uuid
from pydantic import BaseModel
 
class Person(BaseModel):
    id: uuid
    full_name: str
    films: list[dict] = []