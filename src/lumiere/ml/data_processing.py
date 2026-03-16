# src/data_processing.py

import pandas as pd
import sys
from pathlib import Path

# Import from our 'config.py' (the control panel)
from lumiere.ml.config import (
    RATINGS_DATA_PATH,
    MOVIES_DATA_PATH,
    MOVIES_CLEAN_PATH,  # For the API "polish"
    DATA_SEPARATOR,
    DATA_ENGINE,
    MOVIES_ENCODING,
    RATINGS_COLS,
    MOVIES_COLS
)


def load_ratings_data() -> pd.DataFrame:
    """
    v1.0 - Loads the raw 'ratings.dat' file.

    This function reads the "kaos" file based on the rules
    in 'config.py' (separator, columns) and returns
    a clean DataFrame for the 'train.py' script.

    :return: A pandas DataFrame with ratings (UserID, MovieID, Rating).
    """
    print(f"Loading ratings data from: {RATINGS_DATA_PATH}")
    try:
        ratings_df = pd.read_csv(
            RATINGS_DATA_PATH,
            sep=DATA_SEPARATOR,
            header=None,
            names=RATINGS_COLS,
            engine=DATA_ENGINE
        )
        # We only need these 3 columns for the 'surprise' library
        ratings_df = ratings_df[["UserID", "MovieID", "Rating"]]
        print("Ratings data loaded successfully.")
        return ratings_df

    except FileNotFoundError:
        print(f"ERROR: Raw ratings file not found: {RATINGS_DATA_PATH}")
        print("Please ensure 'ratings.dat' is in the 'data/raw/' folder.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading ratings data: {e}")
        sys.exit(1)


def load_and_save_movies_data() -> pd.DataFrame:
    """
    v3.0 (API "Polish") - Loads the raw 'movies.dat' file.

    This function loads the "kaos" movie data, cleans it,
    and saves a clean '.pkl' version to 'data/processed/'.
    The v3.0 API ('app/main.py') will use this clean file
    to map MovieIDs to Titles, rather than re-reading the
    "kaos" .dat file every time.

    :return: A pandas DataFrame with movie info (MovieID, Title, Genres).
    """
    print(f"Loading movies data from: {MOVIES_DATA_PATH}")
    try:
        movies_df = pd.read_csv(
            MOVIES_DATA_PATH,
            sep=DATA_SEPARATOR,
            header=None,
            names=MOVIES_COLS,
            engine=DATA_ENGINE,
            encoding=MOVIES_ENCODING  # Discovered in the notebook
        )

        # Save the clean version for the API to use
        # Ensure the 'data/processed/' directory exists
        MOVIES_CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
        movies_df.to_pickle(MOVIES_CLEAN_PATH)

        print(f"Movies data loaded and clean version saved to: {MOVIES_CLEAN_PATH}")
        return movies_df

    except FileNotFoundError:
        print(f"ERROR: Raw movies file not found: {MOVIES_DATA_PATH}")
        print("Please ensure 'movies.dat' is in the 'data/raw/' folder.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading movies data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # This allows testing the script directly
    # `python src/data_processing.py`

    print("--- Testing Data Processing (v1.0 - Ratings) ---")
    ratings = load_ratings_data()
    print(ratings.head())

    print("\n--- Testing Data Processing (v3.0 - Movies) ---")
    movies = load_and_save_movies_data()
    print(movies.head())