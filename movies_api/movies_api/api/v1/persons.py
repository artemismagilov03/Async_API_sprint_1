from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from movies_api.api.v1.enums import PersonSortOption
from movies_api.api.v1.schemas import FilmRoles, Person
from movies_api.services.person import PersonService, get_person_service

router = APIRouter(prefix='/api/v1/persons', tags=['persons'])


@router.get(
    '/',
    response_model=list[Person],
    summary='Get all persons',
    description='Get all persons with filters, pagination and sorting',
)
async def list_persons(
    sort: PersonSortOption = PersonSortOption.id,
    page_size: Annotated[int, Query(ge=0, le=100)] = 10,
    page_number: Annotated[int, Query(ge=0, le=100)] = 0,
    actor: Annotated[str, Query(max_length=255, title='Actor name')] = '',
    writer: Annotated[str, Query(max_length=255, title='Writer name')] = '',
    director: Annotated[str, Query(max_length=255, title='Director name')] = '',
    person_service: PersonService = Depends(get_person_service),
) -> list[Person]:
    """List of persons"""
    if not (persons := await person_service.get_by_list(sort, page_size, page_number, actor, writer, director)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='persons not found')
    return [
        Person(
            uuid=person.id,
            full_name=person.full_name,
            films=[FilmRoles(uuid=film.id, roles=film.roles) for film in person.films],
        )
        for person in persons
    ]


@router.get(
    '/search',
    response_model=list[Person],
    summary='Get all persons of search query',
    description='Get all persons of search query with filters, pagination and sorting',
)
async def search_persons(
    query: Annotated[str, Query(max_length=255, title='Person full_name')] = '',
    sort: PersonSortOption = PersonSortOption.id,
    page_size: Annotated[int, Query(ge=0, le=100)] = 10,
    page_number: Annotated[int, Query(ge=0, le=100)] = 0,
    actor: Annotated[str, Query(max_length=255, title='Actor name')] = '',
    writer: Annotated[str, Query(max_length=255, title='Writer name')] = '',
    director: Annotated[str, Query(max_length=255, title='Director name')] = '',
    person_service: PersonService = Depends(get_person_service),
) -> list[Person]:
    """List of persons with searching by full_name"""
    persons = await person_service.search_by_full_name(query, sort, page_size, page_number, actor, writer, director)
    if not persons:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='persons not found')
    return [
        Person(
            uuid=person.id,
            full_name=person.full_name,
            films=[FilmRoles(uuid=film.id, roles=film.roles) for film in person.films],
        )
        for person in persons
    ]


@router.get(
    '/{uuid}',
    response_model=Person,
    summary='Get person',
    description='Get person by uuid',
)
async def person_details(
    uuid: UUID,
    person_service: PersonService = Depends(get_person_service),
) -> Person:
    """Single person by uuid"""
    if not (person := await person_service.get_by_id(uuid)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='person not found')
    return Person(
        uuid=person.id,
        full_name=person.full_name,
        films=[FilmRoles(uuid=film.id, roles=film.roles) for film in person.films],
    )
