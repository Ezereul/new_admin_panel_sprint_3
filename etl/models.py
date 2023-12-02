from pydantic import BaseModel, field_validator


class BaseID(BaseModel):
    id: str


class BasePerson(BaseID):
    name: str


class ActorModel(BasePerson):
    pass


class WriterModel(BasePerson):
    pass


class FilmworkModel(BaseID):
    imdb_rating: float
    genre: list[str]
    title: str
    description: str | None
    director: list[str]
    actors_names: list[str]
    writers_names: list[str]
    actors: list[ActorModel]
    writers: list[WriterModel]

    @field_validator("imdb_rating", mode="before")
    def validate_imdb_rating(cls, value):
        return value or 0.0
