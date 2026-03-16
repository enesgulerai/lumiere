from pathlib import Path

# === 1. File Paths (Infrastructure & Project Root) ===
# Dosyanın konumu: src/lumiere/ml/config.py
# 4 seviye yukarı çıkarsak (ml -> lumiere -> src -> ROOT) gerçek proje köküne ulaşırız.
CONFIG_FILE_PATH = Path(__file__).resolve()
PROJECT_ROOT = CONFIG_FILE_PATH.parent.parent.parent.parent

# --- Raw Data Paths ---
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

RATINGS_DATA_PATH = RAW_DATA_DIR / "ratings.dat"
MOVIES_DATA_PATH = RAW_DATA_DIR / "movies.dat"

# --- Model & Artifact Paths ---
# Modelleri ana dizindeki 'models' klasöründe tutuyoruz
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_OUTPUT_PATH = MODELS_DIR / "recsys_svd_model.pkl"

# API için işlenmiş film verisi
MOVIES_CLEAN_PATH = MODELS_DIR / "movies_cleaned.pkl"

# === 2. Data Processing & Encoding Settings ===
DATA_SEPARATOR = "::"
DATA_ENGINE = "python"
MOVIES_ENCODING = "latin-1"

RATINGS_COLS = ["UserID", "MovieID", "Rating", "Timestamp"]
MOVIES_COLS = ["MovieID", "Title", "Genres"]

# === 3. ML Model Settings (Lumiere SVD) ===
TARGET_VARIABLE = "Rating"
RANDOM_STATE = 42
TOP_K_RECOMMENDATIONS = 10

# Hyperparameters (TruncatedSVD için)
N_COMPONENTS = 50 

# === 4. MLFlow Settings ===
MLFLOW_EXPERIMENT_NAME = "Lumiere_Movie_RecSys_V3"

# Dizinlerin varlığından emin olalım (Yoksa oluşturur)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)