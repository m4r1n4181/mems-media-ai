"""MLflow experiment tracking.

Runs are stored locally in ml/mlflow.db (metadata) and ml/mlartifacts/ (files). Both are git-ignored.
Browse them with:   mlflow ui --backend-store-uri sqlite:///mlflow.db   (from the ml/ folder)
"""
from __future__ import annotations

import contextlib
import re
from pathlib import Path

import mlflow

ML_DIR = Path(__file__).resolve().parents[2]
EXPERIMENT = "brand-creator-recommender"


def _setup():
    mlflow.set_tracking_uri(f"sqlite:///{(ML_DIR / 'mlflow.db').as_posix()}")
    if mlflow.get_experiment_by_name(EXPERIMENT) is None:
        mlflow.create_experiment(EXPERIMENT, artifact_location=(ML_DIR / "mlartifacts").as_uri())
    mlflow.set_experiment(EXPERIMENT)


def clean(name: str) -> str:
    """MLflow metric names cannot contain '@', '(' etc.: 'recall@50' -> 'recall_at_50'."""
    return re.sub(r"[^0-9A-Za-z_\-./ ]", "_", name.replace("@", "_at_")).strip("_")


@contextlib.contextmanager
def run(name: str, exp_id: str | None = None, params: dict | None = None):
    """Usage:  with tracking.run("ranker val", exp_id="R5", params={...}): ..."""
    _setup()
    with mlflow.start_run(run_name=name) as r:
        if exp_id:
            mlflow.set_tag("exp_id", exp_id)
        if params:
            mlflow.log_params({k: (v if len(str(v)) < 500 else str(v)[:497] + "...") for k, v in params.items()})
        yield r


def log_metrics(metrics: dict, prefix: str = ""):
    mlflow.log_metrics({clean(f"{prefix}{k}"): float(v) for k, v in metrics.items() if v == v})  # skip NaN


def log_summary(summary, by_bucket=None):
    """summary: models x metrics DataFrame; by_bucket: bucket x models DataFrame (recall@50)."""
    for model, row in summary.iterrows():
        log_metrics(row.to_dict(), prefix=f"{model}/")
    if by_bucket is not None:
        for model in by_bucket.columns:
            log_metrics(by_bucket[model].to_dict(), prefix=f"{model}/recall@50 brands ")
