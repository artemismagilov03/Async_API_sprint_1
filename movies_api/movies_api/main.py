from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from movies_api.api.v1 import films, genres, persons
from movies_api.core.config import settings
from movies_api.db import elastic, redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.rd = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
    elastic.es = AsyncElasticsearch(f'http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}')
    yield
    await redis.rd.aclose()
    await elastic.es.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


app.include_router(films.router)
app.include_router(genres.router)
app.include_router(persons.router)
