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
    "niche_cosine", "same_niche", "svd_score", "svd_rank", "lgcn_score", "lgcn_rank",
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


class FeatureBuilder:
    """Computes everything that does not depend on the specific pair ONCE per task (creator stats,
    brand stats, niche vectors, organic-mention table), then adds features to candidate chunks.
    Working in chunks keeps memory bounded: millions of candidate rows never exist at the same time."""

    def __init__(self, task: Task, posts: pd.DataFrame, creators: pd.DataFrame, brands: pd.DataFrame,
                 niches: tuple, svd, idx, lgcn=None):
        posts_hist = posts[posts.ts < task.cutoff]
        self.task, self.svd, self.idx, self.lgcn = task, svd, idx, lgcn
        self.organic = _pair_organic(task).set_index(["brand", "creator_id"])
        self.creator_stats = _creator_stats(task, posts_hist, creators)
        self.brand_stats = _brand_stats(task, brands).join(_brand_partner_size(task, creators))
        W, B = niches
        self.Wn = W.div(np.linalg.norm(W.values, axis=1), axis=0)
        self.Bn = B.div(np.linalg.norm(B.values, axis=1), axis=0)

    def transform(self, cand: pd.DataFrame) -> pd.DataFrame:
        df = cand.copy()
        df["knn_rank"] = df.groupby("brand").knn_score.rank(ascending=False, method="min")
        df["svd_score"] = self.svd.pair_scores(self.idx, df.brand, df.creator_id)
        df["svd_rank"] = df.groupby("brand").svd_score.rank(ascending=False, method="min")
        if self.lgcn is not None:
            df["lgcn_score"] = self.lgcn.pair_scores(self.idx, df.brand, df.creator_id)
            df["lgcn_rank"] = df.groupby("brand").lgcn_score.rank(ascending=False, method="min")
        else:
            df["lgcn_score"], df["lgcn_rank"] = np.nan, np.nan

        df = df.join(self.organic, on=["brand", "creator_id"])
        df = df.fillna({"org_mentions": 0, "org_mentions_90d": 0, "days_since_org_mention": 9999})
        df = df.join(self.creator_stats, on="creator_id").join(self.brand_stats, on="brand")
        df["size_gap"] = (df.log_followers - df.brand_partner_size).abs()

        have = (df.creator_id.isin(self.Wn.index) & df.brand.isin(self.Bn.index)).values
        cw = self.Wn.reindex(df.creator_id[have]).values
        bw = self.Bn.reindex(df.brand[have]).values
        df["niche_cosine"] = np.nan
        df.loc[have, "niche_cosine"] = (cw * bw).sum(axis=1)
        df["same_niche"] = np.nan
        df.loc[have, "same_niche"] = (cw.argmax(axis=1) == bw.argmax(axis=1)).astype(float)
        df[FEATURES] = df[FEATURES].astype("float32")
        return df


def add_labels(df: pd.DataFrame, task: Task) -> pd.DataFrame:
    pos = task.positives.assign(label=1)
    df = df.merge(pos, on=["brand", "creator_id"], how="left")
    df["label"] = df.label.fillna(0).astype(int)
    return df
