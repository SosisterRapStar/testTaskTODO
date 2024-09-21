from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import Field


class BSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="/home/vanya/new_test_task/bot/.env",
        env_file_encoding="utf-8",
        extra="ignore",  # здесь можно менять окружение на тестовое
    )


class Settings(BSettings):
    api_key: str = Field(alias="BOT_KEY")
    backend_url: str = "http://localhost/"
    redis_url: str = "redis://localhost:6379"
    redis_max_pool_size: int = 5
    redis_host: str = "localhost"
    redis_port: str = "6379"
    redis_db: int = 1


settings = Settings()
