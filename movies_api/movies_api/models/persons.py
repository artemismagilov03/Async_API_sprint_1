from uuid import UUID

from pydantic import BaseModel


class Actor(BaseModel):
    id: UUID
    full_name: str


class Director(BaseModel):
    id: UUID
    full_name: str


class Writer(BaseModel):
    id: UUID
    full_name: str


class Person(BaseModel):
    id: UUID
    full_name: str
    films: list['FilmRoles'] | None


class FilmRoles(BaseModel):
    id: UUID
    roles: list[str] | None
