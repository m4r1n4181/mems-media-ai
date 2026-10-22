"""Stage 2 features for (brand, creator) pairs. Everything is computed from task.history only (no leakage)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import niches as N
from .split import Task

FEATURES = [
    # pair: does the creator already know this brand?
    "org_mentions", "org_mentions_90d", "days_since_org_mention", "knn_score", "knn_rank",
    # pair: content fit
    "niche_cosine", "same_niche",
    # creator: size, activity, experience, performance
    "log_followers", "posts_hist", "days_since_last_post", "paid_brands_total", "paid_brands_180d",
    "paid_share", "median_rel_eng", "paid_rel_eng",
    # brand: size and appetite for collaborations
    "brand_log_followers", "brand_creators_hist", "brand_paid_creators_hist", "brand_paid_creators_180d",
    # pair: does the creator's size fit the sizes this brand usually works with?
    "brand_partner_size", "size_gap",
]


def _creator_stats(task: Task, posts_hist: pd.DataFrame, creators: pd.DataFrame) -> pd.DataFrame:
    h, cut = task.history, task.cutoff
    paid = h[h.sponsored == 1].drop_duplicates(["brand", "creator_id"])
    g = posts_hist.groupby("creator_id")
    out = pd.DataFrame({
        "posts_hist": g.size(),
        "days_since_last_post": (cut - g.ts.max()).dt.days,
        "paid_share": g.sponsored.mean(),
        "median_rel_eng": g.rel_eng.median(),
    })
    out["paid_rel_eng"] = posts_hist[posts_hist.sponsored == 1].groupby("creator_id").rel_eng.mean()
    out["paid_brands_total"] = paid.groupby("creator_id").size()
    out["paid_brands_180d"] = paid[paid.ts >= cut - pd.Timedelta(days=180)].groupby("creator_id").size()
    out = out.join(np.log1p(creators.set_index("creator_id").followers).rename("log_followers"))
    return out.fillna({"paid_brands_total": 0, "paid_brands_180d": 0})


def _brand_stats(task: Task, brands: pd.DataFrame) -> pd.DataFrame:
    h, cut = task.history, task.cutoff
    paid = h[h.sponsored == 1].drop_duplicates(["brand", "creator_id"])
    out = pd.DataFrame({"brand_creators_hist": h.groupby("brand").creator_id.nunique()})
    out["brand_paid_creators_hist"] = paid.groupby("brand").size()
    out["brand_paid_creators_180d"] = paid[paid.ts >= cut - pd.Timedelta(days=180)].groupby("brand").size()
    out = out.join(np.log1p(brands.drop_duplicates("brand").set_index("brand").followers).rename("brand_log_followers"),
                   how="outer")
    return out.fillna({"brand_creators_hist": 0, "brand_paid_creators_hist": 0, "brand_paid_creators_180d": 0})


def _brand_partner_size(task: Task, creators: pd.DataFrame) -> pd.Series:
    """Typical (median) log-followers of creators the brand worked with before the cutoff.
    Falls back to creators who mentioned it organically when the brand has no paid partners yet.
    Learned from behaviour, which is more informative than the brand's own follower count."""
    lf = np.log1p(creators.set_index("creator_id").followers)
    h = task.history.drop_duplicates(["brand", "creator_id", "sponsored"])
    h = h.assign(lf=h.creator_id.map(lf)).dropna(subset=["lf"])
    paid = h[h.sponsored == 1].groupby("brand").lf.median()
    any_ = h.groupby("brand").lf.median()
    return paid.combine_first(any_).rename("brand_partner_size")


def _pair_organic(task: Task) -> pd.DataFrame:
    h, cut = task.history, task.cutoff
    o = h[h.sponsored == 0]
    g = o.groupby(["brand", "creator_id"])
    out = pd.DataFrame({"org_mentions": g.size(), "days_since_org_mention": (cut - g.ts.max()).dt.days})
    out["org_mentions_90d"] = o[o.ts >= cut - pd.Timedelta(days=90)].groupby(["brand", "creator_id"]).size()
    return out.fillna({"org_mentions_90d": 0}).reset_index()


def niche_vectors(task: Task, posts_hist: pd.DataFrame, brand_names: set[str], n_topics: int = 10):
    """Creator and brand niche mixes learned only from posts before the cutoff."""
    docs = N.creator_documents(posts_hist, brand_names)
    _, _, W = N.fit_nmf(docs, n_topics)
    B = N.brand_niches(task.history, W, min_creators=3)
    return W, B


def build(task: Task, cand: pd.DataFrame, posts: pd.DataFrame, creators: pd.DataFrame, brands: pd.DataFrame,
          niche_cache: tuple | None = None) -> tuple[pd.DataFrame, tuple]:
    """Add all FEATURES to the candidate table. Returns (features, niche_cache)."""
    posts_hist = posts[posts.ts < task.cutoff]
    df = cand.copy()
    df["knn_rank"] = df.groupby("brand").knn_score.rank(ascending=False, method="min")

    df = df.merge(_pair_organic(task), on=["brand", "creator_id"], how="left")
    df = df.fillna({"org_mentions": 0, "org_mentions_90d": 0, "days_since_org_mention": 9999})
    df = df.join(_creator_stats(task, posts_hist, creators), on="creator_id")
    df = df.join(_brand_stats(task, brands), on="brand")
    df = df.join(_brand_partner_size(task, creators), on="brand")
    df["size_gap"] = (df.log_followers - df.brand_partner_size).abs()

    W, B = niche_cache or niche_vectors(task, posts_hist, set(brands.brand))
    Wn = W.div(np.linalg.norm(W.values, axis=1), axis=0)
    Bn = B.div(np.linalg.norm(B.values, axis=1), axis=0)
    have = df.creator_id.isin(Wn.index) & df.brand.isin(Bn.index)
    cos = np.full(len(df), np.nan)
    cw = Wn.reindex(df.creator_id[have]).values
    bw = Bn.reindex(df.brand[have]).values
    cos[have.values] = (cw * bw).sum(axis=1)
    df["niche_cosine"] = cos
    same = np.full(len(df), np.nan)
    same[have.values] = (cw.argmax(axis=1) == bw.argmax(axis=1)).astype(float)
    df["same_niche"] = same
    return df, (W, B)


def add_labels(df: pd.DataFrame, task: Task) -> pd.DataFrame:
    pos = task.positives.assign(label=1)
    df = df.merge(pos, on=["brand", "creator_id"], how="left")
    df["label"] = df.label.fillna(0).astype(int)
    return df
