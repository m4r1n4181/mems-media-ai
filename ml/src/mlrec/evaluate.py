from __future__ import annotations

import numpy as np
import pandas as pd

from .baselines import Index
from .metrics import ndcg_at_k, recall_at_k
from .split import Task

KS = (10, 50, 100)


def history_bucket(task: Task, brands: list[str]) -> pd.Series:
    n = task.history.groupby("brand").creator_id.nunique().reindex(brands, fill_value=0)
    return pd.cut(n, [-1, 0, 9, 99, np.inf], labels=["cold (0)", "1-9", "10-99", "100+"])


def evaluate(task: Task, idx: Index, model, creator_followers: pd.Series, top=100, batch=400) -> pd.DataFrame:
    rel = task.positives.groupby("brand").creator_id.apply(set)
    rows = []
    for start in range(0, len(idx.eval_brands), batch):
        names = idx.eval_brands[start:start + batch]
        scores = model.score(idx.b_pos[names].values)
        rows += _rank_batch(task, idx, names, scores, rel, creator_followers, top)
    out = pd.DataFrame(rows)
    out["bucket"] = history_bucket(task, idx.eval_brands).values
    return out


def _rank_batch(task, idx, names, scores, rel, creator_followers, top):
    rows = []
    for i, b in enumerate(names):
        s = scores[i]
        for c in task.known_pairs_by_brand.get(b, ()):
            s[idx.c_pos[c]] = -np.inf
        topi = np.argpartition(-s, top)[:top]
        topi = topi[np.argsort(-s[topi])]
        ranked = list(idx.creators[topi])
        r = rel[b]
        row = {"brand": b, "n_pos": len(r)}
        for k in KS:
            row[f"recall@{k}"] = recall_at_k(ranked, r, k)
        row["ndcg@50"] = ndcg_at_k(ranked, r, 50)
        row["top10_median_followers"] = float(np.median(creator_followers.reindex(ranked[:10]).fillna(0)))
        rows.append(row)
    return rows


def summarize(per_brand: dict[str, pd.DataFrame]) -> pd.DataFrame:
    cols = [f"recall@{k}" for k in KS] + ["ndcg@50", "top10_median_followers"]
    return pd.DataFrame({name: df[cols].mean() for name, df in per_brand.items()}).T.round(4)
