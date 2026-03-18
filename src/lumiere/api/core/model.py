import json
import onnxruntime as ort
import pandas as pd
from typing import Dict, Set
from lumiere.api.core.config import api_settings
from lumiere.ml.config import RATINGS_DATA_PATH, DATA_SEPARATOR, RATINGS_COLS

class ModelManager:
    def __init__(self):
        self.session: ort.InferenceSession = None
        self.user_map: Dict[str, int] = {}
        self.movie_map: Dict[str, int] = {}
        self.movies_df: pd.DataFrame = None
        self.user_watch_list: Dict[int, Set[int]] = {}

    def load_artifacts(self):
        print(f"Loading ONNX model from {api_settings.MODEL_PATH}")
        self.session = ort.InferenceSession(str(api_settings.MODEL_PATH))
        
        with open(api_settings.USER_MAP_PATH, "r", encoding="utf-8") as f:
            self.user_map = json.load(f)
            
        with open(api_settings.MOVIE_MAP_PATH, "r", encoding="utf-8") as f:
            self.movie_map = json.load(f)
            
        print("Loading cleaned movies metadata...")
        self.movies_df = pd.read_csv(api_settings.MOVIES_CLEAN_PATH)
        if "MovieID" in self.movies_df.columns:
            self.movies_df.set_index("MovieID", inplace=True)
            
        print("Loading user watch history for filtering...")
        ratings_df = pd.read_csv(
            RATINGS_DATA_PATH,
            sep=DATA_SEPARATOR,
            header=None,
            names=RATINGS_COLS,
            engine="python"
        )
        self.user_watch_list = ratings_df.groupby("UserID")["MovieID"].apply(set).to_dict()
        print("All machine learning artifacts loaded successfully.")

model_manager = ModelManager()