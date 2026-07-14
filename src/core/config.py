from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "KeySentry API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Queue (Celery / Redis)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    @property
    def CELERY_BROKER_URL(self) -> str:
        return self.REDIS_URL
        
    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return self.REDIS_URL

    # Standalone GoTrue Integration
    GOTRUE_URL: str = "http://localhost:9999"
    GOTRUE_JWT_SECRET: str = ""

    # Encryption
    ENCRYPTION_KEY: str = "change_me_in_production"
    
    # Trigger.dev Config
    TRIGGER_API_KEY: str = ""
    INTERNAL_API_SECRET: str = "super_secret_webhook_key_123"

    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
