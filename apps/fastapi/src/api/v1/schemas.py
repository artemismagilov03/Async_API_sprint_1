from uuid import UUID


class Film:
    uuid: UUID
    title: str


class Genre:
    uuid: UUID
    name: str


class Person:
    uuid: UUID
    full_name: str
    films: list['PersonFilmRoles']


class PersonFilmRoles:
    uuid: UUID
    roles: list[str]
