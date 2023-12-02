import logging
import sys
from typing import Any

import backoff
import psycopg2
from psycopg2.extras import DictCursor

logger = logging.getLogger(__name__)


class PostgresExtractor:
    def __init__(self, dsn: dict):
        self.dsn = dsn
        self.connection = None

    def connect(self):
        logger.info("Попытка создать соединение с Postgres")
        if self.connection is None or self.connection.closed:
            self.connection = psycopg2.connect(**self.dsn, cursor_factory=DictCursor)
            logger.info("Соединение с Postgres установлено")

    def disconnect(self):
        if self.connection is not None and not self.connection.closed:
            self.connection.close()
            logger.info("Соединение с Postgres завершено")

    def get_cursor(self):
        self.connect()
        return self.connection.cursor()

    @backoff.on_exception(backoff.expo, psycopg2.Error, max_time=300, jitter=backoff.random_jitter)
    def execute_query(self, query: str, params=None):
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()

    def fetch_updated_records(self, table: str, last_modified: str) -> tuple[list[str], str]:
        query = """
            SELECT id, modified
            FROM content.{}
            WHERE modified >= %s
            ORDER BY modified
            LIMIT 100;
        """.format(
            table
        )
        results = self.execute_query(query, params=(last_modified,))
        try:
            return [result["id"] for result in results], results[-1]["modified"]
        except IndexError:
            logger.error("База данных пуста", exc_info=True)
            sys.exit(1)

    def fetch_films_by_persons(self, person_ids: list[str]) -> list[str]:
        query = """
            SELECT DISTINCT fw.id, fw.modified
            FROM content.film_work fw
            JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            WHERE pfw.person_id IN %s
            ORDER BY fw.modified
            LIMIT 100;
        """
        results = self.execute_query(query, params=(tuple(person_ids),))
        return [result["id"] for result in results]

    def fetch_films_by_related_table(self, table: str, related_ids: list[str]) -> list[str]:
        query = f"""
            SELECT DISTINCT fw.id, fw.modified
            FROM content.film_work fw
            JOIN content.{table}_film_work pfw ON pfw.film_work_id = fw.id
            WHERE pfw.{table}_id IN %s
            ORDER BY fw.modified
            LIMIT 100;
        """
        results = self.execute_query(query, params=(tuple(related_ids),))
        return [result["id"] for result in results]

    def fetch_film_details(self, film_ids: list[str]) -> list[dict[str, Any]]:
        query = """
            SELECT DISTINCT
                fw.id as fw_id,
                fw.title,
                fw.description,
                fw.rating,
                fw.type,
                fw.created,
                fw.modified,
                pfw.role,
                p.id as person_id,
                p.full_name,
                g.name as genre_name
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            WHERE fw.id IN %s;
        """
        return self.execute_query(query, params=(tuple(film_ids),))

    def get_earliest_modified_date(self, table: str) -> str:
        query = """
            SELECT MIN(modified) as earliest_modified
            FROM content.{};
        """.format(
            table
        )
        result = self.execute_query(query)[0]
        return result["earliest_modified"] if result else None
