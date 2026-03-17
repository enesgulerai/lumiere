import os
from pathlib import Path

# === 1. File Paths (Infrastructure & Project Root) ===
CONFIG_FILE_PATH = Path(__file__).resolve()
PROJECT_ROOT = CONFIG_FILE_PATH.parent.parent.parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# --- Google Drive IDs ---
# Replace these with your actual Google Drive file IDs
# --- Google Drive IDs ---
GDRIVE_IDS = {
    "ratings.dat": "1fQ3RemY7o5GHf-ZMxUmNT6jbb4iOR095",
    "movies.dat": "1TVTN1wRUlCfdwFDvqju9PJOJWuoK3M3L",
    "users.dat": "1eWBE00xOxcW1oQ7SNUb9RGUOFuGaYBgC"
}

# --- Raw Data Paths ---
RATINGS_DATA_PATH = RAW_DATA_DIR / "ratings.dat"
MOVIES_DATA_PATH = RAW_DATA_DIR / "movies.dat"
USERS_DATA_PATH = RAW_DATA_DIR / "users.dat"

# --- Model & Artifact Paths ---
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_OUTPUT_PATH = MODELS_DIR / "recsys_model.onnx"

# API processed data (Pickle removed, using CSV)
MOVIES_CLEAN_PATH = PROCESSED_DATA_DIR / "movies_cleaned.csv"

# === 2. Data Processing & Encoding Settings ===
DATA_SEPARATOR = "::"
DATA_ENGINE = "python"
MOVIES_ENCODING = "latin-1"

RATINGS_COLS = ["UserID", "MovieID", "Rating", "Timestamp"]
MOVIES_COLS = ["MovieID", "Title", "Genres"]
USERS_COLS = ["UserID", "Gender", "Age", "Occupation", "Zip-code"]

# === 3. ML Model Settings ===
TARGET_VARIABLE = "Rating"
RANDOM_STATE = 42
TOP_K_RECOMMENDATIONS = 10

# === 4. MLFlow Settings ===
MLFLOW_EXPERIMENT_NAME = "Lumiere_ONNX_V1"

# Ensure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)