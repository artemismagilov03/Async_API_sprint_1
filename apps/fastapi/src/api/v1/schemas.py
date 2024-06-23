from pydantic import BaseModel
from uuid import UUID


class BasePerson(BaseModel):
    id: UUID
    full_name: str


class Genre(BaseModel):
    id: UUID
    name: str


class Film(BaseModel):
    id: UUID
    title: str
    imdb_rating: float | None
    description: str | None
    genres: list[Genre] | None
    description: str | None
    directors_names: str | None
    actors_names: str | None
    writers_names: str | None
    directors: list[BasePerson] | None
    actors: list[BasePerson] | None
    writers: list[BasePerson] | None


class PersonFilmRoles(BaseModel):
    id: UUID
    roles: list[str] | None


class Person(BasePerson):
    films: list[PersonFilmRoles] | None
