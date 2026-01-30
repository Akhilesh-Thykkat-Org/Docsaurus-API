from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GITHUB_APP_ID: str
    GITHUB_INSTALLATION_ID: str
    GITHUB_PRIVATE_KEY: str
    GITHUB_REPO: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"   # ✅ ignore unknown keys
    )


settings = Settings()
