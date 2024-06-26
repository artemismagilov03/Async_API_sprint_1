from uuid import UUID

from pydantic import BaseModel


class Person:
    id: UUID
    full_name: str
    films: list['FilmRoles'] | None


class FilmRoles(BaseModel):
    id: UUID
    roles: list[str] | None
