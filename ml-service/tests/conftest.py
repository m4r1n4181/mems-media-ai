import json
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture()
def data_dir(tmp_path):
    """A tiny synthetic export with the same schema as ml/scripts/export_service.py (no real data)."""
    pd.DataFrame([
        {"brand": "glowskin", "followers": 52000, "niche": "beauty & makeup", "niche_strength": 0.5,
         "creators_hist": 120, "recent_paid": 14, "typical_partner_followers": 23000.0},
        {"brand": "fitfuel", "followers": 8000, "niche": "fitness", "niche_strength": 0.6,
         "creators_hist": 40, "recent_paid": 6, "typical_partner_followers": None},
    ]).to_parquet(tmp_path / "brands.parquet", index=False)
    pd.DataFrame([
        {"creator_id": f"c_{i:010d}", "followers": f, "niche": n, "paid_brands_total": 4, "paid_brands_180d": 3,
         "median_rel_engagement": 0.1, "posts_in_data": 50, "last_post": "2019-04-20",
         "recent_brands": ["glowskin", "otherbrand"], "size_tier": t}
        for i, (f, n, t) in enumerate([(9000, "beauty & makeup", "nano"), (30000, "beauty & makeup", "micro"),
                                       (400000, "fitness", "macro")])
    ]).to_parquet(tmp_path / "creators.parquet", index=False)
    reasons = json.dumps([{"code": "mentioned_brand", "mentions": 2, "days_ago": 12},
                          {"code": "same_niche", "niche": "beauty & makeup"}])
    pd.DataFrame([
        {"brand": "glowskin", "creator_id": "c_0000000000", "rank": 1, "score": 2.5, "reasons": reasons},
        {"brand": "glowskin", "creator_id": "c_0000000001", "rank": 2, "score": 1.9, "reasons": "[]"},
        {"brand": "glowskin", "creator_id": "c_0000000002", "rank": 3, "score": 1.1, "reasons": "[]"},
        {"brand": "fitfuel", "creator_id": "c_0000000002", "rank": 1, "score": 3.0, "reasons": "[]"},
    ]).to_parquet(tmp_path / "recommendations.parquet", index=False)
    (tmp_path / "model_info.json").write_text(json.dumps({"model_version": "test", "as_of": "2019-05-01"}))
    return tmp_path


@pytest.fixture()
def client(data_dir, monkeypatch):
    from fastapi.testclient import TestClient

    from app import main
    from app.store import Store
    monkeypatch.setattr(main, "_store", Store(data_dir))
    monkeypatch.setattr(main, "make_client", lambda s: None)   # no LLM unless a test installs one
    return TestClient(main.app)


class FakeLLM:
    name, model = "fake", "fake-1"

    def __init__(self, *responses):
        self.responses, self.calls = list(responses), []

    def chat(self, system, user):
        self.calls.append(user)
        r = self.responses.pop(0)
        if isinstance(r, Exception):
            raise r
        return r if isinstance(r, str) else json.dumps(r)
