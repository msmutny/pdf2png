from typing import Optional

from pydantic import BaseSettings, RedisDsn


class Settings(BaseSettings):
    database_url: str = "sqlite:///data/database.db"
    redis_url: Optional[RedisDsn]
    rabbitmq_host: str = "localhost"
    poppler_path: Optional[str]

    class Config:
        env_file = ".env"


settings = Settings()
