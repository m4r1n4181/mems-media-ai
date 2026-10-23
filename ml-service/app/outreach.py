"""AI-drafted outreach e-mails with automatic faithfulness checks.

The model only rewrites FACTS we already have (brand, campaign brief, the creator's niche, size and past
collaborations, why the recommender picked them) into a friendly e-mail. A draft is accepted only if it passes
deterministic checks: no invented numbers, money, @handles or placeholders, and it names the brand and campaign.
If the first draft fails, the model gets the list of problems and one more try; after that, or when no model is
available, a template e-mail is used, and the response says so.
"""
from __future__ import annotations

import json
import re

from .llm import LLMUnavailable

MAX_WORDS = 220
MAX_SUBJECT = 90

SYSTEM = """You write short, warm, professional outreach e-mails from a brand's marketing manager to an Instagram \
creator, inviting them to a paid collaboration.

Rules:
- Use ONLY the facts given. Do not invent numbers, fees, prices, discounts, product details, dates or deadlines.
- Do not mention money, rates or budget; compensation is discussed after the creator replies.
- Mention the brand handle and the campaign name exactly as given.
- Only mention @handles that appear in the facts.
- You do not know the creator's name: greet them warmly without a name.
- No placeholders like [Name] or {link}. Sign with the sender name and company from the facts.
- At most 180 words in the body. Plain text, no markdown.
Return JSON: {"subject": "...", "body": "..."}"""


# How each recommender reason may be said to the creator (no internal jargon, nothing creepy).
FRIENDLY_REASON = {
    "mentioned_brand": "you have already featured {brand} in your posts",
    "similar_brands_worked_with": "brands similar to {brand} have enjoyed working with you",
    "same_niche": "your {niche} content is a natural fit for {brand}",
    "size_fits_brand": "your audience size suits this campaign",
    "experienced": "you have experience with brand collaborations",
    "growing_engagement": "your recent posts are performing really well",
}


def friendly_reasons(reasons: list[dict], brand_handle: str) -> list[str]:
    out = []
    for r in reasons:
        t = FRIENDLY_REASON.get(r.get("code"))
        if t:
            out.append(t.format(brand=brand_handle, niche=r.get("niche", "")))
    return out


def build_facts(brand: dict, creator: dict, reasons: list[dict], campaign: dict, sender: dict) -> dict:
    """Everything the e-mail is allowed to say. Anything not traceable to this dict fails the checks."""
    facts = {
        "brand_handle": "@" + brand["brand"],
        "brand_niche": brand.get("niche"),
        "campaign_name": campaign["name"],
        "campaign_brief": campaign.get("brief") or "",
        "campaign_start": campaign.get("start_date"),
        "campaign_end": campaign.get("end_date"),
        "creator_niche": creator.get("niche"),
        "creator_size": creator.get("size_tier"),
        "creator_recent_brand_collaborations": ["@" + b for b in creator.get("recent_brands", [])[:3]],
        "why_this_creator": friendly_reasons(reasons, "@" + brand["brand"]),
        "sender_name": sender.get("name"),
        "sender_company": sender.get("company"),
        "sender_email": sender.get("email"),
    }
    return {k: v for k, v in facts.items() if v not in (None, "", [])}


def _numbers(text: str) -> set[str]:
    """All integers in the text, also without leading zeros ('05' -> '5') so dates can be rephrased."""
    found = re.findall(r"\d+", text)
    return set(found) | {str(int(n)) for n in found}


