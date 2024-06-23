from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from api.v1.enums import PersonSortOption
from db.elastic import get_elastic
from db.redis import get_redis
from api.v1.schemas import Person

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = None  # await self._person_from_cache(film_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            # await self._put_person_to_cache(film)

        return person

    async def get_by_list(
        self,
        sort: PersonSortOption,
        page_size: int,
        page_number: int,
        genre: str,
        actor: str,
        writer: str,
        director: str,
    ) -> list[Person]:
        persons = None  # await self._persons_from_cache(sort, page_size, page_number)
        if not persons:
            persons = await self._get_persons_from_elastic(
                sort, page_size, page_number, genre, actor, writer, director
            )
            if not persons:
                return None
            # await self._put_person_to_cache(films)

        return persons

    async def _get_person_from_elastic(
        self, person_id: str
    ) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index='persons', id=person_id)
        except NotFoundError:
            return None
        return Person(**doc['_source'])

    async def _get_persons_from_elastic(
        self,
        sort: PersonSortOption,
        page_size: int,
        page_number: int,
        genre: str,
        actor: str,
        writer: str,
        director: str,
    ) -> list[Person]:
        # need implementation filtering persons by diff fields
        filters = []

        query = {'bool': {'must': filters}} if filters else {'match_all': {}}
        order, row = ('desc', sort[1:]) if sort[0] == '-' else ('asc', sort)
        sort = [{row: {'order': order}}]

        body = {
            'query': query,
            'from': page_number,
            'size': page_size,
            'sort': sort,
        }

        docs = await self.elastic.search(index='persons', body=body)
        return [Person(**doc['_source']) for doc in docs['hits']['hits']]

    # async def _person_from_cache(self, film_id: str) -> Optional[Film]:
    #     data = await self.redis.get(film_id)
    #     if not data:
    #         return None
    #
    #     film = Film.model_validate_json(data)
    #     return film

    # async def _persons_from_cache(
    #     self, sort: FilmRow, page_size: int, page_number: int
    # ) -> Optional[Film]:
    #     data = await self.redis.set()
    #     if not data:
    #         return None
    #
    #     film = Film.parse_raw(data)
    #     return film

    # async def _put_persons_to_cache(self, film: Film):
    #     await self.redis.set(
    #         film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS
    #     )
    #
    # async def _put_persons_to_cache(self, films: list[Film]):
    #     await self.redis.set(
    #         film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS
    #     )


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
