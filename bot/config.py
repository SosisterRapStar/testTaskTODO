from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    api_key: str = Field(alias="BOT_KEY")

settings = Settings()