from fastapi import APIRouter, HTTPException, status, Depends

from api.v1.schemas import Film
from services.film import FilmService, get_film_service


router = APIRouter(prefix='/api/v1/films', tags=['films'])


@router.get('/{film_id}', response_model=Film)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='film not found'
        )
    return Film(id=film.id, title=film.title)
