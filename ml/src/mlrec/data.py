"""Load the extracted tables, pseudonymize creators, build the brand–creator interaction table."""
from __future__ import annotations

import hashlib
import secrets
from pathlib import Path

import numpy as np
import pandas as pd

from .config import DATA_DIR


def _salt(data_dir: Path) -> str:
    """Secret salt kept next to the data (never in git), so pseudonyms cannot be reversed by guessing usernames."""
    f = data_dir / "pseudonym_salt.txt"
    if not f.exists():
        f.write_text(secrets.token_hex(16))
    return f.read_text().strip()


def pseudonymize(usernames: pd.Series, salt: str) -> pd.Series:
    return usernames.map(lambda u: "c_" + hashlib.sha256((salt + u).encode()).hexdigest()[:10])


def load_posts(data_dir: Path = DATA_DIR) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Returns (posts, creators, brands) with creators pseudonymized and engagement features added."""
    posts = pd.read_csv(data_dir / "posts.csv", keep_default_na=False,
                        dtype={"hashtags": str, "mentions": str, "user": str})
    creators = pd.read_csv(data_dir / "influencers.csv", keep_default_na=False, dtype={"username": str})
    brands = pd.read_csv(data_dir / "brands.csv", keep_default_na=False, dtype={"username": str})

    salt = _salt(data_dir)
    posts["creator_id"] = pseudonymize(posts["user"], salt)
    creators["creator_id"] = pseudonymize(creators["username"], salt)
    posts = posts.drop(columns=["user"])
    creators = creators.drop(columns=["username"])

    posts["ts"] = pd.to_datetime(pd.to_numeric(posts["ts"], errors="coerce"), unit="s")
    posts["likes"] = pd.to_numeric(posts["likes"], errors="coerce")
    posts = posts.dropna(subset=["ts", "likes"]).sort_values(["creator_id", "ts"])

    # Engagement relative to the creator's own recent history (previous 20 posts, no look-ahead).
    posts["log_likes"] = np.log1p(posts["likes"])
    prev_median = (posts.groupby("creator_id")["log_likes"]
                   .transform(lambda s: s.shift(1).rolling(20, min_periods=5).median()))
    posts["rel_eng"] = posts["log_likes"] - prev_median

    for c in ["followers", "followees", "posts"]:
        creators[c] = pd.to_numeric(creators[c], errors="coerce")
        brands[c] = pd.to_numeric(brands[c], errors="coerce")
    brands = brands.rename(columns={"username": "brand"})
    brands["brand"] = brands["brand"].str.lower()
    return posts, creators, brands


def to_interactions(posts: pd.DataFrame, brands: pd.DataFrame) -> pd.DataFrame:
    """One row per (post, mentioned brand): the basic unit of the recommender."""
    brand_set = set(brands["brand"])
    posts = posts.copy()
    posts["brand"] = posts["mentions"].str.split().map(
        lambda ms: sorted({m for m in ms if m in brand_set}) if isinstance(ms, list) else [])
    return (posts[["post_id", "creator_id", "brand", "ts", "sponsored", "log_likes", "rel_eng"]]
            .explode("brand").dropna(subset=["brand"]).reset_index(drop=True))


def load(data_dir: Path = DATA_DIR) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Returns (interactions, creators, brands)."""
    posts, creators, brands = load_posts(data_dir)
    return to_interactions(posts, brands), creators, brands
