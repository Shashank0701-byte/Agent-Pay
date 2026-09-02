from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AgentPay"
    environment: str = "development"
    database_url: str = "sqlite:///./agentpay.db"
    secret_key: str = "change-this-secret-key"
    razorpay_key_id: str = "rzp_test_key"
    razorpay_key_secret: str = "change-me"
    webhook_secret: str = "change-me"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
