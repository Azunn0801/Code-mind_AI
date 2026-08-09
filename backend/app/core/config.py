from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CodeMind API"
    app_env: str = "local"
    api_prefix: str = "/v1"
    database_url: str = ""
    auth_mode: str = "demo"
    demo_token_secret: str = "local-demo-secret-change-before-production"
    demo_token_ttl_seconds: int = Field(default=3600, ge=60, le=86_400)
    cors_origins: str = "http://localhost:5173"
    code_runner_mode: str = "simulated"
    ai_mode: str = "canned"
    ai_max_interactions_per_session: int = 3
    repository_mode: str = "file"
    state_file_path: str = ".data/codemind_state.json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
