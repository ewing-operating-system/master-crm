"""
letter_integration.py — Next Chapter M&A Advisory
Integration layer: reads research data, generates personalized letters, stores results.

Flow:
    deal_research row  ->  build_letter_text()  ->  proposals.letter_templates['generated_letter']
                                                 ->  letter_approvals.status = 'pending_review'

Usage:
    from lib.letter_integration import generate_letter_for_target, batch_generate_letters

    result = generate_letter_for_target("some-target-id")
    results = batch_generate_letters(entity="next_chapter", limit=5)
"""

import json
import os
import sys
import ssl
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Supabase config (service role -- never exposed to browser)
# ---------------------------------------------------------------------------
SUPABASE_URL = os.environ.get(
    "SUPABASE_URL",
    "https://dwrnfpjcvydhmhnvyzov.supabase.co",
)
SUPABASE_KEY = os.environ.get(
    "SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s",
)

_ctx = ssl.create_default_context()


def _req_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def _request(method: str, path: str, data: Optional[dict] = None):
    """Minimal HTTP wrapper around Supabase REST API."""
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    payload = json.dumps(data, default=str).encode() if data else None
    req = urllib.request.Request(url, data=payload, headers=_req_headers(), method=method)
    try:
        resp = urllib.request.urlopen(req, context=_ctx)
        body = resp.read()
        return json.loads(body) if body.strip() else []
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"Supabase {method} {path} -> {e.code}: {body}") from e


def _get(table: str, params: str = "") -> list:
    path = f"{table}?{params}" if params else table
    result = _request("GET", path)
    return result if isinstance(result, list) else []


def _patch(table: str, params: str, data: dict) -> list:
    """PATCH (update) rows matching params."""
    path = f"{table}?{params}"
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{path}",
        data=json.dumps(data, default=str).encode(),
        headers=_req_headers(),
        method="PATCH",
    )
    try:
        resp = urllib.request.urlopen(req, context=_ctx)
        body = resp.read()
        return json.loads(body) if body.strip() else []
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"Supabase PATCH {table} -> {e.code}: {body}") from e


def _post(table: str, data: dict) -> list:
    return _request("POST", table, data)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _has_content(val) -> bool:
    return bool(val and isinstance(val, str) and val.strip() and len(val.strip()) > 5)


def _format_dollar(n) -> str:
    try:
        n = float(n)
    except (TypeError, ValueError):
        return ""
    if n >= 1_000_000:
        s = f"{n / 1_000_000:.1f}M"
        return f"${s.replace('.0M', 'M')}"
    if n >= 1_000:
        return f"${int(n / 1_000)}K"
    return f"${int(n):,}"


def _infer_tone(flags: dict) -> str:
    motivation = str(flags.get("motivation", "")).lower()
    timeline   = str(flags.get("timeline", "")).lower()
    if "retire" in motivation or "3month" in timeline or "health" in motivation:
        return "urgent"
    if "6month" in timeline or "12month" in timeline or "partner" in motivation or "growth" in motivation:
        return "warm"
    return "exploratory"


# ---------------------------------------------------------------------------
# Personalization scorer
# Mirrors JS LetterTemplateEngine._computeScore rubric (letter-template.js lines 133-177)
# ---------------------------------------------------------------------------

