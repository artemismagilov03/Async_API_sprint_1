from uuid import UUID

from pydantic import BaseModel


class BasePerson(BaseModel):
    id: UUID
    full_name: str


class PersonFilmRoles(BaseModel):
    id: UUID
    roles: list[str] | None


class Person(BasePerson):
    films: list[PersonFilmRoles] | None
