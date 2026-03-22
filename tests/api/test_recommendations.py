def test_recommendation_invalid_type(client):
    """
    Test if the API correctly rejects non-integer user IDs.
    FastAPI should block this at the router level and return 422 Unprocessable Entity.
    """
    response = client.get("/recommend/invalid_string_id")
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert data["detail"][0]["type"] == "int_parsing"

def test_recommendation_missing_parameter(client):
    """
    Test if the API handles missing path parameters correctly.
    """
    response = client.get("/recommend/")
    
    # Missing path parameter should result in a 404 Not Found
    assert response.status_code == 404