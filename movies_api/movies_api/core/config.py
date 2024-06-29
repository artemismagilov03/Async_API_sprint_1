import logging
import os

from pydantic_settings import BaseSettings

from movies_api.core.logger import LOG_FORMAT, LOG_LEVEL


class Settings(BaseSettings):
    PROJECT_NAME: str = 'movies'

    REDIS_HOST: str = '127.0.0.1'
    REDIS_PORT: int = 6379

    ELASTIC_HOST: str = '127.0.0.1'
    ELASTIC_PORT: int = 9200

    BASE_DIR: str = os.getcwd()

    FILM_CACHE_EXPIRE_IN_SECONDS: int = 60 * 5
    GENRE_CACHE_EXPIRE_IN_SECONDS: int = 60 * 5
    PERSON_CACHE_EXPIRE_IN_SECONDS: int = 60 * 5

    MOVIES_INDEX: str = 'movies'
    GENRES_INDEX: str = 'genres'
    PERSONS_INDEX: str = 'persons'


logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
settings = Settings()
