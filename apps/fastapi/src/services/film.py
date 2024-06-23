from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from api.v1.enums import FilmSortOption
from db.elastic import get_elastic
from db.redis import get_redis
from api.v1.schemas import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def get_by_list(
        self,
        sort: FilmSortOption,
        page_size: int,
        page_number: int,
        genre: str,
        actor: str,
        writer: str,
        director: str,
    ) -> list[Film]:
        films = (
            None  # await self._films_from_cache(sort, page_size, page_number)
        )
        if not films:
            films = await self._get_films_from_elastic(
                sort, page_size, page_number, genre, actor, writer, director
            )
            if not films:
                return None
            # await self._put_film_to_cache(films)

        return films

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index='movies', id=film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def _get_films_from_elastic(
        self,
        sort: FilmSortOption,
        page_size: int,
        page_number: int,
        genre: str,
        actor: str,
        writer: str,
        director: str,
    ) -> list[Film]:
        filters = []

        if genre:
            filters.append({'match': {'genres': genre}})
        if actor:
            filters.append(
                {
                    'nested': {
                        'path': 'actors',
                        'query': {
                            'bool': {
                                'must': [{'match': {'actors.name': actor}}]
                            }
                        },
                    }
                }
            )
        if writer:
            filters.append(
                {
                    'nested': {
                        'path': 'writers',
                        'query': {
                            'bool': {
                                'must': [{'match': {'writers.name': writer}}]
                            }
                        },
                    }
                }
            )
        if director:
            filters.append(
                {
                    'nested': {
                        'path': 'directors',
                        'query': {
                            'bool': {
                                'must': [
                                    {'match': {'directors.name': director}}
                                ]
                            }
                        },
                    }
                }
            )

        query = {'bool': {'must': filters}} if filters else {'match_all': {}}
        order, row = ('desc', sort[1:]) if sort[0] == '-' else ('asc', sort)
        sort = [{row: {'order': order}}]

        body = {
            'query': query,
            'from': page_number,
            'size': page_size,
            'sort': sort,
        }

        docs = await self.elastic.search(index='movies', body=body)
        return [Film(**doc['_source']) for doc in docs['hits']['hits']]

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        if data := await self.redis.get(film_id):
            return None
        film = Film.model_validate_json(data)
        return film

    # async def _films_from_cache(
    #     self, sort: FilmRow, page_size: int, page_number: int
    # ) -> Optional[Film]:
    #     data = await self.redis.set()
    #     if not data:
    #         return None
    #
    #     film = Film.parse_raw(data)
    #     return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(
            str(film.id), film.json(), FILM_CACHE_EXPIRE_IN_SECONDS
        )

    #
    # async def _put_films_to_cache(self, films: list[Film]):
    #     await self.redis.set(
    #         film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS
    #     )


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
