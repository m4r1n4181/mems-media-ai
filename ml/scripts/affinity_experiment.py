"""Experiment A1: niche affinity pool vs the old niche pool, measured by candidate recall on validation.

Variants (all on the validation window, test untouched):
  current                        organic + kNN + niche pool + SVD + LightGCN (the final model's candidates)
  + affinity (hashtags)          current + affinity pool, creator niches from hashtags only
  + affinity (hashtags + bio)    current + affinity pool, creator niches from hashtags and profile bios
  affinity instead of niche      the old niche pool replaced by the affinity pool (hashtags + bio), same budget

    python scripts/affinity_experiment.py      # ~10 min; writes results/affinity_val.json
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd

from mlrec import affinity as A
from mlrec import baselines as B
from mlrec import candidates as C
from mlrec import features as F
from mlrec.config import DATA_DIR
from mlrec.data import load_posts, to_interactions
from mlrec.lightgcn import LightGCN
from mlrec.pipeline import DEFAULTS
from mlrec.split import make_task

WINDOW = ("2018-10-01", "2019-01-01")
RESULTS = Path(__file__).resolve().parents[1] / "results"
T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:6.0f}s] {msg}", flush=True)


posts, creators, brands = load_posts()
inter = to_interactions(posts, brands)
task = make_task(inter, *WINDOW)
pos = task.positives
eval_brands = sorted(pos.brand.unique())
posts_hist = posts[posts.ts < task.cutoff]

cfg = DEFAULTS
idx = B.Index(task, eval_brands)
W, Bn = F.niche_vectors(task, posts_hist, set(brands.brand))
svd = C.SVDEmbeddings(cfg["svd_dims"]).fit(task, idx)
lgcn = LightGCN(verbose=False, **cfg["lgcn"]).fit(task, idx)
knn = B.BrandKNN().fit(task, idx)
log("candidate models fitted")

bio = A.load_bio_niches(DATA_DIR)
if bio is None:
    sys.exit("bio_niches.csv not found next to the data: run scripts/extract_bio_niches.py first")
aff_sets = {}
for name, b in [("hashtags", None), ("hashtags+bio", bio)]:
    mix = A.creator_mix(posts_hist, b)
    aff = A.brand_affinity(task, mix)
    aff_sets[name] = (mix, aff, A.ranked_creators(task, mix))
    log(f"affinity ({name}): {len(mix):,} creators with a niche mix, {len(aff):,} brands with an affinity")

VARIANTS = {
    "current": {"niche": True, "affinity": None},
    "+ affinity (hashtags)": {"niche": True, "affinity": "hashtags"},
    "+ affinity (hashtags + bio)": {"niche": True, "affinity": "hashtags+bio"},
    "affinity instead of niche pool": {"niche": False, "affinity": "hashtags+bio"},
}
hits = {v: 0 for v in VARIANTS}
n_cand = {v: 0 for v in VARIANTS}
pos_idx = pd.MultiIndex.from_frame(pos[["brand", "creator_id"]])
for start in range(0, len(eval_brands), 400):
    names = eval_brands[start:start + 400]
    base = [svd.top_pairs(idx, names, cfg["svd_top"]), lgcn.top_pairs(idx, names, cfg["lgcn_top"])]
    niche = C.niche_pool(task, names, W, Bn, per_niche=cfg["niche_top"])
    pools = {k: A.affinity_pool(names, v[1], v[2], slots=cfg["niche_top"]) for k, v in aff_sets.items()}
    for v, spec in VARIANTS.items():
        extra = base + ([niche] if spec["niche"] else []) + ([pools[spec["affinity"]]] if spec["affinity"] else [])
        cand = C.generate(task, idx, names, knn_top=cfg["knn_top"], extra=pd.concat(extra), knn=knn)
        n_cand[v] += len(cand)
        hits[v] += len(pd.MultiIndex.from_frame(cand[["brand", "creator_id"]]).intersection(pos_idx))
    log(f"{min(start + 400, len(eval_brands))}/{len(eval_brands)} brands")

out = {v: {"candidate_recall": hits[v] / len(pos), "candidates_per_brand": n_cand[v] / len(eval_brands)}
       for v in VARIANTS}
mix_bio, _, _ = aff_sets["hashtags+bio"]
mix_tags, _, _ = aff_sets["hashtags"]
out["coverage"] = {
    "new partners whose creator has a niche mix (hashtags)": float(pos.creator_id.isin(mix_tags.index).mean()),
    "new partners whose creator has a niche mix (hashtags + bio)": float(pos.creator_id.isin(mix_bio.index).mean()),
}
(RESULTS / "affinity_val.json").write_text(json.dumps(out, indent=2))
for v in VARIANTS:
    log(f"{v:32s} candidate recall {out[v]['candidate_recall']:.3f}  ({out[v]['candidates_per_brand']:.0f} per brand)")
log(json.dumps(out["coverage"]))
