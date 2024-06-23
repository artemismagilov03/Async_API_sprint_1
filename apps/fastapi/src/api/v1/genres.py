from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends, Query, Path

from api.v1.schemas import Genre
from api.v1.enums import GenreSortOption
from services.genre import GenreService, get_genre_service


router = APIRouter(prefix='/api/v1/genres', tags=['genres'])


@router.get('/{genre_id}', response_model=Genre)
async def genre_details(
    genre_id: Annotated[str, Path(max_length=255)],
    genre_service: GenreService = Depends(get_genre_service),
) -> Genre:
    """Page with single genre"""
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='film not found'
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
