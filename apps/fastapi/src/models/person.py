from uuid import UUID
from pydantic import BaseModel


class Person(BaseModel):
    id: UUID
    full_name: str
    films: list[dict] = []
