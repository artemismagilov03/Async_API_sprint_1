from pydantic import BaseModel
from typing import Never

from uuid import UUID


class Film(BaseModel):
    id: UUID
    title: str
    rating: float | None
    description: str | None
    genres: list[str] | None
    description: str | None
    directors_names: str | None
    actors_names: str | None
    writers_names: str | None
    directors: list['Director'] | None
    actors: list['Actor'] | None
    writers: list['Writer'] | None


class Director(BaseModel):
    id: UUID
    name: str


class Actor(BaseModel):
    id: UUID
    name: str


class Writer(BaseModel):
    id: UUID
    name: str


class Person(BaseModel):
    id: UUID
    full_name: str
    films: list['PersonFilmRoles'] | None


class PersonFilmRoles(BaseModel):
    id: str
    roles: list[str] | None
