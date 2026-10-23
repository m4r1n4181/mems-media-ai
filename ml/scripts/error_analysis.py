"""Error analysis of candidate generation: which future partners are never retrieved, and why?

The ranker can only reorder what candidate generation gives it, so a partner that is not retrieved is lost
for good. This script rebuilds the candidates exactly as the final model does, on the VALIDATION window
(the test window stays untouched), and describes every real new partnership at prediction time:
was it retrieved, by which source, and what did the creator and the brand look like?

    python scripts/error_analysis.py        # ~10 min; writes artifacts/error_analysis_val.parquet
                                            # and results/error_analysis_val.json (aggregates)
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd

from mlrec import baselines as B
from mlrec import candidates as C
from mlrec import niches as N
from mlrec.config import ARTIFACTS_DIR
from mlrec.data import load_posts, to_interactions
from mlrec.lightgcn import LightGCN
from mlrec.pipeline import DEFAULTS
from mlrec.split import make_task

WINDOW = ("2018-10-01", "2019-01-01")     # validation: the same window used for every model decision
RESULTS = Path(__file__).resolve().parents[1] / "results"
T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:6.0f}s] {msg}", flush=True)


posts, creators, brands = load_posts()
inter = to_interactions(posts, brands)
task = make_task(inter, *WINDOW)
h, pos = task.history, task.positives.copy()
eval_brands = sorted(pos.brand.unique())
log(f"{len(pos):,} new partnerships for {len(eval_brands):,} brands")

# ---- rebuild the candidate sources exactly as in the final model, remembering where each pair came from
cfg = DEFAULTS
idx = B.Index(task, eval_brands)
# same as features.niche_vectors, but keeping the topic model so the topics can be named for this cutoff
docs = N.creator_documents(posts[posts.ts < task.cutoff], set(brands.brand))
vec, nmf, W = N.fit_nmf(docs, 10)
Bn = N.brand_niches(task.history, W, min_creators=3)
topic_terms = N.top_terms(vec, nmf, 10)
svd = C.SVDEmbeddings(cfg["svd_dims"]).fit(task, idx)
lgcn = LightGCN(verbose=False, **cfg["lgcn"]).fit(task, idx)
knn = B.BrandKNN().fit(task, idx)
log("candidate models fitted")

pos_keys = pd.MultiIndex.from_frame(pos[["brand", "creator_id"]])
found = {s: pd.Series(False, index=pos_keys) for s in ["organic", "knn", "niche", "svd", "lgcn"]}


def mark(source: str, pairs: pd.DataFrame) -> None:
    hit = pd.MultiIndex.from_frame(pairs[["brand", "creator_id"]]).intersection(pos_keys)
    found[source].loc[hit] = True


# "What if" sources, to estimate how much each fix could gain before building it (ceiling analysis):
#   pop300 / pop1000: the most active paid creators overall, added for every brand, whatever their niche
#   niche_top2: the niche pool built from the brand's two strongest niches instead of only the first
WHATIF = ["pop300", "pop1000", "niche_top2"]
for s_ in WHATIF:
    found[s_] = pd.Series(False, index=pos_keys)
recent_paid = h[(h.sponsored == 1) & (h.ts >= task.cutoff - pd.Timedelta(days=180))]
activity = recent_paid.drop_duplicates(["brand", "creator_id"]).groupby("creator_id").size().sort_values(ascending=False)
n_by_creator = activity.rename("n").to_frame().join(W.idxmax(axis=1).rename("niche"), how="inner")
top_by_niche = n_by_creator.sort_values("n", ascending=False).groupby("niche").head(cfg["niche_top"]).reset_index()
brand_top2 = Bn.apply(lambda r: list(r.nlargest(2).index), axis=1)


def popularity_pairs(names, k):
    top = activity.index[:k]
    return pd.DataFrame({"brand": np.repeat(names, len(top)), "creator_id": np.tile(top, len(names))})


def niche_top2_pairs(names):
    b = brand_top2.reindex(names).dropna().explode().rename("niche").reset_index().rename(columns={"index": "brand"})
    return b.merge(top_by_niche[["creator_id", "niche"]], on="niche")[["brand", "creator_id"]]


n_candidates = 0
organic = h[(h.sponsored == 0)][["brand", "creator_id"]].drop_duplicates()
mark("organic", organic[organic.brand.isin(eval_brands)])
for start in range(0, len(eval_brands), 400):
    names = eval_brands[start:start + 400]
    s = knn.score(idx.b_pos[names].values)
    top = np.argpartition(-s, cfg["knn_top"], axis=1)[:, :cfg["knn_top"]]
    mark("knn", pd.DataFrame({"brand": np.repeat(names, cfg["knn_top"]), "creator_id": idx.creators[top.ravel()]}))
    mark("niche", C.niche_pool(task, names, W, Bn, per_niche=cfg["niche_top"]))
    mark("svd", svd.top_pairs(idx, names, cfg["svd_top"]))
    mark("lgcn", lgcn.top_pairs(idx, names, cfg["lgcn_top"]))
    pool = pd.concat([C.niche_pool(task, names, W, Bn, per_niche=cfg["niche_top"]),
                      svd.top_pairs(idx, names, cfg["svd_top"]), lgcn.top_pairs(idx, names, cfg["lgcn_top"])])
    n_candidates += len(C.generate(task, idx, names, knn_top=cfg["knn_top"], extra=pool, knn=knn))
    mark("pop300", popularity_pairs(names, 300))
    mark("pop1000", popularity_pairs(names, 1000))
    mark("niche_top2", niche_top2_pairs(names))
log("sources marked")
CURRENT = ["organic", "knn", "niche", "svd", "lgcn"]

for s, f in found.items():
    pos[f"by_{s}"] = f.values
pos["retrieved"] = pos[[f"by_{s}" for s in CURRENT]].any(axis=1)

# ---- what each creator and brand looked like at the cutoff (only history, no look-ahead)
cutoff = task.cutoff
ph = posts[posts.ts < cutoff]
c_posts = ph.groupby("creator_id").agg(posts_hist=("post_id", "size"), last_post=("ts", "max"))
c_inter = h.groupby("creator_id").agg(brands_mentioned=("brand", "nunique"))
paid = h[h.sponsored == 1]
c_paid = paid.groupby("creator_id").agg(paid_brands=("brand", "nunique"))
c_paid180 = (paid[paid.ts >= cutoff - pd.Timedelta(days=180)].groupby("creator_id").brand.nunique()
             .rename("paid_brands_180d"))
c_niche = W.idxmax(axis=1).where(W.max(axis=1) > 0).rename("creator_niche")
b_niche = Bn.idxmax(axis=1).where(Bn.max(axis=1) > 0).rename("brand_niche")
b_hist = h.groupby("brand").agg(brand_creators=("creator_id", "nunique"))
b_paid = paid.groupby("brand").agg(brand_paid_creators=("creator_id", "nunique"))
fol = creators.drop_duplicates("creator_id").set_index("creator_id").followers.rename("followers")
bfol = brands.drop_duplicates("brand").set_index("brand").followers.rename("brand_followers")
new_in_window = pos.groupby("creator_id").brand.nunique().rename("new_brands_in_window")

df = (pos.join(c_posts, on="creator_id").join(c_inter, on="creator_id").join(c_paid, on="creator_id")
      .join(c_paid180, on="creator_id").join(c_niche, on="creator_id").join(fol, on="creator_id")
      .join(new_in_window, on="creator_id")
      .join(b_niche, on="brand").join(b_hist, on="brand").join(b_paid, on="brand").join(bfol, on="brand"))
for c in ["brands_mentioned", "paid_brands", "paid_brands_180d", "brand_creators", "brand_paid_creators"]:
    df[c] = df[c].fillna(0).astype(int)
df["days_since_last_post"] = (cutoff - df.last_post).dt.days
df["same_niche"] = np.where(df.creator_niche.isna() | df.brand_niche.isna(), "unknown",
                            np.where(df.creator_niche == df.brand_niche, "same", "different"))
df["size_tier"] = pd.cut(df.followers, [0, 10_000, 50_000, 500_000, np.inf],
                         labels=["nano <10k", "micro 10–50k", "mid 50–500k", "macro 500k+"])
df = df.drop(columns="last_post")

ARTIFACTS_DIR.mkdir(exist_ok=True)
df.to_parquet(ARTIFACTS_DIR / "error_analysis_val.parquet", index=False)

# ---- aggregates for the notebook and git (no per-creator rows)
summary = {
    "window": WINDOW, "new_partnerships": int(len(df)), "brands": int(df.brand.nunique()),
    "candidate_recall": float(df.retrieved.mean()),
    "candidates_per_brand": n_candidates / len(eval_brands),
    "recall_by_source": {s: float(df[f"by_{s}"].mean()) for s in CURRENT},
    "only_this_source": {s: float((df[f"by_{s}"] & (df[[f"by_{o}" for o in CURRENT if o != s]].sum(axis=1) == 0)).mean())
                         for s in CURRENT},
    "what_if_recall": {s: float((df.retrieved | df[f"by_{s}"]).mean()) for s in WHATIF},
    "topics": {i: terms for i, terms in enumerate(topic_terms)},
}
(RESULTS / "error_analysis_val.json").write_text(json.dumps(summary, indent=2))
log(f"candidate recall {summary['candidate_recall']:.3f}; wrote artifacts/error_analysis_val.parquet")
