from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=True,
        env_prefix='GB_API__'
    )

    BASE_URL: str
    API_VERSION: str


gb_api_settings = Settings()
