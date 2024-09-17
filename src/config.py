from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict, BaseSettings
import logging

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


class SecuritySettings(BSettings):
    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_algo: str = Field(alias="JWT_ALGO")
    access_token_expire_minutes: int = Field(
        default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_minutes: int = Field(
        default=60, alias="REFRESH_TOKEN_EXPIRE_MINUTES"
    )


class Settings(BaseModel):
    db: DBSettings = DBSettings()
    security: SecuritySettings = SecuritySettings()


settings = Settings()



logger = logging.getLogger("fastapi-logger")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
