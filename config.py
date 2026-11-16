from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]

class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chroma_path: str = str(BASE_DIR / "data" / "chroma")
    upload_dir: str = str(BASE_DIR / "data" / "uploads")
    max_upload_mb: int = 50
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

settings = Settings()
Path(settings.chroma_path).mkdir(parents=True, exist_ok=True)
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
