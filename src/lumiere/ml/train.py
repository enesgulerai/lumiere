import sys
import datetime
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
from joblib import dump
from sklearn.decomposition import TruncatedSVD
from lumiere.ml.model import LumiereSVD

from lumiere.ml.config import (
    MODEL_OUTPUT_PATH,
    RANDOM_STATE,
    MLFLOW_EXPERIMENT_NAME,
    TARGET_VARIABLE
)
from lumiere.ml.data_processing import load_ratings_data, load_and_save_movies_data

class LumiereSVD:
    def __init__(self, n_components=50, random_state=42):
        self.n_components = n_components
        self.random_state = random_state
        self.model = TruncatedSVD(n_components=self.n_components, random_state=self.random_state)
        
        self.user_means = None
        self.user_idx_map = {}
        self.movie_idx_map = {}
        self.user_features = None
        self.item_features = None

    def fit(self, ratings_df):
        print("Creating User-Item matrix...")
        pivot_df = ratings_df.pivot(index="UserID", columns="MovieID", values=TARGET_VARIABLE)
        
        self.user_idx_map = {user_id: idx for idx, user_id in enumerate(pivot_df.index)}
        self.movie_idx_map = {movie_id: idx for idx, movie_id in enumerate(pivot_df.columns)}
        
        R = pivot_df.values
        self.user_means = np.nanmean(R, axis=1)
        
        R_demeaned = R - self.user_means.reshape(-1, 1)
        R_demeaned = np.nan_to_num(R_demeaned, nan=0.0)
        
        print(f"Training TruncatedSVD with {self.n_components} components...")
        self.user_features = self.model.fit_transform(R_demeaned)
        self.item_features = self.model.components_
        print("Training complete.")

    def predict_est(self, uid, iid):
        if uid not in self.user_idx_map or iid not in self.movie_idx_map:
            return 3.0
            
        u_idx = self.user_idx_map[uid]
        i_idx = self.movie_idx_map[iid]
        
        prediction = self.user_means[u_idx] + np.dot(self.user_features[u_idx, :], self.item_features[:, i_idx])
        return np.clip(prediction, 1.0, 5.0)


def run_training():
    print("===== Starting Lumiere Training Process =====")

    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_name = f"lumiere_svd_{current_time}"

    with mlflow.start_run(run_name=run_name):
        n_components = 50
        mlflow.log_param("random_state", RANDOM_STATE)
        mlflow.log_param("n_components", n_components)

        ratings_df = load_ratings_data()

        algo = LumiereSVD(n_components=n_components, random_state=RANDOM_STATE)
        algo.fit(ratings_df)

        mlflow.log_metric("explained_variance_ratio", algo.model.explained_variance_ratio_.sum())

        MODEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        dump(algo, MODEL_OUTPUT_PATH)
        print(f"Trained model saved to: {MODEL_OUTPUT_PATH}")

        mlflow.sklearn.log_model(
            sk_model=algo.model,
            artifact_path="lumiere_svd_model"
        )

        print("Preparing clean movie data for the API...")
        load_and_save_movies_data()

        print("===== Training Process Completed =====")

if __name__ == "__main__":
    run_training()