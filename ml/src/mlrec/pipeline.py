"""Reusable steps of the two-stage recommender: candidates + features for one time window."""
from __future__ import annotations

import pandas as pd

from . import baselines as B
from . import candidates as C
from . import features as F
from . import ranker as R
from .lightgcn import LightGCN
from .split import Task

DEFAULTS = dict(knn_top=500, svd_top=300, niche_top=300, lgcn_top=300, svd_dims=128,
                lgcn=dict(dim=128, layers=2, epochs=30, batch=32768, lr=1e-2))


def prepare(task: Task, brands_to_rank: list[str], posts, creators, brands, train: bool,
            neg_per_brand: int = 300, chunk: int = 500, cfg: dict = DEFAULTS, log=print):
    """Candidates and features for `brands_to_rank` using only task.history.
    train=True keeps all positives and a sample of negatives; otherwise every candidate is kept.
    Returns (feature table, context) where context holds the fitted components."""
    idx = B.Index(task, brands_to_rank)
    niches = F.niche_vectors(task, posts[posts.ts < task.cutoff], set(brands.brand))
    svd = C.SVDEmbeddings(cfg["svd_dims"]).fit(task, idx)
    lgcn = LightGCN(verbose=False, **cfg["lgcn"]).fit(task, idx)
    log(f"{task.cutoff.date()}: embeddings trained")
    fb = F.FeatureBuilder(task, posts, creators, brands, niches, svd, idx, lgcn=lgcn)
    knn = B.BrandKNN().fit(task, idx)
    kept = []
    for start in range(0, len(brands_to_rank), chunk):
        names = brands_to_rank[start:start + chunk]
        pool = pd.concat([C.niche_pool(task, names, *niches, per_niche=cfg["niche_top"]),
                          svd.top_pairs(idx, names, cfg["svd_top"]),
                          lgcn.top_pairs(idx, names, cfg["lgcn_top"])])
        cand = C.generate(task, idx, names, knn_top=cfg["knn_top"], extra=pool, knn=knn)
        df = F.add_labels(fb.transform(cand), task)
        kept.append(R.sample_training_groups(df, neg_per_brand) if train else df)
    out = pd.concat(kept, ignore_index=True)
    return out, {"idx": idx, "niches": niches, "feature_builder": fb}