def score_personalization(research: dict, company: dict) -> dict:
    """
    Score how personalized the generated letter will be (0.0-1.0).

    Returns { total, breakdown, readiness_label }
    """
    breakdown = {}

    # Parse nested JSON fields safely
    research_data = research.get("research_data") or {}
    if isinstance(research_data, str):
        try:
            research_data = json.loads(research_data)
        except Exception:
            research_data = {}

    flags = research.get("flags") or {}
    if isinstance(flags, str):
        try:
            flags = json.loads(flags)
        except Exception:
            flags = {}

    buyer_targets = research.get("buyer_targets") or []
    if isinstance(buyer_targets, str):
        try:
            buyer_targets = json.loads(buyer_targets)
        except Exception:
            buyer_targets = []

    # 0.30 -- story richness
    story_cards   = research_data.get("story_cards", []) if isinstance(research_data, dict) else []
    story_narrative = research.get("story_narrative") or ""
    filled_cards  = sum(1 for s in story_cards if isinstance(s, dict) and _has_content(s.get("story", "")))
    if story_cards:
        story_score = min(filled_cards / 2, 1) * 0.30
    else:
        story_score = 0.15 if _has_content(story_narrative) else 0.0
    breakdown["story_elements"] = round(story_score, 3)

    # 0.30 -- buyer research signals
    has_buyer_targets   = bool(buyer_targets)
    has_comp_context    = bool(isinstance(research_data, dict) and research_data.get("competitive_context"))
    has_buyer_rationale = _has_content(research.get("notes") or "")
    buyer_signals = sum([has_buyer_targets, has_comp_context, has_buyer_rationale])
    breakdown["buyer_research"] = round((buyer_signals / 3) * 0.30, 3)

    # 0.20 -- timeline / motivation match
    has_timeline   = _has_content(str(flags.get("timeline", "")))
    has_motivation = _has_content(str(flags.get("motivation", "")))
    breakdown["timeline_match"] = round(((1 if has_timeline else 0) + (1 if has_motivation else 0)) / 2 * 0.20, 3)

    # 0.10 -- deal-breakers addressed
    deal_concerns = flags.get("deal_breakers") or flags.get("concerns") or []
    breakdown["deal_breakers"] = 0.10 if not deal_concerns else (0.05 if has_buyer_targets else 0.0)

    # 0.10 -- financial detail
    has_revenue = bool(research.get("revenue") or company.get("estimated_revenue"))
    has_ebitda  = bool(company.get("estimated_ebitda"))
    breakdown["financial_detail"] = round(((1 if has_revenue else 0) + (1 if has_ebitda else 0)) / 2 * 0.10, 3)

    total = round(sum(breakdown.values()), 2)

    if total >= 0.80:
        label = "Production Ready"
    elif total >= 0.60:
        label = "Good"
    else:
        label = "Needs Refinement"

    return {"total": total, "breakdown": breakdown, "readiness_label": label}


# ---------------------------------------------------------------------------
# Letter text builder
# Pure Python implementation of the letter formula from LetterTemplateEngine (JS)
# ---------------------------------------------------------------------------

VERTICAL_MULTIPLES = {
    "water_treatment":  (4.0, 8.0),
    "hvac":             (4.5, 8.5),
    "plumbing":         (4.0, 7.5),
    "roofing":          (3.5, 7.0),
    "pest_control":     (5.0, 10.0),
    "concrete_precast": (4.0, 7.5),
    "flooring":         (3.5, 6.5),
}


