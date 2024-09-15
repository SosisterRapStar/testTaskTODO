from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict, BaseSettings


class BSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="/home/vanya/new_test_task/src/.env",
        env_file_encoding="utf-8",
        extra="ignore",  # здесь можно менять окружение на тестовое
    )


class DBSettings(BSettings):
    db_user: str = Field(default="user", alias="DB_USER")
    db_password: str = Field(default="1234", alias="DB_PASSWORD")
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: str = Field(default="5432", alias="DB_PORT")
    db_name: str = Field(default="postgres", alias="DB_NAME")

    @property
    def db_string_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


class Settings(BaseModel):
    db: DBSettings = DBSettings()


settings = Settings()
