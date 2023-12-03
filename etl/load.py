import logging
from typing import Any

import backoff
from elastic_transport import TransportError
from elasticsearch import Elasticsearch
from elasticsearch.helpers import BulkIndexError, bulk

from etl.models import FilmworkModel

logger = logging.getLogger(__name__)


class ElasticsearchLoader:
    def __init__(self, host: str):
        self.client = Elasticsearch(host)

    def close(self):
        if self.client:
            self.client.close()
            logger.info("Соединение с Elasticsearch закрыто")

    def prepare_data(self, data: list[FilmworkModel]) -> dict[str, Any]:
        for doc in data:
            yield {"_index": "movies", "_id": doc.id, "_source": doc.model_dump()}

    @backoff.on_exception(backoff.expo, TransportError, max_time=300, jitter=backoff.random_jitter)
    def load_to_elasticsearch(self, data: list[FilmworkModel]) -> None:
        try:
            bulk(self.client, self.prepare_data(data))
        except BulkIndexError:
            logger.error("Ошибка индексации", exc_info=True)
