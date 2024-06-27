from uuid import UUID

from pydantic import BaseModel


class Film(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float


class Genre(BaseModel):
    uuid: UUID
    name: str


class Person(BaseModel):
    uuid: UUID
    full_name: str
    films: list['FilmRoles']


class FilmRoles(BaseModel):
    uuid: UUID
    roles: list[str]
