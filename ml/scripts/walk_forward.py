"""Walk-forward (time-series) cross-validation of the ranker.

Each fold trains only on data before its evaluation window, so the model never sees the future:
    fold1: train Jan–Jun 2018 -> evaluate Jul–Sep 2018
    val:   train Apr–Sep 2018 -> evaluate Oct–Dec 2018
The test window (Jan–Apr 2019) is NOT part of this. Usage:  python scripts/walk_forward.py [exp_id]
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from mlrec import tracking
from mlrec.config import ARTIFACTS_DIR

FOLDS = ["fold1", "val"]
exp_id = sys.argv[1] if len(sys.argv) > 1 else "WF"

for fold in FOLDS:
    print(f"=== fold {fold} ===", flush=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "train_ranker.py"), fold, "300", f"{exp_id}-{fold}"],
                   check=True)

rows = []
for fold in FOLDS:
    summary = json.loads((ARTIFACTS_DIR / f"ranker_{fold}.json").read_text())["summary"]
    for model, metrics in summary.items():
        rows.append({"fold": fold, "model": model, **metrics})
df = pd.DataFrame(rows)
metrics = ["recall@10", "recall@50", "recall@100", "ndcg@50"]
agg = df.groupby("model")[metrics].agg(["mean", "std"]).round(4)
print("\nWalk-forward results (mean and std over folds):\n", agg.to_string())

wide = df.pivot(index="fold", columns="model", values="recall@50")
wins = (wide["ranker"] > wide["organic only"]).all()
print("\nRecall@50 per fold:\n", wide.round(4).to_string())
print(f"\nRanker beats the heuristic in every fold: {wins}")

out = {"per_fold": df.to_dict(orient="records"), "ranker_beats_heuristic_every_fold": bool(wins)}
(ARTIFACTS_DIR / "walk_forward.json").write_text(json.dumps(out, indent=2))
with tracking.run("walk-forward", exp_id=exp_id, params={"folds": ",".join(FOLDS)}):
    for model in agg.index:
        for m in metrics:
            tracking.log_metrics({f"{m} mean": agg.loc[model, (m, "mean")], f"{m} std": agg.loc[model, (m, "std")]},
                                 prefix=f"{model}/")
    tracking.mlflow.log_artifact(str(ARTIFACTS_DIR / "walk_forward.json"))
