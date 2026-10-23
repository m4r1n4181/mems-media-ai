"""Cold-start simulation: how good are look-alike recommendations for a brand the model has never seen?

On the validation window, every brand with new partners is treated as if it were new: its own ranking is not
used. Instead, the ranked lists of 3 "similar" brands are fused with reciprocal rank fusion, exactly as
ml-service does for a new client (score = sum of 1 / (60 + rank)). The similar brands are chosen only among the
300 brands the app knows (the most active ones), like the picker in the app, in three ways that mimic managers:

  behaviour   the 3 known brands whose past creators overlap most with this brand's (a well-informed manager)
  niche+size  3 known brands from the same niche with the closest follower count (a manager who knows the market)
  random      3 random known brands (control: is any of this better than luck?)

References: the warm model (the brand's own R7 ranking: the ceiling) and a niche heuristic without look-alikes
(the most active creators of the brand's niche).

    python scripts/train_ranker.py val 300 R7 --save-top     # first: per-brand rankings (~25 min)
    python scripts/cold_start_simulation.py                  # ~3 min; writes results/cold_start_val.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd

from mlrec import baselines as B
from mlrec import features as F
from mlrec.config import ARTIFACTS_DIR
from mlrec.data import load_posts, to_interactions
from mlrec.split import make_task

WINDOW = ("2018-10-01", "2019-01-01")
N_KNOWN, N_SIMILAR, K, RRF_K, SEED = 300, 3, 50, 60, 0
RESULTS = Path(__file__).resolve().parents[1] / "results"

posts, creators, brands = load_posts()
task = make_task(to_interactions(posts, brands), *WINDOW)
h, pos = task.history, task.positives
rankings = pd.read_parquet(ARTIFACTS_DIR / "rankings_val.parquet")
truth = pos.groupby("brand").creator_id.apply(set)
known_pairs = pd.DataFrame(list(task.known_pairs), columns=["brand", "creator_id"]).groupby("brand").creator_id.apply(set)

# The brands the app "knows": most collaborations in the 6 months before the cutoff, among brands with a ranking.
recent_paid = (h[(h.sponsored == 1) & (h.ts >= task.cutoff - pd.Timedelta(days=180))]
               .drop_duplicates(["brand", "creator_id"]).groupby("brand").size())
ranked_brands = set(rankings.brand)
known = recent_paid[recent_paid.index.isin(ranked_brands)].sort_values(ascending=False).head(N_KNOWN).index.tolist()
lists = {b: g.sort_values("rank").creator_id.tolist() for b, g in rankings[rankings.brand.isin(known)].groupby("brand")}
own_lists = rankings.sort_values("rank").groupby("brand").creator_id.apply(list)

# brand-brand similarity from shared creators (cosine on the brand x creator matrix of the history)
targets = sorted(set(truth.index) & ranked_brands)
idx = B.Index(task, targets)
M = B.interaction_matrix(task, idx)
norms = np.sqrt(np.asarray(M.multiply(M).sum(axis=1)).ravel()) + 1e-9
known_rows = idx.b_pos[known].values
Mk = M[known_rows]

# niche (NMF topic) and size of every brand at the cutoff
W, Bn = F.niche_vectors(task, posts[posts.ts < task.cutoff], set(brands.brand))
niche = Bn.idxmax(axis=1)
log_followers = np.log1p(brands.drop_duplicates("brand").set_index("brand").followers)
known_df = pd.DataFrame({"niche": niche.reindex(known), "lf": log_followers.reindex(known)}, index=known)

# niche heuristic: most active creators of each niche
paid180 = h[(h.sponsored == 1) & (h.ts >= task.cutoff - pd.Timedelta(days=180))]
activity = paid180.drop_duplicates(["brand", "creator_id"]).groupby("creator_id").size()
creator_niche = W.idxmax(axis=1)
by_niche = {n: activity.reindex(g.index).dropna().sort_values(ascending=False).index.tolist()
            for n, g in creator_niche.groupby(creator_niche)}

rng = np.random.default_rng(SEED)


def fuse(similar: list[str], exclude: set) -> list[str]:
    score: dict[str, float] = {}
    for b in similar:
        for r, c in enumerate(lists[b], start=1):
            score[c] = score.get(c, 0.0) + 1.0 / (RRF_K + r)
    return [c for c, _ in sorted(score.items(), key=lambda x: -x[1]) if c not in exclude]


def recall(ranked: list[str], target: str) -> float:
    return len(set(ranked[:K]) & truth[target]) / len(truth[target])


rows, sensitivity_rows = [], []
for t in targets:
    exclude = known_pairs.get(t, set())
    pool = [b for b in known if b != t]
    # behaviour look-alikes
    sims = (Mk @ M[idx.b_pos[t]].T).toarray().ravel() / (norms[known_rows] * norms[idx.b_pos[t]])
    order = [known[i] for i in np.argsort(-sims) if known[i] != t]
    behaviour = order[:N_SIMILAR]
    # niche + size look-alikes (fall back to closest size overall when the niche has too few known brands)
    cand = known_df.drop(index=t, errors="ignore")
    same = cand[cand.niche == niche.get(t)] if t in niche.index else cand.iloc[0:0]
    if len(same) < N_SIMILAR:
        same = cand
    tlf = log_followers.get(t, cand.lf.median())
    niche_size = (same.lf - tlf).abs().sort_values().index[:N_SIMILAR].tolist()
    random3 = list(rng.choice(pool, N_SIMILAR, replace=False))
    niche_only = [c for c in by_niche.get(niche.get(t), []) if c not in exclude]
    # sensitivity: how many similar brands to ask for, and look-alikes + the niche list fused together
    extra = {}
    for n in (1, 5, 10):
        extra[f"behaviour, {n} brands"] = recall(fuse(order[:n], exclude), t)
        extra[f"niche + size, {n} brands"] = recall(fuse((same.lf - tlf).abs().sort_values().index[:n].tolist(), exclude), t)
    lists["__niche__"] = niche_only[:300]
    extra["niche + size look-alikes + niche list"] = recall(fuse(niche_size + ["__niche__"], exclude), t)
    extra["behaviour look-alikes + niche list"] = recall(fuse(behaviour + ["__niche__"], exclude), t)
    sensitivity_rows.append(extra)
    rows.append({
        "brand": t, "n_pos": len(truth[t]),
        "history_creators": int(M[idx.b_pos[t]].nnz),
        "warm model (own history)": recall([c for c in own_lists[t] if c not in exclude], t),
        "look-alikes: behaviour": recall(fuse(behaviour, exclude), t),
        "look-alikes: niche + size": recall(fuse(niche_size, exclude), t),
        "look-alikes: random": recall(fuse(random3, exclude), t),
        "niche heuristic (no look-alikes)": recall(niche_only, t),
    })

df = pd.DataFrame(rows)
methods = [c for c in df.columns if c not in ("brand", "n_pos", "history_creators")]
df["history"] = pd.cut(df.history_creators, [-1, 9, 99, 10**9], labels=["1-9", "10-99", "100+"])
summary = {
    "window": WINDOW, "brands": len(df), "known_brands": len(known), "similar_brands": N_SIMILAR, "k": K,
    f"recall@{K}": df[methods].mean().round(4).to_dict(),
    f"recall@{K}_by_history": df.groupby("history", observed=True)[methods].mean().round(4).to_dict(orient="index"),
}
summary["sensitivity"] = pd.DataFrame(sensitivity_rows).mean().round(4).to_dict()
(RESULTS / "cold_start_val.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
