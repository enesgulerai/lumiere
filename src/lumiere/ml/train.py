import os
import sys
import json
import datetime
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
import optuna

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import TargetEncoder
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import cross_val_score
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

from lumiere.ml.config import (
    MODEL_OUTPUT_PATH,
    RANDOM_STATE,
    MLFLOW_EXPERIMENT_NAME,
    TARGET_VARIABLE,
    MODELS_DIR
)
from lumiere.ml.data_processing import load_ratings_data, load_and_save_movies_data

DAGSHUB_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "https://dagshub.com/enesgulerai/lumiere.mlflow")

def save_mapping_to_json(mapping_dict, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(mapping_dict, f, ensure_ascii=False, indent=4)

def run_training():
    print("===== Starting Lumiere Advanced Training Process with Optuna =====")
    
    mlflow.set_tracking_uri(DAGSHUB_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_name = f"lumiere_optuna_onnx_{current_time}"

    ratings_df = load_ratings_data()
    
    print("Mapping UserIDs and MovieIDs to contiguous integers...")
    unique_users = ratings_df["UserID"].unique()
    unique_movies = ratings_df["MovieID"].unique()
    
    user_idx_map = {int(user_id): idx for idx, user_id in enumerate(unique_users)}
    movie_idx_map = {int(movie_id): idx for idx, movie_id in enumerate(unique_movies)}
    
    ratings_df["UserIdx"] = ratings_df["UserID"].map(user_idx_map)
    ratings_df["MovieIdx"] = ratings_df["MovieID"].map(movie_idx_map)
    
    X = ratings_df[["UserIdx", "MovieIdx"]].values.astype(np.float32)
    y = ratings_df[TARGET_VARIABLE].values.astype(np.float32)

    def objective(trial):
        max_iter = trial.suggest_int('max_iter', 100, 500)
        learning_rate = trial.suggest_float('learning_rate', 0.01, 0.3, log=True)
        max_depth = trial.suggest_categorical('max_depth', [5, 10, 15, None])
        l2_regularization = trial.suggest_float('l2_regularization', 0.0, 10.0)
        
        pipeline = Pipeline([
            ('encoder', TargetEncoder(target_type='continuous', random_state=RANDOM_STATE)),
            ('regressor', HistGradientBoostingRegressor(
                max_iter=max_iter,
                learning_rate=learning_rate,
                max_depth=max_depth,
                l2_regularization=l2_regularization,
                random_state=RANDOM_STATE
            ))
        ])
        
        scores = cross_val_score(pipeline, X, y, cv=3, scoring='r2', n_jobs=-1)
        return scores.mean()

    with mlflow.start_run(run_name=run_name):
        print("Starting Optuna Hyperparameter Optimization...")
        study = optuna.create_study(direction='maximize')
        
        study.optimize(objective, n_trials=50)
        
        print(f"Best R2 Score (CV): {study.best_value:.4f}")
        print(f"Best Parameters: {study.best_params}")
        
        mlflow.log_params(study.best_params)
        mlflow.log_metric("cv_best_r2_score", study.best_value)

        print("Training final model with best parameters on full dataset...")
        best_pipeline = Pipeline([
            ('encoder', TargetEncoder(target_type='continuous', random_state=RANDOM_STATE)),
            ('regressor', HistGradientBoostingRegressor(
                **study.best_params,
                random_state=RANDOM_STATE
            ))
        ])
        best_pipeline.fit(X, y)

        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        
        print("Exporting best model pipeline to ONNX format...")
        initial_type = [('float_input', FloatTensorType([None, 2]))]
        onnx_model = convert_sklearn(best_pipeline, initial_types=initial_type)
        
        with open(MODEL_OUTPUT_PATH, "wb") as f:
            f.write(onnx_model.SerializeToString())
            
        print(f"ONNX Model saved to: {MODEL_OUTPUT_PATH}")
        
        user_map_path = MODELS_DIR / "user_idx_map.json"
        movie_map_path = MODELS_DIR / "movie_idx_map.json"
        save_mapping_to_json(user_idx_map, user_map_path)
        save_mapping_to_json(movie_idx_map, movie_map_path)
        print("Mapping dictionaries saved as JSON.")

        mlflow.log_artifact(str(MODEL_OUTPUT_PATH), artifact_path="onnx_models")
        
        print("Preparing clean movie metadata...")
        load_and_save_movies_data() 

        print("===== Training Process Completed =====")

if __name__ == "__main__":
    run_training()