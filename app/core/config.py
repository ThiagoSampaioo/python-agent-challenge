from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    kb_url: str
    llm_provider: str = "openai"
    llm_model: str
    llm_api_key: str
    llm_base_url: str

    memory_store: str | None = None
    session_ttl_seconds: int = 1800
    session_max_messages: int = 4

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()