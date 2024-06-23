from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends, Query, Path

from src.api.v1.schemas import Person
from src.api.v1.enums import PersonSortOption
from src.services.person import PersonService, get_person_service


router = APIRouter(prefix='/api/v1/persons', tags=['persons'])


@router.get('/{person_id}', response_model=Person)
async def person_details(
    person_id: Annotated[str, Path(max_length=255)],
    person_service: PersonService = Depends(get_person_service),
) -> Person:
    """Page with single person"""
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='person not found'
        )
    return Person(id=person.id, full_name=person.full_name)


@router.get('/', response_model=list[Person])
async def list_persons(
    sort: PersonSortOption = PersonSortOption.id,
    page_size: Annotated[int, Query(ge=0, le=100)] = 10,
    page_number: Annotated[int, Query(ge=0, le=100)] = 0,
    genre: Annotated[str, Query(max_length=255, title='Genre name')] = '',
    actor: Annotated[str, Query(max_length=255, title='Actor name')] = '',
    writer: Annotated[str, Query(max_length=255, title='Writer name')] = '',
    director: Annotated[
        str, Query(max_length=255, title='Director name')
    ] = '',
    person_service: PersonService = Depends(get_person_service),
) -> list[Person]:
    """Main page with list of persons"""
    persons = await person_service.get_by_list(
        sort, page_size, page_number, genre, actor, writer, director
    )
    if not persons:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='persons not found'
        )
    return [
        Person(id=person.id, full_name=person.full_name) for person in persons
    ]
