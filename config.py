from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    chunk_size: int = 700
    chunk_overlap: int = 100

    source_dir: str = "sources/"
    chroma_path: str = "vector_store/"
    registry_path: str = "source_registry.json"

    ollama_base_url: str = "http://localhost:11434"
    embed_model: str = "nomic-embed-text"
    llm_model: str = "llama3.2:3b"
    retrieval_k: int = 3


settings = Settings()
