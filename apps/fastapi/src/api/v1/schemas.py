from pydantic import BaseModel

from uuid import UUID


class Film(BaseModel):
    id: UUID
    title: str
    imdb_rating: float


class Genre(BaseModel):
    id: UUID
    name: str


class Person(BaseModel):
    id: UUID
    full_name: str
    films: list['PersonFilmRoles']


class PersonFilmRoles(BaseModel):
    id: UUID
    roles: list[str]
