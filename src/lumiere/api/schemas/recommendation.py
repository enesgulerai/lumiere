from pydantic import BaseModel, Field, ConfigDict
from typing import List

class Movie(BaseModel):
    """
    A Pydantic V2 model representing a single movie recommendation.
    """
    movie_id: int = Field(..., alias="MovieID", description="Unique identifier for the movie.")
    title: str = Field(..., alias="Title", description="The title of the movie including release year.")
    genres: str = Field(..., alias="Genres", description="Pipe-separated list of genres.")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "MovieID": 1196,
                "Title": "Star Wars: Episode V - The Empire Strikes Back (1980)",
                "Genres": "Action|Adventure|Drama|Sci-Fi|War"
            }
        }
    )


class PredictionResponse(BaseModel):
    """
    The output model for the /recommend endpoint.
    Includes performance metrics if requested.
    """
    user_id: int = Field(..., alias="UserID", description="The ID of the user requesting recommendations.")
    recommendations: List[Movie] = Field(..., alias="Recommendations", description="Top-K recommended movies for the user.")
    source: str = Field(default="Model", description="Indicates if the result came from 'Cache' or 'Model'.")
    latency_ms: float = Field(default=0.0, description="Time taken to generate or fetch the response in milliseconds.")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "UserID": 12,
                "Recommendations": [
                    {
                        "MovieID": 1196,
                        "Title": "Star Wars: Episode V - The Empire Strikes Back (1980)",
                        "Genres": "Action|Adventure|Drama|Sci-Fi|War"
                    }
                ],
                "source": "Cache",
                "latency_ms": 12.5
            }
        }
    )