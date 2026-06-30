import os
import json
import joblib
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

DATA_PATH = "data/processed/merged_jobs.csv"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "energy_model.joblib")
FEATURES_PATH = os.path.join(MODEL_DIR, "feature_config.json")


def load_and_clean():
    df = pd.read_csv(DATA_PATH)

    # Basic cleaning
    df = df[df["job_duration_sec"] > 0]
    df = df[df["energyconsumed_joules"] > 0]
    df = df[df["nodes_alloc"] > 0]

    # Drop rows with missing values in columns we use
    required_cols = [
        "cpus_req",
        "mem_req",
        "nodes_alloc",
        "priority",
        "timelimit",
        "job_duration_sec",
        "avgmemoryutilization_pct",
        "avgsmutilization_pct",
        "energyconsumed_joules",
    ]
    df = df.dropna(subset=required_cols)

    return df


def feature_engineering(df):
    df = df.copy()

    # Core features
    df["log_job_duration"] = np.log1p(df["job_duration_sec"])
    df["log_timelimit"] = np.log1p(df["timelimit"])
    df["log_mem_req"] = np.log1p(df["mem_req"])

    # Interaction features
    df["cpu_node_ratio"] = df["cpus_req"] / (df["nodes_alloc"] + 1)
    df["duration_utilization"] = df["job_duration_sec"] * df["avgsmutilization_pct"]
    df["mem_cpu_ratio"] = df["mem_req"] / (df["cpus_req"] + 1)

    # Composite usage
    df["gpu_activity"] = df["avgmemoryutilization_pct"] * df["avgsmutilization_pct"]

    return df


def make_xy(df):
    feature_cols = [
        "cpus_req",
        "mem_req",
        "nodes_alloc",
        "priority",
        "timelimit",
        "job_duration_sec",
        "avgmemoryutilization_pct",
        "avgsmutilization_pct",
        "log_job_duration",
        "log_timelimit",
        "log_mem_req",
        "cpu_node_ratio",
        "duration_utilization",
        "mem_cpu_ratio",
        "gpu_activity",
    ]

    X = df[feature_cols].copy()
    y = np.log1p(df["energyconsumed_joules"].copy())

    return X, y, feature_cols


def inverse_log_target(y):
    return np.expm1(y)


def evaluate_original_scale(y_true_log, y_pred_log):
    y_true = inverse_log_target(y_true_log)
    y_pred = inverse_log_target(y_pred_log)

    # Predictions should never be negative after inverse transform
    y_pred = np.maximum(y_pred, 0)

    mae = mean_absolute_error(y_true, y_pred)
    rmse = mean_squared_error(y_true, y_pred) ** 0.5
    r2 = r2_score(y_true, y_pred)

    return mae, rmse, r2


def main():
    os.makedirs(MODEL_DIR, exist_ok=True)
    mlflow.set_experiment("verge-energy-model")

    df = load_and_clean()
    df = feature_engineering(df)
    X, y, feature_cols = make_xy(df)

    # 60% train, 20% val, 20% test
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.4, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42
    )

    model = XGBRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        max_depth=5,
        min_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        gamma=0.1,
        reg_alpha=0.0,
        reg_lambda=1.0,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1,
    )

    with mlflow.start_run():
        mlflow.log_param("model", "XGBRegressor")
        mlflow.log_param("n_estimators", 1000)
        mlflow.log_param("learning_rate", 0.05)
        mlflow.log_param("max_depth", 5)
        mlflow.log_param("min_child_weight", 3)
        mlflow.log_param("subsample", 0.8)
        mlflow.log_param("colsample_bytree", 0.8)
        mlflow.log_param("gamma", 0.1)
        mlflow.log_param("reg_alpha", 0.0)
        mlflow.log_param("reg_lambda", 1.0)
        mlflow.log_param("features", feature_cols)

        model = XGBRegressor(
            n_estimators=1000,
            learning_rate=0.05,
            max_depth=5,
            min_child_weight=3,
            subsample=0.8,
            colsample_bytree=0.8,
            gamma=0.1,
            reg_alpha=0.0,
            reg_lambda=1.0,
            objective="reg:squarederror",
            random_state=42,
            n_jobs=-1,
            early_stopping_rounds=30   # ✅ move here
        )

        model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )

        # Evaluate on test set only
        preds_log = model.predict(X_test)
        mae, rmse, r2 = evaluate_original_scale(y_test, preds_log)

        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)

        # Save model and feature config
        joblib.dump(model, MODEL_PATH)
        with open(FEATURES_PATH, "w") as f:
            json.dump(feature_cols, f, indent=2)

        mlflow.sklearn.log_model(model, artifact_path="model")

        print("\nModel saved to:", MODEL_PATH)
        print("Feature config saved to:", FEATURES_PATH)
        print(f"MAE:  {mae:.4f}")
        print(f"RMSE: {rmse:.4f}")
        print(f"R2:   {r2:.4f}")


if __name__ == "__main__":
    main()