def check(draft: dict, facts: dict) -> list[str]:
    """Deterministic faithfulness checks. Returns a list of problems (empty = passed)."""
    issues = []
    subject, body = (draft.get("subject") or "").strip(), (draft.get("body") or "").strip()
    text = f"{subject}\n{body}"
    allowed = json.dumps(facts, ensure_ascii=False)
    if not subject or not body:
        issues.append("subject and body must not be empty")
    if len(subject) > MAX_SUBJECT:
        issues.append(f"subject longer than {MAX_SUBJECT} characters")
    if len(body.split()) > MAX_WORDS:
        issues.append(f"body longer than {MAX_WORDS} words")
    if facts["brand_handle"].lower() not in text.lower():
        issues.append(f"does not mention the brand {facts['brand_handle']}")
    if facts["campaign_name"].lower() not in text.lower():
        issues.append(f"does not mention the campaign name '{facts['campaign_name']}'")
    invented = sorted(n for n in _numbers(text) if n not in _numbers(allowed))
    if invented:
        issues.append(f"contains numbers that are not in the facts: {', '.join(invented)}")
    if re.search(r"[$€£]|\b(usd|eur|gbp|fee|rate card|per post|commission|discount)\b", text, re.I):
        issues.append("mentions money, fees or discounts")
    handles = {h.lower().rstrip(".") for h in re.findall(r"@[\w.]+", text)}
    known = {h.lower() for h in re.findall(r"@[\w.]+", allowed)}
    if facts.get("sender_email"):
        known |= {"@" + facts["sender_email"].split("@")[1].lower()}
    unknown = sorted(h for h in handles if h not in known)
    if unknown:
        issues.append(f"mentions handles that are not in the facts: {', '.join(unknown)}")
    if re.search(r"\[[^\]]{1,40}\]|\{[^}]{1,40}\}|<[^>]{1,40}>", text):
        issues.append("contains a placeholder")
    return issues


def template(facts: dict) -> dict:
    why = facts.get("why_this_creator", [])
    reason = f" We reached out because {why[0]}" + (f" and {why[1]}." if len(why) > 1 else ".") if why else ""
    lines = [
        "Hi there,",
        "",
        f"I'm {facts.get('sender_name', 'the marketing manager')} from {facts.get('sender_company', 'our team')}, "
        f"working with {facts['brand_handle']}. We're preparing a campaign called \"{facts['campaign_name']}\" "
        f"and we think your content would be a great fit.{reason}",
    ]
    if facts.get("campaign_brief"):
        lines += ["", f"About the campaign: {facts['campaign_brief']}"]
    lines += ["", "Would you be open to a paid collaboration? If so, just reply to this e-mail and we'll share "
                  "the details and discuss terms.", "", "Best regards,",
              facts.get("sender_name", ""), facts.get("sender_company", "")]
    name, brand = facts["campaign_name"], facts["brand_handle"]
    subject = f"Collaboration invite: {name}" if brand.lower() in name.lower() else f"Collaboration invite: {name} with {brand}"
    return {"subject": subject,
            "body": "\n".join(l for l in lines).strip()}


def _parse(raw: str) -> dict:
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        raise ValueError("no JSON object in model output")
    d = json.loads(m.group(0))
    return {"subject": str(d.get("subject", "")).strip(), "body": str(d.get("body", "")).strip()}


def draft_email(client, facts: dict) -> dict:
    """Ask the LLM for a draft, check it, retry once with feedback, else fall back to the template."""
    user = "FACTS (JSON):\n" + json.dumps(facts, ensure_ascii=False, indent=2)
    attempts = []
    if client is None:
        fallback = "no LLM provider configured"
    else:
        fallback = None
        prompt = user
        for attempt in range(2):
            try:
                draft = _parse(client.chat(SYSTEM, prompt))
            except LLMUnavailable as e:
                fallback = str(e)
                break
            except (ValueError, json.JSONDecodeError) as e:
                attempts.append({"issues": [f"unparseable output: {e}"]})
                prompt = user + "\n\nYour previous answer was not valid JSON. Return only the JSON object."
                continue
            issues = check(draft, facts)
            attempts.append({"issues": issues})
            if not issues:
                return {**draft, "provider": client.name, "model": getattr(client, "model", None),
                        "checks": {"passed": True, "issues": [], "attempts": attempts}, "facts": facts}
            prompt = (user + "\n\nYour previous draft broke these rules, fix them:\n- " + "\n- ".join(issues)
                      + "\n\nPrevious draft:\n" + json.dumps(draft, ensure_ascii=False))
        fallback = fallback or "LLM draft failed the checks twice"
    draft = template(facts)
    return {**draft, "provider": "template", "model": None, "fallback_reason": fallback,
            "checks": {"passed": not check(draft, facts), "issues": check(draft, facts), "attempts": attempts},
            "facts": facts}
