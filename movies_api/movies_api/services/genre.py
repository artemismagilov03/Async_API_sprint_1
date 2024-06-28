from functools import lru_cache
from typing import Optional
from uuid import UUID

import orjson
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from movies_api.api.v1.enums import GenreSortOption
from movies_api.core import config
from movies_api.db.elastic import get_elastic
from movies_api.db.redis import get_redis
from movies_api.models.genre import Genre


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, uuid: UUID) -> Optional[Genre]:
        if not (genre := await self._genre_from_cache(uuid)):
            if not (genre := await self._get_genre_from_elastic(uuid)):
                return None
            await self._put_genre_to_cache(genre)

        return genre

    async def get_by_list(self, sort: GenreSortOption, page_size: int, page_number: int) -> list[Genre]:
        if not (genres := await self._genres_from_cache(sort, page_size, page_number)):
            if not (genres := await self._get_genres_from_elastic(sort, page_size, page_number)):
                return None
            await self._put_genres_to_cache(genres, sort, page_size, page_number)

        return genres

    async def search_by_name(
        self,
        query: str,
        sort: GenreSortOption,
        page_size: int,
        page_number: int,
    ) -> list[Genre]:
        if not (genres := await self._genres_from_cache(query, sort, page_size, page_number)):
            if not (genres := await self._search_genres_from_elastic(query, sort, page_size, page_number)):
                return None
            await self._put_genres_to_cache(genres)

        return genres

    async def _get_genre_from_elastic(self, uuid: UUID) -> Optional[Genre]:
        try:
            doc = await self.elastic.get(index=config.GENRES_INDEX, id=f'{uuid}')
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

        docs = await self.elastic.search(index=config.GENRES_INDEX, body=body)
        return [Genre(**doc['_source']) for doc in docs['hits']['hits']]

    async def _search_genres_from_elastic(
        self,
        query: str,
        sort: GenreSortOption,
        page_size: int,
        page_number: int,
    ) -> list[Genre]:
        filters = {'match': {'name': query}} if query else []

        query = filters if filters else {'match_all': {}}
        order, row = ('desc', sort[1:]) if sort[0] == '-' else ('asc', sort)
        sort = [{row: {'order': order}}]

        body = {
            'query': query,
            'from': page_number,
            'size': page_size,
            'sort': sort,
        }

        docs = await self.elastic.search(index=config.GENRES_INDEX, body=body)
        return [Genre(**doc['_source']) for doc in docs['hits']['hits']]

    async def _genre_from_cache(self, uuid: UUID) -> Optional[Genre]:
        key = f'{config.GENRES_INDEX}:{uuid}'
        if not (data := await self.redis.get(key)):
            return None

        genre = Genre.model_validate_json(data)
        return genre

    async def _genres_from_cache(self, *args) -> list[Genre]:
        key = f'{config.GENRES_INDEX}:' + ','.join(f'{arg}' for arg in args)
        if not (data := await self.redis.get(key)):
            return None
        genres = [Genre(**g) for g in orjson.loads(data)]
        return genres

    async def _put_genre_to_cache(self, genre: Genre):
        key = f'{config.GENRES_INDEX}:{genre.id}'
        await self.redis.set(key, genre.json(), config.GENRE_CACHE_EXPIRE_IN_SECONDS)

    async def _put_genres_to_cache(self, genres: list[Genre], *args):
        key = f'{config.GENRES_INDEX}:' + ','.join(f'{arg}' for arg in args)
        value = orjson.dumps([g for g in genres])
        await self.redis.set(key, value, config.GENRES_INDEX)


@lru_cache
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
