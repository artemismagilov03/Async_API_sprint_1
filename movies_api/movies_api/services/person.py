from functools import lru_cache
from typing import Optional
from uuid import UUID

import orjson
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from movies_api.api.v1.enums import PersonSortOption
from movies_api.core.config import settings
from movies_api.db.elastic import get_elastic
from movies_api.db.redis import get_redis
from movies_api.models.persons import Person


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
        actor: str,
        writer: str,
        director: str,
    ) -> list[Person]:
        if not (persons := await self._persons_from_cache(sort, page_size, page_number, actor, writer, director)):
            if not (
                persons := await self._get_persons_from_elastic(sort, page_size, page_number, actor, writer, director)
            ):
                return None
            await self._put_persons_to_cache(persons)

        return persons

    async def search_by_full_name(
        self,
        query: str,
        sort: PersonSortOption,
        page_size: int,
        page_number: int,
        actor: str,
        writer: str,
        director: str,
    ):
        if not (persons := await self._persons_from_cache(sort, page_size, page_number, actor, writer, director)):
            if not (
                persons := await self._search_persons_from_elastic(
                    query,
                    sort,
                    page_size,
                    page_number,
                    actor,
                    writer,
                    director,
                )
            ):
                return None
            await self._put_persons_to_cache(persons)

        return persons

    async def _get_person_from_elastic(self, uuid: UUID) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index=settings.PERSONS_INDEX, id=f'{uuid}')
        except NotFoundError:
            return None
        return Person(**doc['_source'])

    async def _get_persons_from_elastic(
        self,
        sort: PersonSortOption,
        page_size: int,
        page_number: int,
        actor: str,
        writer: str,
        director: str,
    ) -> list[Person]:
        filters = []
        if actor:
            filters.append(
                {'nested': {'path': 'films', 'query': {'match': {'films.roles': 'actor', 'full_name': actor}}}}
            )
        if writer:
            filters.append(
                {'nested': {'path': 'films', 'query': {'match': {'films.roles': 'writer', 'full_name': writer}}}}
            )
        if director:
            filters.append(
                {'nested': {'path': 'films', 'query': {'match': {'films.roles': 'director', 'full_name': director}}}}
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

        docs = await self.elastic.search(index=settings.PERSONS_INDEX, body=body)
        return [Person(**doc['_source']) for doc in docs['hits']['hits']]

    async def _search_persons_from_elastic(
        self,
        query: str,
        sort: PersonSortOption,
        page_size: int,
        page_number: int,
        actor: str,
        writer: str,
        director: str,
    ) -> list[Person]:
        filters = {'match': {'full_name': query}} if query else []
        if actor:
            filters.append(
                {'nested': {'path': 'films', 'query': {'match': {'films.roles': 'actor', 'full_name': actor}}}}
            )
        if writer:
            filters.append(
                {'nested': {'path': 'films', 'query': {'match': {'films.roles': 'writer', 'full_name': writer}}}}
            )
        if director:
            filters.append(
                {'nested': {'path': 'films', 'query': {'match': {'films.roles': 'director', 'full_name': director}}}}
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

        docs = await self.elastic.search(index=settings.PERSONS_INDEX, body=body)
        return [Person(**doc['_source']) for doc in docs['hits']['hits']]

    async def _person_from_cache(self, uuid: UUID) -> Optional[Person]:
        key = f'{settings.PERSONS_INDEX}:{uuid}'
        if not (data := await self.redis.get(key)):
            return None

        person = Person.model_validate_json(data)
        return person

    async def _persons_from_cache(self, *args) -> list[Person]:
        key = f'{settings.PERSONS_INDEX}:' + ','.join(f'{arg}' for arg in args)
        if not (data := await self.redis.get(key)):
            return None
        persons = [Person(**g) for g in orjson.loads(data)]
        return persons

    async def _put_person_to_cache(self, person: Person):
        key = f'{settings.PERSONS_INDEX}:{person.id}'
        await self.redis.set(key, person.model_dump_json(), settings.PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _put_persons_to_cache(self, persons: list[Person], *args):
        key = f'{settings.PERSONS_INDEX}:' + ','.join(f'{arg}' for arg in args)
        value = orjson.dumps([p.model_dump() for p in persons])
        await self.redis.set(key, value, settings.PERSON_CACHE_EXPIRE_IN_SECONDS)


@lru_cache
def get_person_service(
    redis: Redis = Depends(get_redis), elastic: AsyncElasticsearch = Depends(get_elastic)
) -> PersonService:
    return PersonService(redis, elastic)
