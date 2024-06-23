from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends, Query

from src.api.v1.schemas import Genre
from src.api.v1.enums import GenreSortOption
from src.services.genre import GenreService, get_genre_service


router = APIRouter(prefix='/api/v1/genres', tags=['genres'])


@router.get('/{genre_id}', response_model=Genre)
async def genre_details(
    uuid: UUID,
    genre_service: GenreService = Depends(get_genre_service),
) -> Genre:
    """Page with single genre"""
    if not (genre := await genre_service.get_by_id(uuid)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='genre not found'
        )
    return Genre(id=genre.id, name=genre.name)


@router.get('/', response_model=list[Genre])
async def list_genres(
    sort: GenreSortOption = GenreSortOption.id,
    page_size: Annotated[int, Query(ge=0, le=100)] = 10,
    page_number: Annotated[int, Query(ge=0, le=100)] = 0,
    genre_service: GenreService = Depends(get_genre_service),
) -> list[Genre]:
    """Main page with list of genres"""
    genres = await genre_service.get_by_list(sort, page_size, page_number)
    if not genres:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='films not found'
        )
    return [Genre(id=genre.id, name=genre.name) for genre in genres]
