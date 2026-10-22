"""Evaluate baselines on the validation window. Usage: python scripts/run_baselines.py [val|test]"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd

from mlrec import baselines as B
from mlrec.config import ARTIFACTS_DIR
from mlrec.data import load
from mlrec.evaluate import evaluate, summarize
from mlrec.split import make_task

SPLITS = {"val": ("2018-10-01", "2019-01-01"), "test": ("2019-01-01", "2019-05-01")}

split = sys.argv[1] if len(sys.argv) > 1 else "val"
t0 = time.time()
inter, creators, brands = load()
task = make_task(inter, *SPLITS[split])
task.known_pairs_by_brand = {}
for b, c in task.known_pairs:
    task.known_pairs_by_brand.setdefault(b, []).append(c)
eval_brands = sorted(task.positives.brand.unique())
idx = B.Index(task, eval_brands)
followers = creators.set_index("creator_id").followers
print(f"[{split}] eval brands={len(eval_brands)} positives={len(task.positives)} candidates={len(idx.creators)} "
      f"load={time.time()-t0:.0f}s")

models = {
    "popularity (all time)": B.Popularity(),
    "popularity (last 180d)": B.Popularity(recent_days=180),
    "organic mentions": B.OrganicMentions(),
    "brand kNN": B.BrandKNN(),
}
per_brand = {}
for name, model in models.items():
    t = time.time()
    per_brand[name] = evaluate(task, idx, model.fit(task, idx), followers)
    print(f"  {name}: {time.time()-t:.0f}s")

summary = summarize(per_brand)
print("\nOverall (mean over brands):\n", summary.to_string())
by_bucket = pd.concat({n: d.groupby("bucket", observed=True)["recall@50"].mean() for n, d in per_brand.items()}, axis=1).round(4)
counts = per_brand[next(iter(per_brand))].bucket.value_counts().sort_index()
print("\nRecall@50 by brand history (distinct creators before cutoff):\n", by_bucket.assign(n_brands=counts).to_string())

ARTIFACTS_DIR.mkdir(exist_ok=True)
(ARTIFACTS_DIR / f"baselines_{split}.json").write_text(json.dumps(
    {"summary": summary.to_dict(orient="index"), "recall50_by_bucket": by_bucket.to_dict()}, indent=2))
