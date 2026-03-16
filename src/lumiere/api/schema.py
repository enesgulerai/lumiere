# app/schema.py

from pydantic import BaseModel, Field
from typing import List

# This is the "polish" for our v3.0 API.
# Instead of returning just an ID (e.g., 1196),
# we return a full Movie object.
class Movie(BaseModel):
    """A Pydantic model representing a movie."""
    MovieID: int
    Title: str
    Genres: str

class PredictionResponse(BaseModel):
    """
    The output model for our /recommend endpoint.
    It returns the UserID and a *list* of recommended Movie objects.
    """
    UserID: int
    Recommendations: List[Movie] = Field(..., description="Top-K recommended movies")