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
}


def reason_text(r: dict) -> str:
    try:
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
        return {"brand": brand, "followers": int(r.followers), "niche": r.niche,
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
