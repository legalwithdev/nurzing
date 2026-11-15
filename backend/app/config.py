"""Runtime configuration (12-factor: everything from the environment)."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NURZING_", env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./nurzing.db"
    jwt_secret: str = "dev-only-change-me"
    jwt_algorithm: str = "HS256"
    jwt_ttl_minutes: int = 60 * 24 * 30
    otp_ttl_seconds: int = 300
    otp_debug: bool = True
    cors_origins: str = "http://localhost:5173,https://nurzing.pages.dev"
    admin_phones: str = "+919180000000"
    gold_min_years: int = 7

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def admin_list(self) -> list[str]:
        return [p.strip() for p in self.admin_phones.split(",") if p.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
