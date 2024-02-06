from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=True,
        env_prefix='BACKEND_SERVER__'
    )

    HOST: str
    PORT: int

    LOG_LEVEL: str = 'DEBUG'


server_settings = Settings()
