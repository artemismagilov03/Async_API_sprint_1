import uuid
from pydantic import BaseModel


class Film(BaseModel):
    id: uuid
    title: str
    imdb_rating: float
    description: str
    genre: list[dict] = []
    actors: list[dict] = []
    writers: list[dict] = []
    directors: list[dict] = []