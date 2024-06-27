from uuid import UUID

from pydantic import BaseModel

from movies_api.models.genre import Genre
from movies_api.models.persons import Actor, Director, Writer


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
    directors: list[Director] | None
    actors: list[Actor] | None
    writers: list[Writer] | None
