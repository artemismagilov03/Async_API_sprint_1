from functools import lru_cache
from typing import Optional
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from src.api.v1.enums import PersonSortOption
from src.api.v1.models import Person
from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.core import config


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, uuid: UUID) -> Optional[Person]:
        if not (person := await self._person_from_cache(uuid)):
            if not (person := await self._get_person_from_elastic(uuid)):
                return None
            await self._put_person_to_cache(person)

        return person

    async def get_by_list(
        self,
        sort: PersonSortOption,
        page_size: int,
        page_number: int,
    ) -> list[Person]:
        persons = None  # await self._persons_from_cache(sort, page_size, page_number)
        if not persons:
            persons = await self._get_persons_from_elastic(
                sort, page_size, page_number
            )
            if not persons:
                return None
            # await self._put_person_to_cache(films)

        return persons

    async def _get_person_from_elastic(self, uuid: UUID) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index='persons', id=str(uuid))
        except NotFoundError:
            return None
        return Person(**doc['_source'])

    async def _get_persons_from_elastic(
        self,
        sort: PersonSortOption,
        page_size: int,
        page_number: int,
    ) -> list[Person]:
        query = {'match_all': {}}
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

    async def _person_from_cache(self, uuid: UUID) -> Optional[Person]:
        if not (data := await self.redis.get(str(uuid))):
            return None

        person = Person.model_validate_json(data)
        return person

    # async def _persons_from_cache(
    #     self, sort: FilmRow, page_size: int, page_number: int
    # ) -> Optional[Film]:
    #     data = await self.redis.set()
    #     if not data:
    #         return None
    #
    #     film = Film.parse_raw(data)
    #     return film

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(
            str(person.id),
            person.json(),
            config.PERSON_CACHE_EXPIRE_IN_SECONDS,
        )

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
