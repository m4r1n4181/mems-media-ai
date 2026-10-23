"""ml-service: creator recommendations and AI-drafted outreach e-mails for the MEMS marketing app.

Run:  uvicorn app.main:app --port 8000      (docs at http://localhost:8000/docs)
"""
from __future__ import annotations

from datetime import date

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from .config import settings
from .llm import LLMUnavailable, make_client
from .outreach import build_facts, draft_email
from .store import Store

app = FastAPI(title="MEMS ml-service", version="1.0",
              description="Creator recommendations (two-stage recommender, offline batch) and outreach e-mail drafts.")
_store: Store | None = None


def store() -> Store:
    global _store
    if _store is None:
        try:
            _store = Store(settings.data_dir)
        except FileNotFoundError as e:
            raise HTTPException(503, f"Model data not found in {settings.data_dir}. "
                                     "Run ml/scripts/export_service.py first.") from e
    return _store


# ---------- health ----------
@app.get("/health")
def health():
    client = make_client(settings)
    llm = {"provider": settings.llm_provider, "model": None, "available": False}
    if client is not None:
        try:
            llm["model"] = client.resolve_model() if hasattr(client, "resolve_model") else getattr(client, "model", None)
            llm["available"] = True
        except LLMUnavailable as e:
            llm["error"] = str(e)
    try:
        s = store()
        data = {"loaded": True, "client_brands": len(s.brands), "model_version": s.model_info["model_version"]}
    except HTTPException as e:
        data = {"loaded": False, "error": e.detail}
    return {"status": "ok" if data["loaded"] else "degraded", "data": data, "llm": llm}


@app.get("/model-info")
def model_info():
    return store().model_info


# ---------- brands and creators ----------
@app.get("/brands")
def brands():
    return store().list_brands()


@app.get("/brands/{brand}")
def brand(brand: str):
    b = store().get_brand(brand.lower())
    if b is None:
        raise HTTPException(404, f"Unknown client brand '{brand}'")
    return b


@app.get("/brands/{brand}/recommendations")
def recommendations(brand: str, k: int = Query(20, ge=1, le=300),
                    min_followers: int | None = Query(None, ge=0), max_followers: int | None = Query(None, ge=0),
                    niche: str | None = None, exclude: str | None = Query(None, description="comma-separated creator ids")):
    s = store()
    items = s.recommend(brand.lower(), k, min_followers, max_followers, niche,
                        set(exclude.split(",")) if exclude else None)
    if items is None:
        raise HTTPException(404, f"Unknown client brand '{brand}'")
    return {"brand": brand.lower(), "model_version": s.model_info["model_version"], "as_of": s.model_info["as_of"],
            "items": items}


class LookalikeRequest(BaseModel):
    similar_brands: list[str] = Field(min_length=1, max_length=5)
    k: int = Field(20, ge=1, le=300)
    min_followers: int | None = Field(None, ge=0)
    max_followers: int | None = Field(None, ge=0)
    niche: str | None = None          # filter: only creators of this niche
    exclude: list[str] = Field(default_factory=list)
    brand_niche: str | None = None    # the new brand's own niche: its most active creators are fused in


@app.post("/lookalike/recommendations")
def lookalike_recommendations(req: LookalikeRequest):
    """Cold start: recommendations for a new brand, fused from the lists of brands it resembles."""
    s = store()
    items = s.lookalike(req.similar_brands, req.k, req.min_followers, req.max_followers, req.niche,
                        set(req.exclude) or None, brand_niche=req.brand_niche)
    if items is None:
        raise HTTPException(422, "None of the similar brands is known to the model")
    return {"similar_brands": [b.lower().lstrip("@") for b in req.similar_brands],
            "model_version": s.model_info["model_version"], "as_of": s.model_info["as_of"], "items": items}


@app.get("/creators/{creator_id}")
def creator(creator_id: str):
    c = store().get_creator(creator_id)
    if c is None:
        raise HTTPException(404, f"Unknown creator '{creator_id}'")
    return c


# ---------- outreach ----------
class Campaign(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    brief: str | None = Field(None, max_length=2000)
    start_date: date | None = None
    end_date: date | None = None


class Sender(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    company: str | None = Field(None, max_length=120)
    email: str | None = Field(None, max_length=200)


class DraftRequest(BaseModel):
    brand: str
    creator_id: str
    campaign: Campaign
    sender: Sender
    # for a brand the model does not know (cold start): what the manager told us about it
    brand_niche: str | None = None
    similar_brands: list[str] | None = Field(None, max_length=5)


@app.post("/outreach/draft")
def outreach_draft(req: DraftRequest):
    s = store()
    b = s.get_brand(req.brand.lower())
    c = s.get_creator(req.creator_id)
    if c is None:
        raise HTTPException(404, "Unknown creator")
    if b is not None:
        rec = s.recommend(b["brand"], k=300, exclude=None) or []
    elif req.similar_brands:
        b = {"brand": req.brand.lower().lstrip("@"), "niche": req.brand_niche}
        rec = s.lookalike(req.similar_brands, k=300, brand_niche=req.brand_niche) or []
    else:
        raise HTTPException(404, "Unknown brand: send similar_brands for a brand the model does not know")
    reasons = next((r["reasons"] for r in rec if r["creator_id"] == req.creator_id), [])
    facts = build_facts(b, c, reasons, req.campaign.model_dump(mode="json"), req.sender.model_dump())
    return draft_email(make_client(settings), facts)
