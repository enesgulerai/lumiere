def test_health_check(client):
    response = client.get("/health")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "redis" in data
    assert "model" in data
    assert "version" in data
    
    assert data["status"] in ["healthy", "degraded"]