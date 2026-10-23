from app import main
from app.llm import LLMUnavailable
from app.outreach import build_facts, check, template

from .conftest import FakeLLM

REQ = {"brand": "glowskin", "creator_id": "c_0000000000",
       "campaign": {"name": "Summer Glow", "brief": "Launch of a vitamin C serum for summer.",
                    "start_date": "2019-06-01", "end_date": "2019-07-15"},
       "sender": {"name": "Marina", "company": "MEMS Agency", "email": "marina@mems.example.com"}}

GOOD = {"subject": "Summer Glow with @glowskin",
        "body": "Hi there,\n\nYou have already featured @glowskin in your posts, so we'd love to invite you to "
                "Summer Glow, our launch of a vitamin C serum, running from June 1 to July 15. "
                "Would you be open to a paid collaboration?\n\nBest,\nMarina\nMEMS Agency"}


def facts():
    brand = {"brand": "glowskin", "niche": "beauty & makeup"}
    creator = {"niche": "beauty & makeup", "size_tier": "nano", "recent_brands": ["otherbrand"]}
    return build_facts(brand, creator, [{"code": "mentioned_brand"}], REQ["campaign"], REQ["sender"])


def test_good_draft_passes_checks():
    assert check(GOOD, facts()) == []


def test_checks_catch_invented_facts():
    f = facts()
    bad = {"subject": "Hi", "body": "We pay $500 per post to 3 creators, see [link]. Also @randombrand loves you."}
    issues = " | ".join(check(bad, f))
    for needle in ["brand @glowskin", "campaign name", "numbers that are not in the facts: 3, 500",
                   "money", "handles that are not in the facts: @randombrand", "placeholder"]:
        assert needle in issues


def test_template_always_passes():
    assert check(template(facts()), facts()) == []


def test_llm_draft_used_when_it_passes(client, monkeypatch):
    llm = FakeLLM(GOOD)
    monkeypatch.setattr(main, "make_client", lambda s: llm)
    r = client.post("/outreach/draft", json=REQ).json()
    assert r["provider"] == "fake" and r["checks"]["passed"] and r["subject"] == GOOD["subject"]


def test_llm_gets_feedback_and_retries(client, monkeypatch):
    bad = {"subject": "Hello", "body": "Join our campaign for $100!"}
    llm = FakeLLM(bad, GOOD)
    monkeypatch.setattr(main, "make_client", lambda s: llm)
    r = client.post("/outreach/draft", json=REQ).json()
    assert r["provider"] == "fake" and len(r["checks"]["attempts"]) == 2
    assert "mentions money" in llm.calls[1]


def test_falls_back_to_template_after_two_failures(client, monkeypatch):
    bad = {"subject": "Hello", "body": "Join our campaign for $100!"}
    monkeypatch.setattr(main, "make_client", lambda s: FakeLLM(bad, bad))
    r = client.post("/outreach/draft", json=REQ).json()
    assert r["provider"] == "template" and r["checks"]["passed"]
    assert r["fallback_reason"] == "LLM draft failed the checks twice"


def test_falls_back_when_llm_unavailable(client, monkeypatch):
    monkeypatch.setattr(main, "make_client", lambda s: FakeLLM(LLMUnavailable("Ollama not reachable")))
    r = client.post("/outreach/draft", json=REQ).json()
    assert r["provider"] == "template" and "Ollama not reachable" in r["fallback_reason"]
    assert "@glowskin" in r["body"] and "Summer Glow" in r["body"]


def test_unparseable_output_is_retried(client, monkeypatch):
    monkeypatch.setattr(main, "make_client", lambda s: FakeLLM("sorry, here you go", GOOD))
    r = client.post("/outreach/draft", json=REQ).json()
    assert r["provider"] == "fake" and r["checks"]["passed"]


def test_draft_validation(client):
    assert client.post("/outreach/draft", json={**REQ, "creator_id": "c_x"}).status_code == 404
    assert client.post("/outreach/draft", json={**REQ, "campaign": {"name": ""}}).status_code == 422
