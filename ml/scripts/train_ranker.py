"""Train the LightGBM ranker on an earlier window and evaluate it on validation (or test).

    python scripts/train_ranker.py          # train on Jul–Sep 2018, evaluate on Oct–Dec 2018
    python scripts/train_ranker.py test     # train on Oct–Dec 2018, evaluate once on Jan–Apr 2019
    python scripts/train_ranker.py val 300 R7   # optional: negatives per brand, experiment id for MLflow
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd

from mlrec import baselines as B
from mlrec import candidates as C
from mlrec import features as F
from mlrec import ranker as R
from mlrec.lightgcn import LightGCN
from mlrec import tracking
from mlrec.config import ARTIFACTS_DIR
from mlrec.data import load_posts, to_interactions
from mlrec.evaluate import summarize
from mlrec.split import make_task

# Several earlier windows are stacked for training: more examples of "who started working with whom".
WINDOWS = {
    # walk-forward fold 1: same setup shifted one quarter back
    "fold1": {"train": [("2018-01-01", "2018-04-01"), ("2018-04-01", "2018-07-01")],
              "eval": ("2018-07-01", "2018-10-01")},
    "val":  {"train": [("2018-04-01", "2018-07-01"), ("2018-07-01", "2018-10-01")],
             "eval": ("2018-10-01", "2019-01-01")},
    "test": {"train": [("2018-07-01", "2018-10-01"), ("2018-10-01", "2019-01-01")],
             "eval": ("2019-01-01", "2019-05-01")},
}
NEG_PER_BRAND = int(sys.argv[2]) if len(sys.argv) > 2 else 300
SVD_TOP = 300   # extra candidates per brand from SVD embeddings
KNN_TOP = 500   # candidates per brand from brand kNN
NICHE_TOP = 300 # experienced, recently active creators per niche
SVD_DIMS = 128
LGCN_TOP = 300  # extra candidates per brand from LightGCN
LGCN = dict(dim=128, layers=2, epochs=30, batch=32768, lr=1e-2, half_life_days=None)  # time decay helps LightGCN alone (B7) but not the ranker (R8)
EXP_ID = sys.argv[3] if len(sys.argv) > 3 else None
CANDIDATE_RECALL = {}
mode = sys.argv[1] if len(sys.argv) > 1 else "val"


def log(msg, t0=[time.time()]):
    print(f"[{time.time() - t0[0]:6.0f}s] {msg}", flush=True)


posts, creators, brands = load_posts()
inter = to_interactions(posts, brands)
followers = creators.set_index("creator_id").followers
log("data loaded")


def prepare(window, train: bool, chunk: int = 500):
    """Candidates + features for one window, processed in chunks of brands to bound memory.
    For training windows only the sampled rows are kept; for evaluation every candidate is
    scored by `score_fn` and only the scores are kept."""
    task = make_task(inter, *window)
    eval_brands = sorted(task.positives.brand.unique())
    idx = B.Index(task, eval_brands)
    niches = F.niche_vectors(task, posts[posts.ts < task.cutoff], set(brands.brand))
    svd = C.SVDEmbeddings(SVD_DIMS).fit(task, idx)
    lgcn = LightGCN(verbose=False, **LGCN).fit(task, idx)
    log(f"{window}: LightGCN trained")
    fb = F.FeatureBuilder(task, posts, creators, brands, niches, svd, idx, lgcn=lgcn)
    knn = B.BrandKNN().fit(task, idx)
    kept, n_cand, n_hit = [], 0, 0
    for start in range(0, len(eval_brands), chunk):
        names = eval_brands[start:start + chunk]
        pool = pd.concat([C.niche_pool(task, names, *niches, per_niche=NICHE_TOP),
                          svd.top_pairs(idx, names, SVD_TOP),
                          lgcn.top_pairs(idx, names, LGCN_TOP)])
        cand = C.generate(task, idx, names, knn_top=KNN_TOP, extra=pool, knn=knn)
        df = F.add_labels(fb.transform(cand), task)
        n_cand += len(df); n_hit += int(df.label.sum())
        kept.append(R.sample_training_groups(df, NEG_PER_BRAND) if train else df[KEEP_EVAL])
        del cand, df
    CANDIDATE_RECALL[window[0]] = n_hit / len(task.positives)
    log(f"{window}: {len(eval_brands)} brands, {n_cand:,} candidates ({n_cand / len(eval_brands):.0f}/brand), "
        f"candidate recall {n_hit / len(task.positives):.3f}")
    return task, pd.concat(kept, ignore_index=True)


train_parts = []
for w in WINDOWS[mode]["train"]:
    _, df_w = prepare(w, train=True)
    # brand ids are suffixed per window so the same brand in two windows forms two separate ranking groups
    train_parts.append(df_w.assign(brand=df_w.brand + "@" + w[0]))
    del df_w
train_df = pd.concat(train_parts).sort_values("brand").reset_index(drop=True)
KEEP_EVAL = ["brand", "creator_id", "label"] + F.FEATURES   # features kept to compare simple heuristics
eval_task, eval_df = prepare(WINDOWS[mode]["eval"], train=False)

model = R.train(train_df)
log("ranker trained")
eval_df["ranker"] = model.predict(eval_df[F.FEATURES])

# Baselines re-scored on the same candidate table, for an apples-to-apples comparison
eval_df["organic only"] = (eval_df.org_mentions_90d * 1e3 + eval_df.org_mentions * 10
                          - eval_df.days_since_org_mention / 1e4 + eval_df.knn_score * 1e-6)  # kNN breaks ties
eval_df["kNN only"] = eval_df.knn_score
per_brand = {name: R.evaluate_scored(eval_df, name, eval_task, followers)
             for name in ["organic only", "kNN only", "ranker"]}
summary = summarize(per_brand)
print("\nOverall:\n", summary.to_string())
by_bucket = pd.concat({n: d.groupby("bucket", observed=True)["recall@50"].mean() for n, d in per_brand.items()}, axis=1)
print("\nRecall@50 by brand history:\n", by_bucket.round(4).to_string())

# Popularity bias by brand size: do small brands get small creators?
bsize = pd.qcut(brands.drop_duplicates("brand").set_index("brand").followers.rank(method="first"), 5,
                labels=["XS", "S", "M", "L", "XL"])
bias = pd.concat({n: d.assign(size=d.brand.map(bsize)).groupby("size", observed=True).top10_median_followers.median()
                  for n, d in per_brand.items()}, axis=1)
print("\nMedian followers of top-10 recommendations, by brand size:\n", bias.round(0).to_string())

imp = pd.Series(model.booster_.feature_importance("gain"), index=F.FEATURES).sort_values(ascending=False)
print("\nFeature importance (gain, share):\n", (imp / imp.sum()).round(3).to_string())

ARTIFACTS_DIR.mkdir(exist_ok=True)
model.booster_.save_model(str(ARTIFACTS_DIR / f"ranker_{mode}.txt"))
(imp / imp.sum()).rename("gain_share").to_csv(ARTIFACTS_DIR / f"feature_importance_{mode}.csv")
(ARTIFACTS_DIR / f"ranker_{mode}.json").write_text(json.dumps({
    "summary": summary.to_dict(orient="index"),
    "recall50_by_bucket": by_bucket.to_dict(),
    "feature_importance": (imp / imp.sum()).to_dict(),
    "top10_followers_by_brand_size": bias.to_dict(),
}, indent=2))
log("saved")

params = {
    "mode": mode, "train_windows": WINDOWS[mode]["train"], "eval_window": WINDOWS[mode]["eval"],
    "neg_per_brand": NEG_PER_BRAND, "knn_top": KNN_TOP, "svd_top": SVD_TOP, "niche_top": NICHE_TOP,
    "svd_dims": SVD_DIMS, "lgcn_top": LGCN_TOP, **{f"lgcn_{k}": v for k, v in LGCN.items()}, "n_features": len(F.FEATURES), "features": ",".join(F.FEATURES),
    **{f"lgbm_{k}": v for k, v in model.get_params().items()
       if k in ("n_estimators", "learning_rate", "num_leaves", "min_child_samples", "subsample", "colsample_bytree")},
}
with tracking.run(f"ranker {mode}", exp_id=EXP_ID, params=params):
    tracking.log_summary(summary, by_bucket)
    tracking.log_metrics({f"candidate_recall {k}": v for k, v in CANDIDATE_RECALL.items()})
    tracking.log_metrics({f"top10 followers {s}": v for s, v in bias["ranker"].items()}, prefix="ranker/")
    for f in [f"ranker_{mode}.txt", f"ranker_{mode}.json", f"feature_importance_{mode}.csv"]:
        tracking.mlflow.log_artifact(str(ARTIFACTS_DIR / f))
log("logged to MLflow")
