import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from lumiere.api.core.redis import redis_client
from lumiere.api.core.model import model_manager
from lumiere.api.main import app

@pytest.fixture(autouse=True)
def mock_infrastructure():
    """
    By isolating external dependencies (Redis, ONNX), it enables us to write fast and reliable unit tests.
    """
    # 1. Mimic Redis
    redis_client.pool = MagicMock()
    redis_client.connect = AsyncMock()
    redis_client.disconnect = AsyncMock()
    
    # 2. Mimic the ML Model
    model_manager.session = MagicMock()
    model_manager.load_artifacts = MagicMock()
    
    yield
    
    # Clean up the area after the tests are finished.
    redis_client.pool = None
    model_manager.session = None

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client