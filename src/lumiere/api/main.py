import sys
import joblib
import pandas as pd
import __main__
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from typing import Dict, Set, Any

# --- Pickle Compatibility Hack ---
# We must ensure LumiereSVD is available in the __main__ module 
# so joblib can unpickle the model correctly when running via uvicorn.
import lumiere.ml.model
__main__.LumiereSVD = lumiere.ml.model.LumiereSVD
from lumiere.ml.model import LumiereSVD
# ---------------------------------

from lumiere.api.schema import PredictionResponse, Movie
from lumiere.ml.config import (
    MODEL_OUTPUT_PATH,
    MOVIES_CLEAN_PATH,
    TOP_K_RECOMMENDATIONS,
    RATINGS_DATA_PATH,
    RATINGS_COLS
)
from lumiere.ml.data_processing import DATA_SEPARATOR, DATA_ENGINE

class ModelCache:
    model: Any = None
    movies_df: pd.DataFrame = None
    user_watch_list: Dict[int, Set[int]] = {}

cache = ModelCache()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing Lumiere API...")
    try:
        # Load the trained SVD model
        cache.model = joblib.load(MODEL_OUTPUT_PATH)
        
        # Load the cleaned movies metadata
        cache.movies_df = pd.read_pickle(MOVIES_CLEAN_PATH)
        if "MovieID" in cache.movies_df.columns:
            cache.movies_df.set_index("MovieID", inplace=True)
        
        # Load ratings to create a exclusion list (already watched movies)
        ratings_df = pd.read_csv(
            RATINGS_DATA_PATH,
            sep=DATA_SEPARATOR,
            header=None,
            names=RATINGS_COLS,
            engine=DATA_ENGINE
        )
        
        cache.user_watch_list = ratings_df.groupby('UserID')['MovieID'].apply(set).to_dict()
        
        app.state.cache = cache
        print("ML assets loaded successfully.")
    except Exception as e:
        print(f"Critical error during startup: {e}")
        print("Ensure 'python -m lumiere.ml.train' has been executed.")
        sys.exit(1)
        
    yield
    
    print("Shutting down Lumiere API... Cleaning up memory.")
    cache.model = None
    cache.movies_df = None
    cache.user_watch_list.clear()

app = FastAPI(
    title="Lumiere Recommendation API",
    description="Production-ready MLOps API for serving SVD-based movie recommendations.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/", tags=["Health"])
def health_check():
    """Root endpoint for infrastructure health checks."""
    if hasattr(app.state, "cache") and app.state.cache.model is not None:
        return {"status": "healthy", "message": "Lumiere API is operational."}
    return {"status": "unhealthy", "message": "ML assets are not loaded."}

@app.get("/recommend/{user_id}", response_model=PredictionResponse, tags=["Inference"])
def get_recommendations(user_id: int):
    """
    Core inference endpoint. 
    Returns Top-K movie recommendations for a given user, excluding previously watched movies.
    """
    current_cache = app.state.cache

    if user_id not in current_cache.user_watch_list:
        raise HTTPException(
            status_code=404,
            detail=f"User ID {user_id} not found in the historical data."
        )

    if current_cache.model is None:
        raise HTTPException(status_code=503, detail="Inference model is unavailable.")

    watched_movies = current_cache.user_watch_list.get(user_id, set())
    all_movie_ids = current_cache.movies_df.index.tolist()
    
    # Filter out movies the user has already seen
    movies_to_predict = [mid for mid in all_movie_ids if mid not in watched_movies]

    # Batch prediction using our custom LumiereSVD.predict_est method
    predictions = [
        (movie_id, current_cache.model.predict_est(user_id, movie_id))
        for movie_id in movies_to_predict
    ]

    # Sort by predicted rating (descending) and take top K
    predictions.sort(key=lambda x: x[1], reverse=True)
    top_k_preds = predictions[:TOP_K_RECOMMENDATIONS]
    
    recommended_movies = []
    for movie_id, _ in top_k_preds:
        try:
            row = current_cache.movies_df.loc[movie_id]
            recommended_movies.append(
                Movie(
                    MovieID=int(movie_id),
                    Title=str(row.Title),
                    Genres=str(row.Genres)
                )
            )
        except KeyError:
            continue

    return {
        "UserID": user_id,
        "Recommendations": recommended_movies
    }