from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GITHUB_APP_ID: str
    GITHUB_INSTALLATION_ID: str
    GITHUB_PRIVATE_KEY: str
    GITHUB_REPO: str

    class Config:
        env_file = ".env"


settings = Settings()
