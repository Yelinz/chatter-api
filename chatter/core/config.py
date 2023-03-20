import secrets

from pydantic import AnyHttpUrl, BaseSettings, HttpUrl, PostgresDsn, validator

TORTOISE_ORM = {
    "connections": {"default": "asyncpg://user:password@db:5432/db"},
    "apps": {
        "models": {
            "models": ["chatter.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str = "localhost"
    SERVER_HOST: AnyHttpUrl = "http://localhost"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "Chatter"

    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "db"

    OPENAI_API_KEY: str = "TODO"
    AZURE_API_KEY: str = "TODO"

    TORTOISE_ORM = TORTOISE_ORM

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
