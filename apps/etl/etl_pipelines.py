from contextlib import contextmanager
from time import sleep

import psycopg
from elasticsearch import Elasticsearch

import config
from etl_logger import logger
from etl_utils import backoff


class ETL:
    @contextmanager
    def create_conn_pg(self):
        with psycopg.connect(
            f'postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DBNAME}'
        ) as conn:
            with conn.cursor() as cur:
                yield cur

    @contextmanager
    def create_conn_es(self):
        with Elasticsearch(
            f'http://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}/'
        ) as es:
            yield es

    def pipeline_film_works(
        self, pg_conn: psycopg.Cursor, es_conn: Elasticsearch
    ):
        self.indexing_es(
            'movies', 'sqls/fetch_film_works.sql', pg_conn, es_conn
        )
        logger.info('Successfully indexing film works')

    def pipeline_genres(self, pg_conn: psycopg.Cursor, es_conn: Elasticsearch):
        self.indexing_es('genres', 'sqls/fetch_genres.sql', pg_conn, es_conn)
        logger.info('Successfully indexing genres')

    def pipeline_persons(
        self, pg_conn: psycopg.Cursor, es_conn: Elasticsearch
    ): ...

    def indexing_es(
        self,
        index: str,
        sql_path: str,
        pg_conn: psycopg.Cursor,
        es_conn: Elasticsearch,
    ):
        with open(sql_path) as f:
            sql = f.read()

        pg_conn.execute(sql)
        data = pg_conn.fetchmany(config.SIZE_CHUNK)

        while data:
            body = []
            for row in data:
                body.extend(
                    (
                        {
                            'index': {
                                '_index': index,
                                '_id': row[0]['id'],
                            }
                        },
                        row[0],
                    )
                )

            es_conn.bulk(body=body)
            data = pg_conn.fetchmany(config.SIZE_CHUNK)

    @backoff(steps=3)
    def run(self):
        with self.create_conn_pg() as pg_conn, self.create_conn_es() as es_conn:
            self.pipeline_film_works(pg_conn, es_conn)
            self.pipeline_genres(pg_conn, es_conn)
            # self.pipeline_persons(pg_conn, es_conn)
        logger.info('ETL process successfully finished')


if __name__ == '__main__':
    etl = ETL()
    while True:
        etl.run()
        sleep(30)
