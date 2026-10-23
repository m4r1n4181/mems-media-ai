"""LightGBM learning-to-rank model over candidate features."""
from __future__ import annotations

import lightgbm as lgb
import numpy as np
import pandas as pd

from .evaluate import KS, history_bucket
from .features import FEATURES
from .metrics import ndcg_at_k, recall_at_k
from .split import Task


def sample_training_groups(df: pd.DataFrame, neg_per_brand: int = 100, seed: int = 0) -> pd.DataFrame:
    """Keep brands that have at least one positive (others teach a ranker nothing), all their positives,
    and a random sample of negatives — the full set would be large and mostly redundant."""
    has_pos = df.groupby("brand").label.transform("max") == 1
    df = df[has_pos]
    pos = df[df.label == 1]
    neg = (df[df.label == 0].sample(frac=1.0, random_state=seed)
           .groupby("brand").head(neg_per_brand))
    return pd.concat([pos, neg]).sort_values("brand").reset_index(drop=True)


def train(train_df: pd.DataFrame, seed: int = 0, features: list[str] = FEATURES) -> lgb.LGBMRanker:
    groups = train_df.groupby("brand", sort=False).size().values
    model = lgb.LGBMRanker(
        objective="lambdarank", n_estimators=400, learning_rate=0.05, num_leaves=31,
        min_child_samples=50, subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
        lambdarank_truncation_level=50, random_state=seed, verbose=-1,
    )
    model.fit(train_df[features], train_df.label, group=groups)
    return model


def evaluate_scored(df: pd.DataFrame, score_col: str, task: Task, creator_followers: pd.Series,
                    top: int = 100) -> pd.DataFrame:
    """Same metrics as evaluate.evaluate, but for scored candidate tables.
    Positives that never made it into the candidate set count as misses."""
    rel = task.positives.groupby("brand").creator_id.apply(set)
    ranked = (df.sort_values(["brand", score_col], ascending=[True, False])
              .groupby("brand").head(top).groupby("brand").creator_id.apply(list))
    rows = []
    for b, r in rel.items():
        lst = ranked.get(b, [])
        row = {"brand": b, "n_pos": len(r)}
        for k in KS:
            row[f"recall@{k}"] = recall_at_k(lst, r, k)
        row["ndcg@50"] = ndcg_at_k(lst, r, 50)
        row["top10_median_followers"] = float(np.median(creator_followers.reindex(lst[:10]).fillna(0))) if lst else 0.0
        rows.append(row)
    out = pd.DataFrame(rows)
    out["bucket"] = history_bucket(task, list(out.brand)).values
    return out
