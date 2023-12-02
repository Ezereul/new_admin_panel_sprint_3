import logging

from etl.config import settings
from etl.etl_proccess import ETLProcess
from etl.storage import JsonFileStorage, State


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    logger = logging.getLogger(__name__)

    logger.info("НАЧИНАЕМ")
    dsl = {
        "dbname": settings.postgres_db,
        "user": settings.postgres_user,
        "password": settings.postgres_password,
        "host": settings.db_host,
        "port": settings.db_port,
    }
    es_host = settings.es_host

    etl = ETLProcess(
        postgres_dsl=dsl, es_host=es_host, state_storage=State(storage=JsonFileStorage(file_path="storage.json"))
    )
    logger.info("Запуск ETL")
    etl.run()
    logger.info("ETL завершил работу")


if __name__ == "__main__":
    main()
