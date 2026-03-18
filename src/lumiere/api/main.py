import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI

from lumiere.api.core.config import api_settings
from lumiere.api.core.model import model_manager
from lumiere.api.core.redis import redis_client
from lumiere.api.routes import recommendation
from lumiere.api.core.logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API...", extra={"project": api_settings.PROJECT_NAME})
    try:
        model_manager.load_artifacts()
        logger.info("Machine learning artifacts loaded successfully.")
    except Exception as e:
        logger.error("Failed to load ML artifacts", exc_info=True)
        sys.exit(1)
        
    try:
        await redis_client.connect()
        logger.info("Connected to Redis cache.")
    except Exception as e:
        logger.error("Failed to connect to Redis", exc_info=True)
        sys.exit(1)
        
    yield
    
    await redis_client.disconnect()
    logger.info("API shutdown complete.")

app = FastAPI(
    title=api_settings.PROJECT_NAME,
    version=api_settings.VERSION,
    description="Production-ready MLOps API with ONNX and Redis.",
    lifespan=lifespan
)

app.include_router(recommendation.router)

@app.get("/health", tags=["Health"])
async def health_check():
    """Infrastructure health check endpoint."""
    redis_status = "connected" if redis_client.pool else "disconnected"
    model_status = "loaded" if model_manager.session else "unloaded"
    
    is_healthy = redis_client.pool is not None and model_manager.session is not None
    
    if not is_healthy:
        logger.warning(
            "Health check degraded", 
            extra={"redis": redis_status, "model": model_status}
        )
        
    return {
        "status": "healthy" if is_healthy else "degraded",
        "redis": redis_status,
        "model": model_status,
        "version": api_settings.VERSION
    }