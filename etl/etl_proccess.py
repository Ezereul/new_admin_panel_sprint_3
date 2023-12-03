import logging
from datetime import datetime

from etl.extract import PostgresExtractor
from etl.load import ElasticsearchLoader
from etl.storage import State
from etl.transfrom import DataTransform

logger = logging.getLogger(__name__)


class ETLProcess:
    TABLES = ("film_work", "genre", "person")

    def __init__(self, postgres_dsl: dict, es_host: str, state_storage: State):
        self.pg_client = PostgresExtractor(postgres_dsl)
        self.es_client = ElasticsearchLoader(es_host)
        self.transform = DataTransform()
        self.storage = state_storage

    def get_state_key(self, table: str) -> str:
        return table + "_last_updated"

    def run(self):
        for table in self.TABLES:
            try:
                self.process_table(table)
            except Exception as e:
                logger.error(f"Ошибка при обработке таблицы {table}: {e}")
                continue

        self.pg_client.disconnect()
        self.es_client.close()

    def process_table(self, table: str):
        logger.info(f"Загрузка таблицы {table}")
        state = self.storage.get_state(self.get_state_key(table))
        last_modified = self.get_last_modified(state, table)

        while True:
            updated_records, last_modified_of_batch = self.pg_client.fetch_updated_records(table, last_modified)
            if not updated_records:
                break

            transformed_data = self.transform_data(table, updated_records)
            self.es_client.load_to_elasticsearch(transformed_data)

            self.storage.set_state(key=self.get_state_key(table), value=str(last_modified_of_batch))

            if last_modified_of_batch > last_modified:
                last_modified = last_modified_of_batch
            else:
                logger.info(f"Таблица {table} загружена")
                break

    def get_last_modified(self, state: str, table: str):
        if not state:
            return self.pg_client.get_earliest_modified_date(table)
        return datetime.fromisoformat(state)

    def transform_data(self, table, updated_records):
        if table == "film_work":
            film_details = self.pg_client.fetch_film_details(updated_records)
        else:
            film_ids = self.pg_client.fetch_films_by_related_table(table, updated_records)
            film_details = self.pg_client.fetch_film_details(film_ids)

        return self.transform.consolidate_films(film_details)
