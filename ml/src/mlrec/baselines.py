"""Baseline scorers. fit() once per task, then score(brands) returns a dense (len(brands) x n_candidates) matrix.
Scoring is done in batches of brands to keep memory bounded."""
from __future__ import annotations

import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.preprocessing import normalize

from .split import Task


class Index:
    def __init__(self, task: Task, eval_brands: list[str]):
        self.creators = task.candidates
        self.c_pos = pd.Series(np.arange(len(self.creators)), index=self.creators)
        self.brands = pd.Index(sorted(set(task.history.brand) | set(eval_brands)))
        self.b_pos = pd.Series(np.arange(len(self.brands)), index=self.brands)
        self.eval_brands = eval_brands


def interaction_matrix(task: Task, idx: Index, paid_w=1.0, organic_w=0.5, half_life_days=None) -> sp.csr_matrix:
    h = task.history
    w = np.where(h.sponsored == 1, paid_w, organic_w).astype(float)
    if half_life_days:
        age = (task.cutoff - h.ts).dt.days.values
        w = w * 0.5 ** (age / half_life_days)
    m = sp.coo_matrix((w, (idx.b_pos[h.brand].values, idx.c_pos[h.creator_id].values)),
                      shape=(len(idx.brands), len(idx.creators))).tocsr()
    m.sum_duplicates()
    m.eliminate_zeros()
    return m


def popularity_vector(task: Task, idx: Index, recent_days: int | None = None) -> np.ndarray:
    h = task.history[task.history.sponsored == 1]
    if recent_days:
        h = h[h.ts >= task.cutoff - pd.Timedelta(days=recent_days)]
    cnt = h.drop_duplicates(["brand", "creator_id"]).groupby("creator_id").size()
    return cnt.reindex(idx.creators, fill_value=0).values.astype(np.float32)


class Popularity:
    """Same ranking for every brand: creators with the most distinct paid collaborations."""
    def __init__(self, recent_days=None):
        self.recent_days = recent_days

    def fit(self, task, idx):
        self.v = popularity_vector(task, idx, self.recent_days)
        return self

    def score(self, rows):
        return np.tile(self.v, (len(rows), 1))


class OrganicMentions:
    """Creators who already mention the brand without being paid, weighted by recency."""
    def __init__(self, half_life_days=90):
        self.hl = half_life_days

    def fit(self, task, idx):
        self.org = interaction_matrix(task, idx, paid_w=0.0, organic_w=1.0, half_life_days=self.hl)
        self.tie = 1e-6 * popularity_vector(task, idx, 180)
        return self

    def score(self, rows):
        return self.org[rows].toarray().astype(np.float32) + self.tie


class BrandKNN:
    """Item-kNN: a creator scores high if similar brands (sharing creators) paid them."""
    def __init__(self, k=50, half_life_days=180):
        self.k, self.hl = k, half_life_days

    def fit(self, task, idx):
        m = interaction_matrix(task, idx, half_life_days=self.hl)
        self.mn = normalize(m, norm="l2", axis=1).tocsr()
        self.mnT = self.mn.T.tocsc()
        self.paid = interaction_matrix(task, idx, paid_w=1.0, organic_w=0.0, half_life_days=self.hl).tocsr()
        self.tie = 1e-6 * popularity_vector(task, idx, 180)
        return self

    def score(self, rows):
        sim = (self.mn[rows] @ self.mnT).toarray()
        sim[np.arange(len(rows)), rows] = 0.0
        if self.k < sim.shape[1]:
            thr = -np.partition(-sim, self.k, axis=1)[:, self.k][:, None]
            sim[sim < thr] = 0.0
        return (sp.csr_matrix(sim) @ self.paid).toarray().astype(np.float32) + self.tie
