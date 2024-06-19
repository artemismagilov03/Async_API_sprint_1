from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis import Redis
from elasticsearch import AsyncElasticsearch

from api.v1 import films
from core import config
from db import elastic
from db import redis


app = FastAPI(
    title=config.PROJECT_NAME,
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    redis.rd = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    elastic.es = AsyncElasticsearch(
        f'http://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'
    )


@app.on_event('shutdown')
async def shutdown():
    await redis.rd.close()
    await elastic.es.close()


app.include_router(films.router)
