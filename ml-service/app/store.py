"""Read-only access to the exported recommendations (produced by ml/scripts/export_service.py).

Recommendations are computed offline in batch (top-300 per client brand). The service filters and pages them;
it never recomputes the model, which keeps every request fast and deterministic.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

REASON_TEXT = {
    "mentioned_brand": "Mentioned the brand {mentions} time(s) without being paid, last {days_ago} days ago",
    "similar_brands_worked_with": "Brands similar to this one have worked with this creator",
    "same_niche": "Same niche as the brand: {niche}",
    "size_fits_brand": "Audience size matches the creators this brand usually works with",
    "experienced": "Experienced: paid collaborations with {paid_brands_180d} brands in the last 6 months",
    "growing_engagement": "Recent posts perform above the creator's usual level",
    "lookalike": "Ranked highly for similar brands: {brands_text}",
}
# Reasons about the creator itself, valid for any brand (kept when lists of similar brands are fused).
CREATOR_REASONS = {"experienced", "growing_engagement"}
NICHE_SOURCE = "__niche__"   # marks the niche list among the fused sources
RRF_K = 60   # reciprocal rank fusion constant: 1 / (60 + rank); the usual default, damps the very top ranks


def reason_text(r: dict) -> str:
    try:
        if "brands" in r:
            r = {**r, "brands_text": ", ".join("@" + b for b in r["brands"])}
        return REASON_TEXT[r["code"]].format(**r)
    except (KeyError, IndexError):
        return r.get("code", "")


class Store:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.brands = pd.read_parquet(self.data_dir / "brands.parquet").set_index("brand")
        self.creators = pd.read_parquet(self.data_dir / "creators.parquet").set_index("creator_id")
        self.recs = pd.read_parquet(self.data_dir / "recommendations.parquet")
        self.model_info = json.loads((self.data_dir / "model_info.json").read_text())

    # ---------- brands ----------
    def list_brands(self) -> list[dict]:
        return [self._brand(b) for b in self.brands.index]

    def get_brand(self, brand: str) -> dict | None:
        return self._brand(brand) if brand in self.brands.index else None

    def _brand(self, brand: str) -> dict:
        r = self.brands.loc[brand]
        return {"brand": brand, "is_client": bool(r.get("is_client", True)), "followers": int(r.followers),
                "niche": r.niche,
                "creators_mentioning": int(r.creators_hist), "recent_paid_creators": int(r.recent_paid),
                "typical_partner_followers": None if pd.isna(r.typical_partner_followers)
                else int(r.typical_partner_followers)}

    # ---------- creators ----------
    def get_creator(self, creator_id: str) -> dict | None:
        if creator_id not in self.creators.index:
            return None
        r = self.creators.loc[creator_id]
        return {"creator_id": creator_id, "followers": int(r.followers), "size_tier": r.size_tier,
                "niche": None if r.niche in (None, "unknown") else r.niche, "paid_brands_total": int(r.paid_brands_total),
                "paid_brands_180d": int(r.paid_brands_180d),
                "median_rel_engagement": None if pd.isna(r.median_rel_engagement) else float(r.median_rel_engagement),
                "posts_in_data": int(r.posts_in_data), "last_post": r.last_post,
                "recent_brands": list(r.recent_brands) if r.recent_brands is not None else []}

    # ---------- recommendations ----------
    def recommend(self, brand: str, k: int = 20, min_followers: int | None = None, max_followers: int | None = None,
                  niche: str | None = None, exclude: set[str] | None = None) -> list[dict] | None:
        if brand not in self.brands.index:
            return None
        r = self.recs[self.recs.brand == brand].join(self.creators[["followers", "niche"]], on="creator_id")
        return self._page(r, k, min_followers, max_followers, niche, exclude)

    def niche_list(self, niche: str, n: int = 300) -> pd.DataFrame:
        """The most active creators of a niche (paid collaborations in the last 6 months), as a ranked list."""
        c = self.creators[self.creators.niche == niche].sort_values(
            ["paid_brands_180d", "paid_brands_total"], ascending=False).head(n)
        return pd.DataFrame({"brand": NICHE_SOURCE, "creator_id": c.index, "rank": range(1, len(c) + 1),
                             "reasons": json.dumps([{"code": "same_niche", "niche": niche}])})

    def lookalike(self, similar: list[str], k: int = 20, min_followers: int | None = None,
                  max_followers: int | None = None, niche: str | None = None,
                  exclude: set[str] | None = None, brand_niche: str | None = None) -> list[dict] | None:
        """Recommendations for a brand the model has never seen (cold start), from brands it resembles.

        The ranked lists of the similar brands are merged with reciprocal rank fusion: a creator gets
        1 / (60 + rank) from every list it appears in. Only positions are used, so lists whose scores are on
        different scales combine fairly, and creators ranked well for several similar brands come first.
        When the brand's niche is known, the niche's most active creators are fused in as one more list: in the
        cold-start simulation (ml/scripts/cold_start_simulation.py) this kept poorly chosen look-alikes from doing
        worse than the niche alone, and did not hurt well chosen ones.
        """
        known = [b for b in dict.fromkeys(x.lower().lstrip("@") for x in similar) if b in self.brands.index]
        if not known:
            return None
        r = self.recs[self.recs.brand.isin(known)]
        if brand_niche:
            r = pd.concat([r, self.niche_list(brand_niche)], ignore_index=True)
        r = r.assign(rrf=1.0 / (RRF_K + r["rank"]))
        best = r.sort_values("rank").drop_duplicates("creator_id").set_index("creator_id")
        fused = r.groupby("creator_id").agg(score=("rrf", "sum"), sources=("brand", lambda s: sorted(set(s))))

        def explain(c, src):
            brands_ = [b for b in src if b != NICHE_SOURCE]
            out = [{"code": "lookalike", "brands": brands_}] if brands_ else []
            if NICHE_SOURCE in src:
                out.append({"code": "same_niche", "niche": brand_niche})
            return json.dumps(out + [x for x in json.loads(best.at[c, "reasons"]) if x["code"] in CREATOR_REASONS])

        fused["reasons"] = [explain(c, src) for c, src in zip(fused.index, fused.sources)]
        fused = fused.sort_values("score", ascending=False).reset_index()
        fused["rank"] = range(1, len(fused) + 1)
        fused = fused.join(self.creators[["followers", "niche"]], on="creator_id")
        return self._page(fused, k, min_followers, max_followers, niche, exclude)

    def _page(self, r: pd.DataFrame, k: int, min_followers: int | None, max_followers: int | None,
              niche: str | None, exclude: set[str] | None) -> list[dict]:
        if min_followers is not None:
            r = r[r.followers >= min_followers]
        if max_followers is not None:
            r = r[r.followers <= max_followers]
        if niche:
            r = r[r.niche == niche]
        if exclude:
            r = r[~r.creator_id.isin(exclude)]
        out = []
        for row in r.sort_values("rank").head(k).itertuples(index=False):
            reasons = json.loads(row.reasons)
            for x in reasons:
                x["text"] = reason_text(x)
            out.append({"creator_id": row.creator_id, "rank": int(row.rank), "score": round(float(row.score), 4),
                        "reasons": reasons, "creator": self.get_creator(row.creator_id)})
        return out
