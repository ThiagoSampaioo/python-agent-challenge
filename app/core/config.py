from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # URL da base de conhecimento usada pela aplicação
    kb_url: str

    # Provedor e modelo do LLM configurados por ambiente
    llm_provider: str = "openai"
    llm_model: str
    llm_api_key: str
    llm_base_url: str

    # Configurações opcionais de memória/sessão
    memory_store: str | None = None
    session_ttl_seconds: int = 1800
    session_max_messages: int = 4

    # Configuração padrão do servidor
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Carrega as variáveis do arquivo .env
    # e ignora campos extras que não existirem na classe
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Instância única das configurações da aplicação
settings = Settings()