"""Niche affinity learned from behaviour: which creator niches does a brand actually hire?

Error analysis (notebook 04) showed two problems with the niche pool:
  * it uses one niche per creator and per brand, while creators mix niches ("mom of 3 | fashion lover");
  * it assumes brands hire creators from their own niche, but only 27-43% of new partners are in the
    brand's niche (food brands hire many parenting creators, for example).

Here creators get a MIX of niches (from their hashtags and, when available, their profile bio), and each brand
gets an AFFINITY: the niche mix of the creators it has paid before, smoothed towards the typical affinity of
brands in the same category when the brand has little history. The affinity pool then fills a brand's candidate
slots from each niche in proportion to that affinity.

Niches are the seven keyword groups in niches.KEYWORDS (interpretable, and shared by hashtags and bios).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import niches as N
from .split import Task

GROUPS = list(N.KEYWORDS)


def load_bio_niches(data_dir: Path) -> pd.DataFrame | None:
    """Keyword counts per niche from profile bios (scripts/extract_bio_niches.py). Never contains bio text."""
    f = Path(data_dir) / "bio_niches.csv"
    if not f.exists():
        return None
    bio = pd.read_csv(f).drop_duplicates("creator_id").set_index("creator_id")
    return bio[GROUPS]


def creator_mix(posts_hist: pd.DataFrame, bio: pd.DataFrame | None = None, min_hits: int = 3,
                bio_weight: float = 0.3) -> pd.DataFrame:
    """Creator x niche shares (rows sum to 1); only creators with some niche signal are returned.

    Hashtags: share of a creator's niche-keyword hashtags in each niche (at least `min_hits` such hashtags).
    Bio: share of niche keywords in the bio. When both exist they are blended (bio weight `bio_weight`);
    when only the bio exists (creators who use few hashtags) the bio alone decides.
    """
    tags = posts_hist.groupby("creator_id")["hashtags"].apply(lambda s: " ".join(s).split())
    counts = pd.DataFrame({g: tags.map(lambda t, kw=kw: sum(x in kw for x in t)) for g, kw in N.KEYWORDS.items()})
    counts = counts[counts.sum(axis=1) >= min_hits]
    mix = counts.div(counts.sum(axis=1), axis=0)
    if bio is None:
        return mix
    b = bio[bio.sum(axis=1) > 0]
    b = b.div(b.sum(axis=1), axis=0)
    both = mix.index.intersection(b.index)
    mix.loc[both] = (1 - bio_weight) * mix.loc[both] + bio_weight * b.loc[both]
    only_bio = b.index.difference(mix.index)
    return pd.concat([mix, b.loc[only_bio]])


def brand_affinity(task: Task, mix: pd.DataFrame, alpha: float = 5.0) -> pd.DataFrame:
    """Brand x niche: the niche mix of creators the brand paid before, smoothed towards its category.

    Category = the brand's strongest niche among all creators who mention it. With n paid partners,
    affinity = (n * own + alpha * category average) / (n + alpha), so 2 partners say little and 50 say a lot.
    """
    h = task.history
    mentions = h[["brand", "creator_id"]].drop_duplicates()
    mentions = mentions[mentions.creator_id.isin(mix.index)]
    mention_mix = mix.loc[mentions.creator_id].set_axis(mentions.brand.values).groupby(level=0).mean()
    category = mention_mix.idxmax(axis=1)

    paid = h[h.sponsored == 1][["brand", "creator_id"]].drop_duplicates()
    paid = paid[paid.creator_id.isin(mix.index)]
    own = mix.loc[paid.creator_id].set_axis(paid.brand.values).groupby(level=0).mean()
    n = paid.groupby("brand").size().reindex(mention_mix.index).fillna(0)

    weighted = own.mul(n.reindex(own.index), axis=0).join(category.rename("category"))
    prior = weighted.groupby("category")[GROUPS].sum().div(
        n.reindex(own.index).groupby(category.reindex(own.index)).sum(), axis=0)
    global_prior = own.mul(n.reindex(own.index), axis=0).sum() / n.sum()
    prior_b = prior.reindex(category.values).set_axis(category.index).fillna(global_prior)

    own_b = own.reindex(mention_mix.index).fillna(0)
    aff = own_b.mul(n, axis=0).add(prior_b * alpha).div(n + alpha, axis=0)
    return aff.div(aff.sum(axis=1), axis=0)


def ranked_creators(task: Task, mix: pd.DataFrame, recent_days: int = 180, min_share: float = 0.25) -> pd.DataFrame:
    """Per niche: recently paid creators with at least `min_share` of that niche, most collaborations first.
    A creator can appear in several niches (multi-niche)."""
    h = task.history
    paid = h[(h.sponsored == 1) & (h.ts >= task.cutoff - pd.Timedelta(days=recent_days))]
    n = paid.drop_duplicates(["brand", "creator_id"]).groupby("creator_id").size().rename("n")
    m = mix.join(n, how="inner")
    parts = []
    for g in GROUPS:
        sel = m[m[g] >= min_share].sort_values("n", ascending=False)
        parts.append(pd.DataFrame({"group": g, "creator_id": sel.index, "pos": np.arange(len(sel))}))
    return pd.concat(parts, ignore_index=True)


def affinity_pool(brands: list[str], aff: pd.DataFrame, ranked: pd.DataFrame, slots: int = 300) -> pd.DataFrame:
    """Fill each brand's `slots` from each niche in proportion to the brand's affinity."""
    a = aff.reindex(brands).dropna()
    alloc = (a * slots).round().astype(int).stack().rename("k").reset_index()
    alloc.columns = ["brand", "group", "k"]
    alloc = alloc[alloc.k > 0]
    pairs = alloc.merge(ranked, on="group")
    pairs = pairs[pairs.pos < pairs.k]
    return pairs[["brand", "creator_id"]].drop_duplicates()


def pair_affinity(aff: pd.DataFrame, mix: pd.DataFrame, brands: pd.Series, creators: pd.Series) -> np.ndarray:
    """How well a creator's niches match the niches this brand hires (dot product; NaN if unknown)."""
    out = np.full(len(brands), np.nan, dtype="float32")
    have = (brands.isin(aff.index) & creators.isin(mix.index)).values
    if have.any():
        out[have] = (aff.reindex(brands[have]).values * mix.reindex(creators[have]).values).sum(axis=1)
    return out
