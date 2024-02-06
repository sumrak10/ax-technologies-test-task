from pydantic_settings import BaseSettings, SettingsConfigDict

from .server import server_settings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=True,
        env_prefix='DB__'
    )

    HOST: str
    PORT: int
    NAME: str
    USER: str
    PASS: str

    POOL_SIZE: int
    MAX_POOL_OVERFLOW: int
    POOL_TIMEOUT: int

    DB_AND_DRIVER: str = "postgresql+asyncpg"

    @property
    def DSN(self):
        return f"{self.DB_AND_DRIVER}://{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.NAME}"


db_settings = Settings()
