from pydantic import BaseModel
from uuid import UUID


class BasePerson(BaseModel):
    id: UUID
    full_name: str

class PersonFilmRoles(BaseModel):
    id: UUID
    roles: list[str] | None


class Person(BasePerson):
    films: list[PersonFilmRoles] | None
