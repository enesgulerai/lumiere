import sys
import gdown
import pandas as pd
from pathlib import Path

from lumiere.ml.config import (
    RATINGS_DATA_PATH,
    MOVIES_DATA_PATH,
    MOVIES_CLEAN_PATH,
    DATA_SEPARATOR,
    DATA_ENGINE,
    MOVIES_ENCODING,
    RATINGS_COLS,
    MOVIES_COLS,
    GDRIVE_IDS
)

def download_if_missing(file_path: Path, file_key: str):
    """Downloads the file from Google Drive if it does not exist locally."""
    if not file_path.exists():
        print(f"Data missing: {file_path.name}. Downloading from Google Drive...")
        file_id = GDRIVE_IDS.get(file_key)
        
        if not file_id or file_id.startswith("YOUR_"):
            print(f"WARNING: Missing or default Google Drive ID for {file_key} in config.py")
            print("Cannot download data automatically. Please provide valid IDs or place files manually.")
            sys.exit(1)
            
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, str(file_path), quiet=False)
        print(f"Download complete: {file_path.name}")
    else:
        print(f"Found existing data: {file_path.name}")


def load_ratings_data() -> pd.DataFrame:
    """Loads the raw 'ratings.dat' file, downloading it if necessary."""
    download_if_missing(RATINGS_DATA_PATH, "ratings.dat")
    print(f"Loading ratings data from: {RATINGS_DATA_PATH}")
    
    try:
        ratings_df = pd.read_csv(
            RATINGS_DATA_PATH,
            sep=DATA_SEPARATOR,
            header=None,
            names=RATINGS_COLS,
            engine=DATA_ENGINE
        )
        ratings_df = ratings_df[["UserID", "MovieID", "Rating"]]
        print("Ratings data loaded successfully.")
        return ratings_df

    except Exception as e:
        print(f"Error loading ratings data: {e}")
        sys.exit(1)


def load_and_save_movies_data() -> pd.DataFrame:
    """Loads 'movies.dat', cleans it, and saves it as CSV for the API."""
    download_if_missing(MOVIES_DATA_PATH, "movies.dat")
    print(f"Loading movies data from: {MOVIES_DATA_PATH}")
    
    try:
        movies_df = pd.read_csv(
            MOVIES_DATA_PATH,
            sep=DATA_SEPARATOR,
            header=None,
            names=MOVIES_COLS,
            engine=DATA_ENGINE,
            encoding=MOVIES_ENCODING
        )

        MOVIES_CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Switched from pickle to CSV
        movies_df.to_csv(MOVIES_CLEAN_PATH, index=False)
        print(f"Movies data loaded and clean CSV version saved to: {MOVIES_CLEAN_PATH}")
        return movies_df

    except Exception as e:
        print(f"Error loading movies data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("--- Testing Data Processing (Ratings) ---")
    ratings = load_ratings_data()
    print(ratings.head())

    print("\n--- Testing Data Processing (Movies) ---")
    movies = load_and_save_movies_data()
    print(movies.head())