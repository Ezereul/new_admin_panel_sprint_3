import abc
import json
from json import JSONDecodeError
from typing import Any, Dict


class BaseStorage(abc.ABC):
    """
    Абстрактное хранилище состояния.

    Позволяет сохранять и получать состояние.
    Способ хранения состояния может варьироваться в зависимости
    от итоговой реализации. Например, можно хранить информацию
    в базе данных или в распределённом файловом хранилище.
    """

    @abc.abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""

    @abc.abstractmethod
    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: str | None = "storage.json"):
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        with open(self.file_path, "w") as file:
            json.dump(state, file)

    def retrieve_state(self) -> dict:
        try:
            with open(self.file_path, "r") as file:
                return json.load(file)
        except (FileNotFoundError, JSONDecodeError):
            return dict()


class State:
    """Класс для работы с состояниями."""

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        try:
            state = self.storage.retrieve_state()
        except FileNotFoundError:
            state = dict()
        state[key] = value
        self.storage.save_state(state)

    def get_state(self, key: str) -> Any:
        return self.storage.retrieve_state().get(key)
