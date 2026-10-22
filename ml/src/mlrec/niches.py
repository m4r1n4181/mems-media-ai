"""Derive content niches (fashion, beauty, fitness, ...) from hashtags.

Instagram's own profile category is not a content niche (64% of creators are just
"Creators & Celebrities"), so niches are learned from what creators actually post about:
  * NMF topic model over each creator's hashtags (unsupervised, discovers niches)
  * a small keyword dictionary (transparent, used as a sanity check)
Brands inherit niches from the creators who mention them.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer

# Hashtags that say nothing about the topic: disclosure tags, generic engagement tags,
# and shopping-platform tags (LIKEtoKNOW.it) that appear across many niches.
STOP_TAGS = {
    "ad", "ads", "sponsored", "sponsor", "spon", "paidpartnership", "partner", "collab", "gifted",
    "advertisement", "werbung", "anzeige", "love", "instagood", "photooftheday", "picoftheday",
    "instadaily", "happy", "beautiful", "girl", "repost", "photography", "summer", "influencer",
    "blogger", "liketkit", "liketoknowit", "ltkunder50", "ltkunder100", "ltksalealert", "ltkstyletip",
    "ltkshoecrush", "ltkitbag", "ltkhome", "ltkbeauty", "ltkfit", "ltkkids", "ltkfamily",
    "ltktravel", "ltkcurves", "ltkwedding", "ltkspring", "ltkseasonal", "ltkbump", "ltkmens",
}

KEYWORDS = {
    "fashion": {"fashion", "ootd", "outfit", "outfitoftheday", "style", "streetstyle", "fashionblogger",
                "styleblogger", "whatiwore", "wiw", "lookoftheday", "fashionista", "instafashion", "styleinspo"},
    "beauty": {"makeup", "beauty", "skincare", "mua", "beautyblogger", "makeupartist", "motd",
               "wakeupandmakeup", "lipstick", "eyeshadow", "nails", "hair"},
    "fitness": {"fitness", "gym", "workout", "fitfam", "fit", "health", "yoga", "fitnessmotivation",
                "training", "running", "healthy"},
    "food": {"food", "foodie", "foodblogger", "feedfeed", "f52grams", "foodporn", "recipe", "vegan",
             "baking", "yum", "delicious", "instafood"},
    "travel": {"travel", "travelblogger", "wanderlust", "traveltheworld", "travelgram", "vacation",
               "explore", "adventure"},
    "family": {"momlife", "mom", "motherhood", "family", "kids", "baby", "momblogger", "toddler"},
    "home": {"home", "homedecor", "interiordesign", "interior", "decor", "homedesign"},
}


def brand_tag_filter(brand_names: set[str]):
    """Campaign hashtags (#danielwellington, #dwforeveryone, #fashionnovacurve) describe a brand deal,
    not the creator's niche. Without removing them, NMF learns 'brand topics' instead of niches.
    Returns a fast, cached predicate: tag -> is it a brand/campaign tag?
    Generic words that some brand happens to use as a handle (e.g. 'fitness') are protected."""
    protected = set().union(*KEYWORDS.values())
    names = {b.replace(".", "").replace("_", "") for b in brand_names} - protected
    prefixes = {b for b in names if len(b) >= 6}
    cache: dict[str, bool] = {}

    def is_brand(tag: str) -> bool:
        if tag not in cache:
            cache[tag] = tag not in protected and (
                tag in names or any(tag[:n] in prefixes for n in range(6, len(tag) + 1)))
        return cache[tag]
    return is_brand


# Names for the 10-topic NMF solution (seed=0), assigned by reading each topic's top hashtags
# in notebooks/01_data_exploration.ipynb. Re-check them if the data, filters or seed change.
NICHE_NAMES = {
    0: "general lifestyle", 1: "food", 2: "fashion blogging", 3: "beauty & makeup", 4: "parenting",
    5: "fitness", 6: "travel", 7: "shoppable fashion (LTK)", 8: "home & interior",
    9: "fast fashion & campaign tags",
}


def creator_documents(posts: pd.DataFrame, brand_names: set[str] | None = None, min_tags: int = 20) -> pd.Series:
    """One 'document' per creator: all hashtags they used (minus stop tags and brand campaign tags)."""
    is_brand = brand_tag_filter(brand_names or set())
    tags = posts.groupby("creator_id")["hashtags"].apply(lambda s: " ".join(s))
    tags = tags.map(lambda t: " ".join(h for h in t.split() if h not in STOP_TAGS and not is_brand(h)))
    return tags[tags.str.split().str.len() >= min_tags]


def fit_nmf(docs: pd.Series, n_topics: int, seed: int = 0):
    """TF-IDF over hashtags, then NMF. Returns (vectorizer, model, creator x topic weights)."""
    vec = TfidfVectorizer(token_pattern=r"\S+", min_df=20, max_df=0.3, sublinear_tf=True)
    X = vec.fit_transform(docs.values)
    nmf = NMF(n_components=n_topics, init="nndsvda", random_state=seed, max_iter=400)
    W = nmf.fit_transform(X)
    W = W / np.maximum(W.sum(axis=1, keepdims=True), 1e-12)   # each creator's topic mix sums to 1
    return vec, nmf, pd.DataFrame(W, index=docs.index)


def top_terms(vec, nmf, n: int = 10) -> list[list[str]]:
    terms = np.array(vec.get_feature_names_out())
    return [list(terms[np.argsort(-comp)[:n]]) for comp in nmf.components_]


def npmi_coherence(docs: pd.Series, topics: list[list[str]], top: int = 10) -> list[float]:
    """Topic coherence: do a topic's top hashtags actually co-occur in the same creators?
    NPMI ranges from -1 (never together) to 1 (always together). Higher = more interpretable topic."""
    sets = [set(d.split()) for d in docs.values]
    n = len(sets)
    vocab = {t for tp in topics for t in tp[:top]}
    df = {t: sum(t in s for s in sets) for t in vocab}
    scores = []
    for tp in topics:
        tp = tp[:top]
        vals = []
        for i in range(len(tp)):
            for j in range(i + 1, len(tp)):
                a, b = tp[i], tp[j]
                both = sum(a in s and b in s for s in sets)
                if both == 0:
                    vals.append(-1.0)
                    continue
                p_ab, p_a, p_b = both / n, df[a] / n, df[b] / n
                vals.append(np.log(p_ab / (p_a * p_b)) / -np.log(p_ab))
        scores.append(float(np.mean(vals)))
    return scores


def keyword_niches(docs: pd.Series) -> pd.DataFrame:
    """Share of each creator's hashtags that fall into each keyword niche."""
    def shares(doc):
        toks = doc.split()
        return {k: sum(t in v for t in toks) / len(toks) for k, v in KEYWORDS.items()}
    return pd.DataFrame([shares(d) for d in docs.values], index=docs.index)


def brand_niches(interactions: pd.DataFrame, creator_topics: pd.DataFrame, min_creators: int = 3) -> pd.DataFrame:
    """A brand's niche mix = average niche mix of the distinct creators who mention it."""
    pairs = interactions[["brand", "creator_id"]].drop_duplicates()
    pairs = pairs[pairs.creator_id.isin(creator_topics.index)]
    counts = pairs.groupby("brand").size()
    pairs = pairs[pairs.brand.isin(counts[counts >= min_creators].index)]
    joined = creator_topics.loc[pairs.creator_id.to_numpy()]
    joined.index = pairs.brand.to_numpy()
    return joined.groupby(level=0).mean()
