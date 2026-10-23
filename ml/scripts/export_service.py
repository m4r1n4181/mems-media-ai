"""Train the final model on ALL data and export what ml-service needs.

"Today" for the app is the end of the data (AS_OF = 2019-05-01). The ranker is trained on the two most recent
windows (Oct–Dec 2018 and Jan–Apr 2019), then ranks candidates for a set of client brands using the full history.

Besides the client brands the app starts with, the most active other brands are exported too (300 in total):
a new client that is one of them gets the model's own recommendations, and a brand the model has never seen
can be matched to them as "similar brands" (cold start, see ml-service).

Outputs (default: ../ml-service/data, never committed):
  brands.parquet           known brands (is_client marks the 39 the app seeds) with niche and size profile
  creators.parquet         every recommended creator: size, niche, experience, engagement, past brands
  recommendations.parquet  top-300 creators per client brand with score, rank and reasons
  model_info.json          model version, as-of date, training windows, test metrics

    python scripts/export_service.py [output_dir]
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd

from mlrec import features as F
from mlrec import niches as N
from mlrec import pipeline as P
from mlrec import ranker as R
from mlrec.data import load_posts, to_interactions
from mlrec.split import make_task

AS_OF = "2019-05-01"
TRAIN_WINDOWS = [("2018-10-01", "2019-01-01"), ("2019-01-01", AS_OF)]
N_CLIENTS_PER_NICHE = 5
N_KNOWN_BRANDS = 300   # clients + the most active other brands
TOP_K = 300
MODEL_VERSION = "r7-final-2019-05-01"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "ml-service" / "data"


def log(msg, t0=[time.time()]):
    print(f"[{time.time() - t0[0]:6.0f}s] {msg}", flush=True)


posts, creators, brands = load_posts()
inter = to_interactions(posts, brands)
log("data loaded")

# ---------- 1. train the final ranker on the two most recent windows ----------
parts = []
for w in TRAIN_WINDOWS:
    task = make_task(inter, *w)
    df, _ = P.prepare(task, sorted(task.positives.brand.unique()), posts, creators, brands, train=True, log=log)
    parts.append(df.assign(brand=df.brand + "@" + w[0]))
    log(f"{w}: {len(df):,} training rows")
model = R.train(pd.concat(parts).sort_values("brand").reset_index(drop=True))
del parts
log("final ranker trained")

# ---------- 2. pick client brands at AS_OF ----------
now = make_task(inter, AS_OF, "2019-06-01")          # history = everything before AS_OF, no future labels
h = now.history
recent_paid = (h[(h.sponsored == 1) & (h.ts >= now.cutoff - pd.Timedelta(days=180))]
               .drop_duplicates(["brand", "creator_id"]).groupby("brand").size())
creators_hist = h.groupby("brand").creator_id.nunique()
posts_hist = posts[posts.ts < now.cutoff]
W, Bn = F.niche_vectors(now, posts_hist, set(brands.brand))
brand_niche = Bn.idxmax(axis=1)
brand_strength = Bn.max(axis=1)
profile = brands.drop_duplicates("brand").set_index("brand")
eligible = (pd.DataFrame({"recent_paid": recent_paid, "creators_hist": creators_hist,
                          "niche": brand_niche, "niche_strength": brand_strength})
            .join(profile[["followers"]]).dropna())
eligible = eligible[(eligible.recent_paid >= 5) & (eligible.niche_strength >= 0.3) & (eligible.followers > 0)
                    & (~eligible.niche.isin([0, 9]))]   # skip the two leftover topics
clients = (eligible.sort_values("recent_paid", ascending=False).groupby("niche").head(N_CLIENTS_PER_NICHE))
client_list = sorted(clients.index)
log(f"{len(client_list)} client brands across {clients.niche.nunique()} niches")
# other well-known brands: most collaborations in the last 6 months (any niche)
active = (pd.DataFrame({"recent_paid": recent_paid, "creators_hist": creators_hist,
                        "niche": brand_niche, "niche_strength": brand_strength})
          .join(profile[["followers"]]).dropna())
active = active[(active.recent_paid >= 5) & (active.followers > 0) & (~active.index.isin(client_list))]
others = active.sort_values("recent_paid", ascending=False).head(N_KNOWN_BRANDS - len(client_list))
known = pd.concat([clients.assign(is_client=True), others.assign(is_client=False)])
known_list = sorted(known.index)
log(f"{len(known_list)} known brands ({len(client_list)} clients)")

# ---------- 3. rank candidates for every known brand ----------
cand, ctx = P.prepare(now, known_list, posts, creators, brands, train=False, log=log)
cand["score"] = model.predict(cand[F.FEATURES])
cand = cand.sort_values(["brand", "score"], ascending=[True, False])
cand["rank"] = cand.groupby("brand").cumcount() + 1
recs = cand[cand["rank"] <= TOP_K].copy()
log(f"{len(recs):,} recommendations")

# ---------- 4. human-readable reasons from the features the model used ----------
cn = W.idxmax(axis=1)
recs["creator_niche"] = recs.creator_id.map(cn)
recs["brand_niche"] = recs.brand.map(brand_niche)


def reasons(r):
    out = []
    if r.org_mentions > 0:
        out.append({"code": "mentioned_brand", "mentions": int(r.org_mentions),
                    "days_ago": int(r.days_since_org_mention)})
    if r.lgcn_rank <= 50 or r.knn_rank <= 50:
        out.append({"code": "similar_brands_worked_with"})
    if pd.notna(r.creator_niche) and r.creator_niche == r.brand_niche:
        out.append({"code": "same_niche", "niche": N.NICHE_NAMES[int(r.creator_niche)]})
    if pd.notna(r.size_gap) and r.size_gap < 0.7:
        out.append({"code": "size_fits_brand"})
    if r.paid_brands_180d >= 3:
        out.append({"code": "experienced", "paid_brands_180d": int(r.paid_brands_180d)})
    if pd.notna(r.median_rel_eng) and r.median_rel_eng > 0.05:
        out.append({"code": "growing_engagement"})
    return json.dumps(out[:4])


recs["reasons"] = recs.apply(reasons, axis=1)

# ---------- 5. creator and brand tables ----------
rec_creators = recs.creator_id.unique()
cs = ctx["feature_builder"].creator_stats.reindex(rec_creators)
paid_hist = h[h.sponsored == 1].sort_values("ts", ascending=False).drop_duplicates(["creator_id", "brand"])
past_brands = paid_hist.groupby("creator_id").brand.apply(lambda s: list(s.head(5)))
last_post = posts_hist.groupby("creator_id").ts.max()
cr = creators.drop_duplicates("creator_id").set_index("creator_id").reindex(rec_creators)


def tier(f):
    return ("nano" if f < 10_000 else "micro" if f < 50_000 else "mid" if f < 250_000
            else "macro" if f < 1_000_000 else "mega")


creator_table = pd.DataFrame({
    "creator_id": rec_creators,
    "followers": cr.followers.fillna(0).astype(int).values,
    "niche": [N.NICHE_NAMES.get(int(n), "general lifestyle") if pd.notna(n) else "unknown"
              for n in cn.reindex(rec_creators)],
    "paid_brands_total": cs.paid_brands_total.fillna(0).astype(int).values,
    "paid_brands_180d": cs.paid_brands_180d.fillna(0).astype(int).values,
    "median_rel_engagement": cs.median_rel_eng.round(3).values,
    "posts_in_data": cs.posts_hist.fillna(0).astype(int).values,
    "last_post": last_post.reindex(rec_creators).dt.date.astype(str).values,
    "recent_brands": [past_brands.get(c, []) for c in rec_creators],
})
creator_table["size_tier"] = creator_table.followers.map(tier)

brand_table = known.reset_index().rename(columns={"index": "brand"})
brand_table["niche"] = brand_table.niche.map(lambda n: N.NICHE_NAMES[int(n)])
fb = ctx["feature_builder"]
brand_table["typical_partner_followers"] = (np.expm1(fb.brand_stats.brand_partner_size.reindex(brand_table.brand))
                                            .round(-2).values)
brand_table = brand_table[["brand", "is_client", "followers", "niche", "niche_strength", "creators_hist",
                           "recent_paid", "typical_partner_followers"]]
brand_table["followers"] = brand_table.followers.astype(int)

rec_table = recs[["brand", "creator_id", "rank", "score", "reasons"]].reset_index(drop=True)

OUT.mkdir(parents=True, exist_ok=True)
brand_table.to_parquet(OUT / "brands.parquet", index=False)
creator_table.to_parquet(OUT / "creators.parquet", index=False)
rec_table.to_parquet(OUT / "recommendations.parquet", index=False)
test = json.loads((ROOT / "results" / "ranker_test.json").read_text())["summary"]["ranker"]
(OUT / "model_info.json").write_text(json.dumps({
    "model_version": MODEL_VERSION, "as_of": AS_OF, "train_windows": TRAIN_WINDOWS,
    "client_brands": int(brand_table.is_client.sum()), "known_brands": len(brand_table),
    "recommendations_per_brand": TOP_K,
    "test_metrics": {k: round(v, 4) for k, v in test.items()},
}, indent=2))
log(f"exported to {OUT}")
