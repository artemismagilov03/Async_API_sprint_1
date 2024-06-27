import json
from functools import lru_cache
from typing import Optional
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis

from movies_api.api.v1.enums import FilmSortOption
from movies_api.core import config
from movies_api.db.elastic import get_elastic
from movies_api.db.redis import get_redis
from movies_api.models.film import Film


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, uuid: UUID) -> Optional[Film]:
        if not (film := await self._film_from_cache(uuid)):
            if not (film := await self._get_film_from_elastic(uuid)):
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
        if not (films := await self._films_from_cache(sort, page_size, page_number, genre, actor, writer, director)):
            if not (
                films := await self._get_films_from_elastic(
                    sort, page_size, page_number, genre, actor, writer, director
                )
            ):
                return None
            await self._put_films_to_cache(films, sort, page_size, page_number, genre, actor, writer, director)

        return films

    async def search_by_title(
        self,
        query: str,
        sort: FilmSortOption,
        page_size: int,
        page_number: int,
        genre: str,
        actor: str,
        writer: str,
        director: str,
    ) -> list[Film]:
        if not (
            films := await self._films_from_cache(query, sort, page_size, page_number, genre, actor, writer, director)
        ):
            if not (
                films := await self._search_films_from_elastic(
                    query, sort, page_size, page_number, genre, actor, writer, director
                )
            ):
                return None
            await self._put_films_to_cache(films, query, sort, page_size, page_number, genre, actor, writer, director)

        return films

    async def get_films_by_person(self, uuid: UUID, sort, page_size: int, page_number: int):
        if not (films := await self._films_from_cache(uuid, sort, page_size, page_number)):
            if not (films := await self._get_films_by_person_from_elastic(uuid, sort, page_size, page_number)):
                return None
            await self._put_films_to_cache(films, uuid, sort, page_size, page_number)

        return films

    async def _get_film_from_elastic(self, uuid: UUID) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index=config.MOVIES_INDEX, id=f'{uuid}')
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
            filters.append({'match': {'actors_names': actor}})
        if writer:
            filters.append({'match': {'writers_name': writer}})
        if director:
            filters.append({'match': {'directors_name': director}})

        query = {'bool': {'must': filters}} if filters else {'match_all': {}}
        order, row = ('desc', sort[1:]) if sort[0] == '-' else ('asc', sort)
        sort = [{row: {'order': order}}]

        body = {
            'query': query,
            'from': page_number,
            'size': page_size,
            'sort': sort,
        }

        docs = await self.elastic.search(index=config.MOVIES_INDEX, body=body)
        return [Film(**doc['_source']) for doc in docs['hits']['hits']]

    async def _search_films_from_elastic(
        self,
        query: str,
        sort: FilmSortOption,
        page_size: int,
        page_number: int,
        genre: str,
        actor: str,
        writer: str,
        director: str,
    ) -> list[Film]:
        filters = [{'match': {'title': query}}] if query else []

        if genre:
            filters.append({'match': {'genres': genre}})
        if actor:
            filters.append({'match': {'actors_name': actor}})
        if writer:
            filters.append({'match': {'writers_name': writer}})
        if director:
            filters.append({'match': {'directors_name': director}})

        query = {'bool': {'must': filters}} if filters else {'match_all': {}}
        order, row = ('desc', sort[1:]) if sort[0] == '-' else ('asc', sort)
        sort = [{row: {'order': order}}]

        body = {
            'query': query,
            'from': page_number,
            'size': page_size,
            'sort': sort,
        }

        docs = await self.elastic.search(index=config.MOVIES_INDEX, body=body)
        return [Film(**doc['_source']) for doc in docs['hits']['hits']]

    async def _get_films_by_person_from_elastic(
        self, uuid: UUID, sort: FilmSortOption, page_size: int, page_number: int
    ):
        filters = [
            {'nested': {'path': r, 'query': {'match': {f'{r}.id': uuid}}}} for r in ('actors', 'writers', 'directors')
        ]

        query = {'bool': {'should': filters}}
        order, row = ('desc', sort[1:]) if sort[0] == '-' else ('asc', sort)
        sort = [{row: {'order': order}}]

        body = {
            'query': query,
            'from': page_number,
            'size': page_size,
            'sort': sort,
        }

        docs = await self.elastic.search(index=config.MOVIES_INDEX, body=body)
        return [Film(**doc['_source']) for doc in docs['hits']['hits']]

    async def _film_from_cache(self, uuid: UUID) -> Optional[Film]:
        if data := await self.redis.get(f'{uuid}'):
            return None
        film = Film.model_validate_json(data)
        return film

    async def _films_from_cache(self, *args) -> Optional[Film]:
        key = 'movies:' + ','.join(f'{arg}' for arg in args)
        data = await self.redis.get(key)
        if not data:
            return None
        films = [Film(**f) for f in json.loads(data)]
        return films

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(f'{film.id}', film.json(), config.FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _put_films_to_cache(self, films: list[Film], *args):
        key = 'movies:' + ','.join(f'{arg}' for arg in args)
        value = json.dumps([jsonable_encoder(f) for f in films])
        await self.redis.set(key, value, config.FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
