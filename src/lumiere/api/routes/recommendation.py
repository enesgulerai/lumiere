from fastapi import APIRouter
from lumiere.api.schemas.recommendation import PredictionResponse
from lumiere.api.services.recommendation import get_recommendations_for_user

router = APIRouter(prefix="/recommend", tags=["Inference"])

@router.get("/{user_id}", response_model=PredictionResponse)
async def recommend_movies(user_id: int):
    """
    Returns Top-K movie recommendations for a given user.
    Utilizes Redis caching for sub-millisecond latency.
    """
    return await get_recommendations_for_user(user_id)