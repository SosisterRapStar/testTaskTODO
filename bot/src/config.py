from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import Field


class BSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="/home/vanya/new_test_task/bot/.env", env_file_encoding="utf-8", extra="ignore" # здесь можно менять окружение на тестовое
    )
    

class Settings(BSettings):
    api_key: str = Field(alias="BOT_KEY")
    backend_url: str = ""

settings = Settings()