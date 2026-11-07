from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Resume Job Matcher"
    app_env: str = "development"
    debug: bool = True

    max_file_size_mb: int = 10
    max_job_description_chars: int = 50_000
    min_job_description_chars: int = 50
    min_resume_text_chars: int = 80
    chunk_size: int = 500
    chunk_overlap: int = 100

    raw_data_dir: str = "data/raw"
    processed_data_dir: str = "data/processed"
    chroma_persist_dir: str = "data/chroma_db"

    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    top_k_results: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
