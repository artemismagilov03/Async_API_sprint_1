from pydantic import BaseModel
from uuid import UUID

from movies_api.models.genre import Genre
from movies_api.models.person import BasePerson


class Film(BaseModel):
    id: UUID
    title: str
    rating: float | None
    description: str | None
    genres: list[Genre] | None
    description: str | None
    directors_names: str | None
    actors_names: str | None
    writers_names: str | None
    directors: list[BasePerson] | None
    actors: list[BasePerson] | None
    writers: list[BasePerson] | None
