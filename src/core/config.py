from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "EngineTriagingSupport"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    LLM_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_API_KEY: str
    LLM_MODEL: str = "google/gemini-flash-1.5"
    LLM_TIMEOUT_SECONDS: int = 40

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CACHE_INDEX_PATH: str = "data/cache/faiss.index"
    CACHE_STORE_PATH: str = "data/cache/store.json"

    SIMILARITY_THRESHOLD: float = 0.85
    MAX_LLM_RETRIES: int = 2
    ENABLE_LLM_COMPRESSION: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()
