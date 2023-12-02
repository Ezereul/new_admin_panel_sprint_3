from pydantic.v1 import BaseSettings


class Config(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    db_port: str
    db_host: str
    es_host: str

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


settings = Config()
