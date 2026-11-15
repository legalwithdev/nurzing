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

    # payments
    payment_provider: str = "dummy"          # dummy | razorpay
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""

    # sms
    sms_provider: str = "console"            # console | msg91
    msg91_authkey: str = ""
    msg91_sender: str = "NURZNG"
    msg91_template_id: str = ""

    # uploads
    upload_dir: str = "./uploads"
    max_upload_bytes: int = 5 * 1024 * 1024  # 5 MB
    allowed_upload_types: str = "image/jpeg,image/png,application/pdf"

    # rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_auth_per_minute: int = 10

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def allowed_types(self) -> list[str]:
        return [t.strip() for t in self.allowed_upload_types.split(",") if t.strip()]

    @property
    def admin_list(self) -> list[str]:
        return [p.strip() for p in self.admin_phones.split(",") if p.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
