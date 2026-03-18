from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class APISettings(BaseSettings):
    PROJECT_NAME: str = "Lumiere Recommendation API"
    VERSION: str = "2.0.0"
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent.parent
    MODEL_PATH: Path = BASE_DIR / "models" / "recsys_model.onnx"
    USER_MAP_PATH: Path = BASE_DIR / "models" / "user_idx_map.json"
    MOVIE_MAP_PATH: Path = BASE_DIR / "models" / "movie_idx_map.json"
    MOVIES_CLEAN_PATH: Path = BASE_DIR / "data" / "processed" / "movies_cleaned.csv"
    
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600
    
    TOP_K_RECOMMENDATIONS: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

api_settings = APISettings()