def build_letter_text(research: dict, company: dict) -> str:
    """
    Generate a personalized letter from deal_research + company row.
    Returns HTML paragraphs wrapped in <p class="letter-paragraph"> tags.
    """
    owner_name   = research.get("owner_name") or ""
    owner_first  = owner_name.split()[0] if owner_name.strip() else "there"
    company_name = research.get("company_name") or company.get("company_name", "your company")
    vertical     = company.get("vertical") or research.get("category") or "default"
    city         = research.get("city") or company.get("city", "")
    state        = research.get("state") or company.get("state", "")
    location_str = f" in {city}, {state}" if city and state else (f" in {city}" if city else "")

    # Parse nested fields
    research_data = research.get("research_data") or {}
    if isinstance(research_data, str):
        try:
            research_data = json.loads(research_data)
        except Exception:
            research_data = {}

    flags = research.get("flags") or {}
    if isinstance(flags, str):
        try:
            flags = json.loads(flags)
        except Exception:
            flags = {}

    buyer_targets = research.get("buyer_targets") or []
    if isinstance(buyer_targets, str):
        try:
            buyer_targets = json.loads(buyer_targets)
        except Exception:
            buyer_targets = []

    # Best story to hook with
    story_cards     = research_data.get("story_cards", []) if isinstance(research_data, dict) else []
    story_narrative = research.get("story_narrative") or ""
    top_story = ""
    for card in story_cards:
        if isinstance(card, dict) and _has_content(card.get("story", "")):
            top_story = card["story"].strip()
            break
    if not top_story and _has_content(story_narrative):
        top_story = story_narrative.strip()

    competitive_context = ""
    if isinstance(research_data, dict):
        competitive_context = (research_data.get("competitive_context") or "").strip()

    # Buyer names
    buyer_names = []
    for b in buyer_targets[:3]:
        if isinstance(b, dict):
            n = b.get("name") or b.get("buyer_name") or b.get("company")
            if n:
                buyer_names.append(str(n).strip())
        elif isinstance(b, str) and b.strip():
            buyer_names.append(b.strip())

    # Financials
    revenue  = research.get("revenue") or company.get("estimated_revenue")
    ebitda   = company.get("estimated_ebitda")
    val_low  = research.get("valuation_low")
    val_high = research.get("valuation_high")
    mult_low, mult_high = VERTICAL_MULTIPLES.get(vertical, (4.0, 7.0))

    tone = _infer_tone(flags)

    # -- P1: Story hook + market fit ----------------------------------------
    if top_story:
        p1_hook = f"{top_story} "
    else:
        year_founded = company.get("year_founded")
        if year_founded:
            try:
                age = 2026 - int(year_founded)
                p1_hook = (
                    f"You've spent {age} years building {company_name}{location_str}, "
                    f"and that kind of track record doesn't happen by accident. "
                )
            except Exception:
                p1_hook = f"What you've built at {company_name}{location_str} is exactly the kind of story that gets a buyer's attention. "
        else:
            p1_hook = f"What you've built at {company_name}{location_str} is exactly the kind of story that gets a buyer's attention. "

    if competitive_context:
        p1_mid = f"{competitive_context} "
    else:
        p1_mid = ""

    if buyer_names:
        buyers_str = " and ".join(buyer_names[:2])
        p1_close = f"That's precisely why buyers like {buyers_str} belong in this conversation. I'm reaching out directly because I believe there's a genuine fit between what you've built and what active acquirers are pursuing right now."
    else:
        p1_close = "That combination is exactly what serious buyers in your market are looking for. I'm reaching out directly because I believe there's a genuine fit worth exploring."

    p1 = f"{p1_hook}{p1_mid}{p1_close}"

    # -- P2: Financials + differentiators -----------------------------------
    p2_parts = []
    if revenue:
        rev_str = _format_dollar(revenue)
        p2_parts.append(f"{company_name} is running {rev_str} in annual revenue")
        if ebitda:
            p2_parts.append(f"generating {_format_dollar(ebitda)} in adjusted EBITDA")
        p2_parts.append("-- numbers that will stand up in any quality of earnings process.")

    notes = (research.get("notes") or "").strip()
    if _has_content(notes):
        p2_parts.append(notes)

    if not p2_parts:
        p2_parts.append(
            f"The fundamentals at {company_name} are exactly what active acquirers want to see -- "
            f"an operator-built business with real customers and real staying power."
        )

    p2 = " ".join(p2_parts)

    # -- P3: Valuation + buyer intro ----------------------------------------
    p3_parts = []

    if val_low and val_high:
        p3_parts.append(
            f"Based on current market comps in your vertical, {company_name} is realistically "
            f"positioned in the {_format_dollar(val_low)}-{_format_dollar(val_high)} range."
        )
    elif ebitda:
        low_val  = _format_dollar(float(ebitda) * mult_low)
        high_val = _format_dollar(float(ebitda) * mult_high)
        p3_parts.append(
            f"Based on current {vertical.replace('_', ' ')} market multiples ({mult_low}x-{mult_high}x EBITDA), "
            f"a business like {company_name} is realistically positioned in the {low_val}-{high_val} range."
        )

    if buyer_names:
        p3_parts.append(
            f"I'd like to introduce you to a shortlist of buyers -- including {buyer_names[0]} -- "
            f"who are actively acquiring in your space. This is not a mass mailer. "
            f"If you're willing to take one conversation, I will make sure the right person is on the other end of it."
        )
    else:
        p3_parts.append(
            f"I have a shortlist of buyers who are actively acquiring in your space. "
            f"This is not a mass mailer. "
            f"If you're willing to take one conversation, I will make sure the right person is on the other end of it."
        )

    p3 = " ".join(p3_parts)

    # -- Closing based on tone ----------------------------------------------
    if tone == "urgent":
        closing = (
            f"There's no pressure and no obligation. When you've spent your life building "
            f"something as real as {company_name}, the decision to explore what's next deserves "
            f"to happen on your terms. Reply to this letter, call me, or send an email -- "
            f"whichever feels most comfortable. I'm here when you're ready."
        )
    elif tone == "warm":
        closing = (
            f"You've built something worth growing further, and the right partner can accelerate "
            f"everything you've already put in motion. A single conversation costs nothing and "
            f"could change how you think about what's possible from here. Just say the word."
        )
    else:
        closing = (
            f"This letter costs you nothing and obligates you to nothing. If you're even slightly "
            f"curious about what {company_name} is worth in today's market -- and what your "
            f"options actually look like -- I hope you'll reach out. I'll make the introduction the same day."
        )

    paragraphs = [
        f'<p class="letter-paragraph" data-section="greeting">Dear {owner_first},</p>',
        f'<p class="letter-paragraph" data-section="p1">{p1}</p>',
        f'<p class="letter-paragraph" data-section="p2">{p2}</p>',
        f'<p class="letter-paragraph" data-section="p3">{p3}</p>',
        f'<p class="letter-paragraph" data-section="closing">{closing}</p>',
    ]
    return "\n\n".join(paragraphs)


