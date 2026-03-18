import time
import json
import numpy as np
from fastapi import HTTPException

from lumiere.api.schemas.recommendation import Movie, PredictionResponse
from lumiere.api.core.model import model_manager
from lumiere.api.core.redis import redis_client
from lumiere.api.core.config import api_settings

async def get_recommendations_for_user(user_id: int) -> PredictionResponse:
    start_time = time.perf_counter()
    cache_key = f"lumiere:recs:{user_id}"

    # 1. Try to fetch from Redis Cache
    if redis_client.pool:
        try:
            cached_data = await redis_client.pool.get(cache_key)
            if cached_data:
                latency = (time.perf_counter() - start_time) * 1000
                recs_dict = json.loads(cached_data)
                
                # Reconstruct Movie objects
                recs = [Movie(**item) for item in recs_dict]
                
                return PredictionResponse(
                    user_id=user_id,
                    recommendations=recs,
                    source="Redis Cache",
                    latency_ms=round(latency, 2)
                )
        except Exception as e:
            print(f"Redis Cache Read Error: {e}")

    # 2. Validation & Mapping
    str_user_id = str(user_id)
    if str_user_id not in model_manager.user_map:
        raise HTTPException(
            status_code=404, 
            detail=f"User ID {user_id} not found in historical data."
        )

    user_idx = model_manager.user_map[str_user_id]
    watched_movies = model_manager.user_watch_list.get(user_id, set())

    # 3. Prepare Batch Inference Data
    candidate_movie_ids = []
    features = []
    
    for str_movie_id, movie_idx in model_manager.movie_map.items():
        movie_id = int(str_movie_id)
        if movie_id not in watched_movies:
            candidate_movie_ids.append(movie_id)
            # TargetEncoder expects shape (n_samples, 2) -> [UserIdx, MovieIdx]
            features.append([user_idx, movie_idx])

    if not features:
        raise HTTPException(status_code=404, detail="No new movies to recommend.")

    # 4. Execute ONNX Inference
    input_name = model_manager.session.get_inputs()[0].name
    X_tensor = np.array(features, dtype=np.float32)
    predictions = model_manager.session.run(None, {input_name: X_tensor})[0]

    # 5. Sort and Extract Top-K
    # predictions is a 1D array, we get the indices of the highest values
    top_indices = np.argsort(predictions.flatten())[::-1][:api_settings.TOP_K_RECOMMENDATIONS]
    
    recommended_movies = []
    for idx in top_indices:
        m_id = candidate_movie_ids[idx]
        if m_id in model_manager.movies_df.index:
            row = model_manager.movies_df.loc[m_id]
            recommended_movies.append(
                Movie(
                    MovieID=m_id,
                    Title=str(row["Title"]),
                    Genres=str(row["Genres"])
                )
            )

    # 6. Save results to Redis Cache
    if redis_client.pool:
        try:
            # Pydantic V2 model_dump with alias=True ensures keys like 'MovieID' are preserved
            cache_payload = [m.model_dump(by_alias=True) for m in recommended_movies]
            await redis_client.pool.setex(
                cache_key,
                api_settings.CACHE_TTL,
                json.dumps(cache_payload)
            )
        except Exception as e:
            print(f"Redis Cache Write Error: {e}")

    latency = (time.perf_counter() - start_time) * 1000

    return PredictionResponse(
        user_id=user_id,
        recommendations=recommended_movies,
        source="ONNX Model",
        latency_ms=round(latency, 2)
    )