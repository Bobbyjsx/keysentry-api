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

    # Supabase Auth Integration
    SUPABASE_URL: str = "http://home-server:1024"
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
