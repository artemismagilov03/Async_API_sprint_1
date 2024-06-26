from uuid import UUID


class Film:
    uuid: UUID
    title: str
    imdb_rating: float


class Genre:
    uuid: UUID
    name: str


class Person:
    uuid: UUID
    full_name: str
    films: list['FilmRoles']


class FilmRoles:
    uuid: UUID
    roles: list[str]
