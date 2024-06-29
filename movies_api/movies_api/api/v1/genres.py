from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from movies_api.api.v1.enums import GenreSortOption
from movies_api.api.v1.schemas import Genre
from movies_api.services.genre import GenreService, get_genre_service

router = APIRouter(prefix='/api/v1/genres', tags=['genres'])


@router.get(
    '/',
    response_model=list[Genre],
    summary='Get all genres',
    description='Get all genres with filters, pagination and sorting',
)
async def list_genres(
    sort: GenreSortOption = GenreSortOption.id,
    page_size: Annotated[int, Query(ge=0, le=100)] = 10,
    page_number: Annotated[int, Query(ge=0, le=100)] = 0,
    genre_service: GenreService = Depends(get_genre_service),
) -> list[Genre]:
    """List of genres"""
    if not (genres := await genre_service.get_by_list(sort, page_size, page_number)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='films not found')
    return [Genre(uuid=genre.id, name=genre.name) for genre in genres]


@router.get(
    '/search',
    response_model=list[Genre],
    summary='Get all genres of search query',
    description='Get all genres of search query with pagination and sorting',
)
async def search_genres(
    query: Annotated[str, Query(max_length=255, title='Genre name')] = '',
    sort: GenreSortOption = GenreSortOption.id,
    page_size: Annotated[int, Query(ge=0, le=100)] = 10,
    page_number: Annotated[int, Query(ge=0, le=100)] = 0,
    genre_service: GenreService = Depends(get_genre_service),
) -> list[Genre]:
    """List of genres with searching by name"""
    if not (genres := await genre_service.search_by_name(query, sort, page_size, page_number)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='genres not found')
    return [Genre(uuid=genre.id, name=genre.name) for genre in genres]


@router.get(
    '/{uuid}',
    response_model=Genre,
    summary='Get genre',
    description='Get genre by uuid',
)
async def genre_details(
    uuid: UUID,
    genre_service: GenreService = Depends(get_genre_service),
) -> Genre:
    """Single genre by uuid"""
    if not (genre := await genre_service.get_by_id(uuid)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='genre not found')
    return Genre(uuid=genre.id, name=genre.name)
