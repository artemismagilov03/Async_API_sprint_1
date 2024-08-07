from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from movies_api.api.v1.enums import FilmSortOption
from movies_api.api.v1.schemas import Film
from movies_api.services.film import FilmService, get_film_service

router = APIRouter(prefix='/api/v1/films', tags=['films'])


@router.get(
    '/',
    response_model=list[Film],
    summary='Get all films',
    description='Get all films with filters, pagination and sorting',
)
async def list_films(
    sort: FilmSortOption = FilmSortOption.id,
    page_size: Annotated[int, Query(ge=0, le=100)] = 10,
    page_number: Annotated[int, Query(ge=0, le=100)] = 0,
    genre: Annotated[str, Query(max_length=255, title='Genre name')] = '',
    actor: Annotated[str, Query(max_length=255, title='Actor name')] = '',
    writer: Annotated[str, Query(max_length=255, title='Writer name')] = '',
    director: Annotated[str, Query(max_length=255, title='Director name')] = '',
    film_service: FilmService = Depends(get_film_service),
) -> list[Film]:
    """List of films"""
    if not (films := await film_service.get_by_list(sort, page_size, page_number, genre, actor, writer, director)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='films not found')
    return [Film(uuid=film.id, title=film.title, imdb_rating=film.rating) for film in films]


@router.get(
    '/search',
    response_model=list[Film],
    summary='Get all films of search query',
    description='Get all films of search query with filters, pagination and sorting',
)
async def search_films(
    query: Annotated[str, Query(max_length=255, title='Film title')] = '',
    sort: FilmSortOption = FilmSortOption.id,
    page_size: Annotated[int, Query(ge=0, le=100)] = 10,
    page_number: Annotated[int, Query(ge=0, le=100)] = 0,
    genre: Annotated[str, Query(max_length=255, title='Genre name')] = '',
    actor: Annotated[str, Query(max_length=255, title='Actor name')] = '',
    writer: Annotated[str, Query(max_length=255, title='Writer name')] = '',
    director: Annotated[str, Query(max_length=255, title='Director name')] = '',
    film_service: FilmService = Depends(get_film_service),
) -> list[Film]:
    """List of films with searching by title"""
    if not (
        films := await film_service.search_by_title(query, sort, page_size, page_number, genre, actor, writer, director)
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='films not found')
    return [Film(uuid=film.id, title=film.title, imdb_rating=film.rating) for film in films]


@router.get(
    '/{uuid}/film',
    response_model=list[Film],
    summary='Get all films by person',
    description='Get all films by uuid person with pagination and sorting',
)
async def person_films(
    uuid: UUID,
    sort: FilmSortOption = FilmSortOption.id,
    page_size: Annotated[int, Query(ge=0, le=100)] = 10,
    page_number: Annotated[int, Query(ge=0, le=100)] = 0,
    film_service: FilmService = Depends(get_film_service),
) -> list[Film]:
    """List of films by person"""
    if not (films := await film_service.get_films_by_person(uuid, sort, page_size, page_number)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='films not found')
    return [Film(uuid=film.id, title=film.title, imdb_rating=film.rating) for film in films]


@router.get(
    '/{uuid}',
    response_model=Film,
    summary='Get film',
    description='Get film by uuid',
)
async def film_details(
    uuid: UUID,
    film_service: FilmService = Depends(get_film_service),
) -> Film:
    """Single film by uuid"""
    if not (film := await film_service.get_by_id(uuid)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='film not found')
    return Film(uuid=film.id, title=film.title, imdb_rating=film.rating)
