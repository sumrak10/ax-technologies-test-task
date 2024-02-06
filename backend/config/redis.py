from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=True,
        env_prefix='REDIS__'
    )

    HOST: str
    PORT: int

    @property
    def DSN(self):
        return f"redis://{self.HOST}:{self.PORT}"


redis_settings = Settings()