# ---------------------------------------------------------------------------
# Core integration functions
# ---------------------------------------------------------------------------

def generate_letter_for_target(target_id: str) -> dict:
    """
    Generate a personalized letter for a single target.

    Steps:
        a. Fetch target from targets table
        b. Fetch research from deal_research (matched by company_name)
        c. Fetch company data from companies
        d. Build letter text + score personalization
        e. Store in proposals.letter_templates['generated_letter']
        f. Create letter_approvals record status='pending_review' (graceful if table missing)

    Returns:
        {
            "target_id": str,
            "proposal_id": str | None,
            "letter_text": str,
            "personalization_score": float,
            "score_breakdown": dict,
            "tone_signal": str,
            "readiness_label": str,
            "generated_at": str,
        }
    """
    now = datetime.utcnow().isoformat() + "Z"

    # -- Step a: Fetch target ------------------------------------------------
    rows = _get("targets", f"id=eq.{urllib.parse.quote(target_id)}")
    if not rows:
        raise ValueError(f"Target not found: {target_id}")
    target     = rows[0]
    entity     = target.get("entity", "next_chapter")
    company_id = target.get("company_id") or ""

    # -- Step b: Fetch research ----------------------------------------------
    research = {}
    company_name_raw = target.get("company_name", "")
    if company_name_raw:
        research_rows = _get(
            "deal_research",
            f"company_name=eq.{urllib.parse.quote(company_name_raw)}&limit=1",
        )
        if research_rows:
            research = research_rows[0]

    # -- Step c: Fetch company -----------------------------------------------
    company = {}
    if company_id:
        co_rows = _get("companies", f"id=eq.{urllib.parse.quote(company_id)}")
        if co_rows:
            company = co_rows[0]
    if not company and company_name_raw:
        co_rows = _get("companies", f"company_name=eq.{urllib.parse.quote(company_name_raw)}&limit=1")
        if co_rows:
            company = co_rows[0]

    # -- Step d: Generate ----------------------------------------------------
    # Merge target + research so builder has full context
    merged = {
        "owner_name":      target.get("company_name", ""),
        "company_name":    company_name_raw,
        "city":            company.get("city", ""),
        "state":           company.get("state", ""),
        "category":        company.get("vertical", ""),
        "revenue":         company.get("estimated_revenue"),
        "valuation_low":   None,
        "valuation_high":  None,
        "story_narrative": "",
        "research_data":   {},
        "buyer_targets":   [],
        "flags":           {},
        "notes":           "",
    }
    # Overlay actual research fields (non-None only)
    for k, v in research.items():
        if v is not None:
            merged[k] = v

    letter_text  = build_letter_text(merged, company)
    score_result = score_personalization(merged, company)
    tone_signal  = _infer_tone(merged.get("flags") or {})

    # -- Step e: Upsert into proposals ---------------------------------------
    letter_payload = {
        "generated_letter":      letter_text,
        "personalization_score": score_result["total"],
        "tone_signal":           tone_signal,
        "readiness_label":       score_result["readiness_label"],
        "score_breakdown":       score_result["breakdown"],
        "generated_at":          now,
    }

    proposals = _get("proposals", f"target_id=eq.{urllib.parse.quote(target_id)}&limit=1")
    proposal_id = None

    if proposals:
        proposal_id = proposals[0]["id"]
        # Merge into existing letter_templates
        existing_lt = proposals[0].get("letter_templates") or {}
        if isinstance(existing_lt, str):
            try:
                existing_lt = json.loads(existing_lt)
            except Exception:
                existing_lt = {}
        existing_lt.update(letter_payload)

        existing_ef = proposals[0].get("extra_fields") or {}
        if isinstance(existing_ef, str):
            try:
                existing_ef = json.loads(existing_ef)
            except Exception:
                existing_ef = {}
        existing_ef.update({
            "letter_personalization_score": score_result["total"],
            "letter_tone_signal":           tone_signal,
            "letter_readiness_label":       score_result["readiness_label"],
            "letter_generated_at":          now,
        })

        _patch(
            "proposals",
            f"id=eq.{urllib.parse.quote(proposal_id)}",
            {
                "letter_templates": existing_lt,
                "extra_fields":     existing_ef,
                "updated_at":       now,
            },
        )
    else:
        # Create minimal proposal if none exists
        new_proposal = {
            "target_id":        target_id,
            "company_id":       company_id or None,
            "entity":           entity,
            "company_name":     company_name_raw,
            "vertical":         company.get("vertical", ""),
            "letter_templates": letter_payload,
            "extra_fields": {
                "letter_personalization_score": score_result["total"],
                "letter_tone_signal":           tone_signal,
                "letter_readiness_label":       score_result["readiness_label"],
                "letter_generated_at":          now,
            },
            "status":     "letter_pending_review",
            "created_at": now,
            "updated_at": now,
        }
        created = _post("proposals", new_proposal)
        if created:
            proposal_id = (created[0] if isinstance(created, list) else created).get("id")

    # -- Step f: letter_approvals record (graceful) --------------------------
    if proposal_id:
        approval_row = {
            "proposal_id":           proposal_id,
            "target_id":             target_id,
            "entity":                entity,
            "status":                "pending_review",
            "personalization_score": score_result["total"],
            "tone_signal":           tone_signal,
            "created_at":            now,
            "updated_at":            now,
        }
        try:
            _post("letter_approvals", approval_row)
        except RuntimeError as e:
            err_str = str(e)
            if "PGRST205" in err_str or "does not exist" in err_str or "404" in err_str:
                pass  # Table not yet created -- skip silently
            else:
                raise

    return {
        "target_id":             target_id,
        "proposal_id":           proposal_id,
        "letter_text":           letter_text,
        "personalization_score": score_result["total"],
        "score_breakdown":       score_result["breakdown"],
        "tone_signal":           tone_signal,
        "readiness_label":       score_result["readiness_label"],
        "generated_at":          now,
    }


