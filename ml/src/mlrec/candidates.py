"""Stage 1 — candidate generation: shrink ~35k creators to a few hundred plausible ones per brand."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .baselines import BrandKNN, Index
from .split import Task


class SVDEmbeddings:
    """Matrix factorization of the brand x creator interaction matrix (truncated SVD).
    Every brand and creator gets a k-dimensional vector; pairs that interact get similar vectors.
    Their dot product is a 'latent affinity' score, and its top-N is an extra candidate source."""
    def __init__(self, k: int = 128, half_life_days: int = 180):
        self.k, self.hl = k, half_life_days

    def fit(self, task: Task, idx: Index):
        from sklearn.decomposition import TruncatedSVD
        from .baselines import interaction_matrix
        m = interaction_matrix(task, idx, half_life_days=self.hl)
        m.data = np.log1p(m.data * 10)          # dampen pairs with very many mentions
        svd = TruncatedSVD(self.k, random_state=0)
        self.U = svd.fit_transform(m).astype(np.float32)
        self.V = svd.components_.T.astype(np.float32)
        return self

    def score(self, rows):
        return self.U[rows] @ self.V.T

    def pair_scores(self, idx: Index, brand_names, creator_ids) -> np.ndarray:
        bu = self.U[idx.b_pos[brand_names].values]
        cv = self.V[idx.c_pos[creator_ids].values]
        return (bu * cv).sum(axis=1)

    def top_pairs(self, idx: Index, brands: list[str], n: int, batch: int = 400) -> pd.DataFrame:
        parts = []
        for start in range(0, len(brands), batch):
            names = brands[start:start + batch]
            s = self.score(idx.b_pos[names].values)
            top = np.argpartition(-s, n, axis=1)[:, :n]
            parts.append(pd.DataFrame({"brand": np.repeat(names, n), "creator_id": idx.creators[top.ravel()]}))
        return pd.concat(parts)


def niche_pool(task: Task, brands: list[str], creator_niches: pd.DataFrame, brand_niches: pd.DataFrame,
               per_niche: int = 300, recent_days: int = 180) -> pd.DataFrame:
    """Recently active, experienced creators from the brand's dominant niche.
    91% of future partners had already been paid by some brand, so 'experienced in my niche' is a good pool."""
    h = task.history
    paid = h[(h.sponsored == 1) & (h.ts >= task.cutoff - pd.Timedelta(days=recent_days))]
    n = paid.drop_duplicates(["brand", "creator_id"]).groupby("creator_id").size().rename("n")
    pool = n.to_frame().join(creator_niches.idxmax(axis=1).rename("niche"), how="inner")
    top = pool.sort_values("n", ascending=False).groupby("niche").head(per_niche).reset_index()
    bn = brand_niches.idxmax(axis=1).rename("niche")
    b = pd.DataFrame({"brand": brands}).join(bn, on="brand").dropna()
    return b.merge(top[["creator_id", "niche"]], on="niche")[["brand", "creator_id"]]


def generate(task: Task, idx: Index, brands: list[str], knn_top: int = 200, batch: int = 400,
             extra: pd.DataFrame | None = None, knn: BrandKNN | None = None) -> pd.DataFrame:
    """Union of (a) every creator who organically mentioned the brand before the cutoff,
    (b) the top `knn_top` creators from brand kNN and (c) optional extra (brand, creator_id) pairs,
    e.g. from niche_pool. Already-paid pairs are excluded (we look for NEW partners).
    Returns columns: brand, creator_id, knn_score."""
    h = task.history
    organic = (h[(h.sponsored == 0) & h.brand.isin(brands)][["brand", "creator_id"]].drop_duplicates())

    knn = knn or BrandKNN().fit(task, idx)
    parts = []
    for start in range(0, len(brands), batch):
        names = brands[start:start + batch]
        s = knn.score(idx.b_pos[names].values)
        top = np.argpartition(-s, knn_top, axis=1)[:, :knn_top]
        vals = np.take_along_axis(s, top, axis=1)
        parts.append(pd.DataFrame({
            "brand": np.repeat(names, knn_top),
            "creator_id": idx.creators[top.ravel()],
            "knn_score": vals.ravel(),
        }))
        # kNN scores for the organic candidates of these brands too (so every candidate has the feature)
        o = organic[organic.brand.isin(names)]
        if extra is not None:
            o = pd.concat([o, extra[extra.brand.isin(names)]]).drop_duplicates()
        if len(o):
            row_of = pd.Series(np.arange(len(names)), index=names)
            parts.append(pd.DataFrame({
                "brand": o.brand.values, "creator_id": o.creator_id.values,
                "knn_score": s[row_of[o.brand].values, idx.c_pos[o.creator_id].values],
            }))
    cand = pd.concat(parts).sort_values("knn_score", ascending=False).drop_duplicates(["brand", "creator_id"])
    cand["knn_score"] = cand.knn_score.astype("float32")
    known = pd.DataFrame(list(task.known_pairs), columns=["brand", "creator_id"])
    cand = cand.merge(known.assign(_k=1), on=["brand", "creator_id"], how="left")
    return cand[cand._k.isna()].drop(columns="_k").reset_index(drop=True)


def candidate_recall(cand: pd.DataFrame, task: Task) -> float:
    """Share of true future partners that made it into the candidate set (upper bound for the ranker)."""
    hit = task.positives.merge(cand[["brand", "creator_id"]], on=["brand", "creator_id"], how="inner")
    return len(hit) / len(task.positives)
