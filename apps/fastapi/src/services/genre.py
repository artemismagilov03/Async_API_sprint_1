from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from src.api.v1.enums import GenreSortOption
from src.api.v1.schemas import Genre
from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.core import config


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        if not (genre := await self._genre_from_cache(genre_id)):
            if not (genre := await self._get_genre_from_elastic(genre_id)):
                return None
            await self._put_genre_to_cache(genre)

        return genre

    async def get_by_list(
        self,
        sort: GenreSortOption,
        page_size: int,
        page_number: int,
    ) -> list[Genre]:
        genres = (
            None  # await self._genres_from_cache(sort, page_size, page_number)
        )
        if not genres:
            genres = await self._get_genres_from_elastic(
                sort, page_size, page_number
            )
            if not genres:
                return None
            # await self._put_genre_to_cache(films)

        return genres

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        try:
            doc = await self.elastic.get(index='genres', id=genre_id)
        except NotFoundError:
            return None
        return Genre(**doc['_source'])

    async def _get_genres_from_elastic(
        self,
        sort: GenreSortOption,
        page_size: int,
        page_number: int,
    ) -> list[Genre]:
        query = {'match_all': {}}
        order, row = ('desc', sort[1:]) if sort[0] == '-' else ('asc', sort)
        sort = [{row: {'order': order}}]

        body = {
            'query': query,
            'from': page_number,
            'size': page_size,
            'sort': sort,
        }

        docs = await self.elastic.search(index='genres', body=body)
        return [Genre(**doc['_source']) for doc in docs['hits']['hits']]

    async def _genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        if not (data := await self.redis.get(genre_id)):
            return None

        genre = Genre.model_validate_json(data)
        return genre

    # async def _genres_from_cache(
    #     self, sort: FilmRow, page_size: int, page_number: int
    # ) -> Optional[Film]:
    #     data = await self.redis.set()
    #     if not data:
    #         return None
    #
    #     film = Film.parse_raw(data)
    #     return film

    async def _put_genre_to_cache(self, genre: Genre):
        await self.redis.set(
            str(genre.id), genre.json(), config.GENRE_CACHE_EXPIRE_IN_SECONDS
        )

    #
    # async def _put_genres_to_cache(self, films: list[Film]):
    #     await self.redis.set(
    #         film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS
    #     )


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