def batch_generate_letters(entity: str = "next_chapter", limit: int = 10) -> list:
    """
    Batch-generate letters for targets that don't yet have a generated_letter stored.

    Skips targets with pipeline_status in: letter_sent, called, responded, closed, dead.
    Skips targets that already have proposals.letter_templates.generated_letter set.

    Returns list of result dicts from generate_letter_for_target.
    """
    SKIP_STATUSES = {"letter_sent", "called", "responded", "closed", "dead"}

    # Fetch candidates
    targets = _get(
        "targets",
        f"entity=eq.{urllib.parse.quote(entity)}&order=created_at.desc&limit={limit * 4}",
    )
    candidates = [t for t in targets if t.get("pipeline_status") not in SKIP_STATUSES]

    # Filter: skip targets that already have a generated_letter in proposals
    already_done = set()
    if candidates:
        ids_csv = ",".join(urllib.parse.quote(t["id"]) for t in candidates)
        props = _get("proposals", f"target_id=in.({ids_csv})&select=target_id,letter_templates")
        for p in props:
            lt = p.get("letter_templates") or {}
            if isinstance(lt, str):
                try:
                    lt = json.loads(lt)
                except Exception:
                    lt = {}
            if lt.get("generated_letter"):
                already_done.add(p["target_id"])

    work_queue = [t for t in candidates if t["id"] not in already_done][:limit]

    if not work_queue:
        print(f"[letter_integration] No targets need letters for entity={entity}")
        return []

    results = []
    for target in work_queue:
        try:
            result = generate_letter_for_target(target["id"])
            print(
                f"  + {target.get('company_name','?')} "
                f"score={result['personalization_score']:.2f} ({result['readiness_label']})"
            )
            results.append(result)
        except Exception as e:
            print(f"  x {target.get('company_name','?')} -- {e}")
            results.append({"target_id": target["id"], "error": str(e)})

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Letter Integration -- generate letters from research data")
    sub = parser.add_subparsers(dest="cmd")

    p_gen = sub.add_parser("generate", help="Generate letter for one target")
    p_gen.add_argument("target_id", help="UUID of the target row")

    p_batch = sub.add_parser("batch", help="Batch-generate letters for an entity")
    p_batch.add_argument("--entity", default="next_chapter")
    p_batch.add_argument("--limit", default=10, type=int)

    args = parser.parse_args()

    if args.cmd == "generate":
        res = generate_letter_for_target(args.target_id)
        print(json.dumps(res, indent=2))

    elif args.cmd == "batch":
        results = batch_generate_letters(entity=args.entity, limit=args.limit)
        ok  = [r for r in results if "error" not in r]
        err = [r for r in results if "error" in r]
        print(f"\n[letter_integration] {len(ok)} generated, {len(err)} failed")
        if ok:
            avg = sum(r["personalization_score"] for r in ok) / len(ok)
            print(f"  Avg personalization score: {avg:.2f}")
    else:
        parser.print_help()
