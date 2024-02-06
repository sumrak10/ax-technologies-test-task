from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=True,
        env_prefix='API_KEY__'
    )

    LENGTH: int


api_key_settings = Settings()
