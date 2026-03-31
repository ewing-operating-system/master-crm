#!/usr/bin/env python3
"""
Why Sell Engine — buyer-facing pitch narratives for NC sell-side engagements.

Generates 5 narrative components that answer "Why sell your company NOW?" and
per-buyer narratives that answer "Why sell to THIS buyer?"

These narratives are:
  - Included in the mail package sent to prospects (company owners)
  - Sent to the client for review and editing
  - Sent by link/email to potential buyers as outreach

Components:
  1. Market Timing     — industry consolidation trends, current valuation multiples
  2. Owner Lifecycle   — succession planning, retirement timeline
  3. Competitive Pressure — PE roll-ups in their vertical, shrinking independents
  4. Value Maximization   — current EBITDA multiples vs historical, buyer demand
  5. Risk of Waiting   — market cycles, regulatory changes, key-person risk

Primary functions:
  generate_why_sell(company_id, entity='next_chapter')
      — generates all 5 components for a selling company
  generate_buyer_pitch(company_id, buyer_id)
      — generates "why sell to THIS buyer" narrative
  batch_generate(proposal_id)
      — generates for all buyers in a proposal

Output stored in why_sell_narratives table (upserted by company_id / buyer_id).
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.parse
import ssl
from datetime import datetime

# ─── Config ──────────────────────────────────────────────────────────────────

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dwrnfpjcvydhmhnvyzov.supabase.co")
SUPABASE_KEY = os.environ.get(
    "SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s",
)
OPENROUTER_KEY = os.environ.get(
    "OPENROUTER_API_KEY",
    "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",
)

LOG_FILE = os.path.expanduser("~/Projects/master-crm/data/logs/why_sell_engine.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

ctx = ssl.create_default_context()

# ─── Logging ─────────────────────────────────────────────────────────────────


def log(msg):
    line = f"{datetime.utcnow().isoformat()} | WHY_SELL | {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# ─── LLM Callers ─────────────────────────────────────────────────────────────


def call_claude(prompt, timeout=300):
    """Claude CLI — $0.00, highest quality. Returns text or None."""
    try:
        result = subprocess.run(
            ["claude", "-p", "--output-format", "text"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        log(f"  Claude CLI failed: exit={result.returncode}, stderr={result.stderr[:120]}")
        return None
    except subprocess.TimeoutExpired:
        log(f"  Claude CLI timeout after {timeout}s")
        return None
    except Exception as e:
        log(f"  Claude CLI error: {e}")
        return None


def call_openrouter(prompt, model="deepseek/deepseek-chat-v3-0324", max_tokens=4000):
    """OpenRouter fallback."""
    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        }
    ).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://nextchapterma.com",
        },
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=120)
        data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log(f"  OpenRouter error: {e}")
        return None


def generate_text(prompt, timeout=300):
    """Try Claude CLI first, fall back to OpenRouter."""
    text = call_claude(prompt, timeout=timeout)
    if text:
        return text
    log("  Falling back to OpenRouter…")
    return call_openrouter(prompt)


# ─── Supabase REST Helpers ───────────────────────────────────────────────────


def _headers(prefer=None):
    h = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def sb_get(table, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, headers=_headers())
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read())


def sb_upsert(table, data, on_conflict=None):
    prefer = "return=representation,resolution=merge-duplicates"
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if on_conflict:
        url += f"?on_conflict={on_conflict}"
    payload = json.dumps(data, default=str).encode()
    req = urllib.request.Request(url, data=payload, headers=_headers(prefer), method="POST")
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read())


def sb_update(table, match_col, match_val, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{match_col}=eq.{urllib.parse.quote(str(match_val))}"
    payload = json.dumps(data, default=str).encode()
    req = urllib.request.Request(
        url, data=payload, headers=_headers("return=representation"), method="PATCH"
    )
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read())


# ─── Data Loaders ────────────────────────────────────────────────────────────


def load_company(company_id):
    """Load company profile from deal_research by id or company_name."""
    rows = sb_get("deal_research", f"id=eq.{company_id}&limit=1")
    if rows:
        return rows[0]
    # Fallback: treat company_id as name substring
    rows = sb_get(
        "deal_research",
        f"company_name=ilike.*{urllib.parse.quote(str(company_id))}*&limit=1",
    )
    return rows[0] if rows else {}


def load_buyer(buyer_id):
    """Load a buyer record from engagement_buyers by id."""
    rows = sb_get("engagement_buyers", f"id=eq.{buyer_id}&limit=1")
    return rows[0] if rows else {}


def load_buyers_for_proposal(proposal_id):
    """Load all buyers for a proposal from engagement_buyers."""
    return sb_get(
        "engagement_buyers",
        f"proposal_id=eq.{proposal_id}&order=fit_score.desc.nullslast",
    )


def load_proposal(proposal_id):
    """Load a proposal record."""
    rows = sb_get("proposals", f"id=eq.{proposal_id}&limit=1")
    return rows[0] if rows else {}


# ─── Narrative Prompts ────────────────────────────────────────────────────────


def _company_context(company):
    """Build a compact company brief for prompt injection."""
    research_data = company.get("research_data") or {}
    if isinstance(research_data, str):
        try:
            research_data = json.loads(research_data)
        except Exception:
            research_data = {}

    flags = company.get("flags") or {}
    if isinstance(flags, str):
        try:
            flags = json.loads(flags)
        except Exception:
            flags = {}

    return {
        "company_name": company.get("company_name", "the company"),
        "owner_name": company.get("owner_name", "the owner"),
        "vertical": company.get("category") or company.get("vertical", "business services"),
        "city": company.get("city", ""),
        "state": company.get("state", ""),
        "revenue": company.get("revenue") or research_data.get("revenue", ""),
        "ebitda": company.get("ebitda") or research_data.get("ebitda", ""),
        "employees": company.get("employees") or research_data.get("employees", ""),
        "years_in_business": company.get("years_in_business") or research_data.get("years_in_business", ""),
        "services": company.get("services") or research_data.get("services", ""),
        "story_narrative": company.get("story_narrative", ""),
        "flags": flags,
        "research_data": research_data,
    }


NARRATIVE_INSTRUCTIONS = """
Write in second person ("you", "your company"). Be specific. Avoid jargon.
Do NOT use phrases like "private equity" — say "investors who buy businesses" or "operators who buy and grow companies" or "business owners who've cashed out and now acquire".
Do NOT make up financial figures — use ranges and qualitative language if numbers are unknown.
Output 2–4 tight paragraphs. No headers, no bullets. Plain narrative prose only.
"""


def _prompt_market_timing(ctx_dict):
    return f"""You are a senior M&A advisor at Next Chapter, a sell-side advisory firm that represents business owners.

Write a compelling "Market Timing" narrative for why NOW is the right moment to sell {ctx_dict['company_name']}, a {ctx_dict['vertical']} business in {ctx_dict['city']}, {ctx_dict['state']}.

Known details:
- Revenue: {ctx_dict['revenue'] or 'not disclosed'}
- EBITDA: {ctx_dict['ebitda'] or 'not disclosed'}
- Years in business: {ctx_dict['years_in_business'] or 'unknown'}
- Services: {ctx_dict['services'] or 'not specified'}

Cover:
- Industry consolidation trends currently happening in this vertical
- Current EBITDA valuation multiples vs. where they were 3–5 years ago
- Why buyer appetite is high right now for businesses like this one
- Why waiting 2–3 years could mean selling at a lower multiple

{NARRATIVE_INSTRUCTIONS}"""


def _prompt_owner_lifecycle(ctx_dict):
    return f"""You are a senior M&A advisor at Next Chapter, a sell-side advisory firm.

Write an "Owner Lifecycle" narrative for {ctx_dict['owner_name']}, owner of {ctx_dict['company_name']} ({ctx_dict['vertical']}, {ctx_dict['city']}, {ctx_dict['state']}).

This section speaks directly to the owner about:
- The natural arc of building a business and what comes next
- How the next stage of life — freedom, legacy, financial security — is unlocked by a well-timed sale
- How selling doesn't mean leaving; most buyers want operators to stay if they want to
- Why this is about maximizing the value of a life's work, not just exiting

Additional context:
- Years in business: {ctx_dict['years_in_business'] or 'unknown'}
- Owner narrative: {ctx_dict['story_narrative'][:300] if ctx_dict['story_narrative'] else 'not available'}

{NARRATIVE_INSTRUCTIONS}"""


def _prompt_competitive_pressure(ctx_dict):
    return f"""You are a senior M&A advisor at Next Chapter, a sell-side advisory firm.

Write a "Competitive Pressure" narrative for the owner of {ctx_dict['company_name']} ({ctx_dict['vertical']}, {ctx_dict['city']}, {ctx_dict['state']}).

This section explains:
- How operators who buy and grow companies (funded buyers) are aggressively rolling up independents in this vertical
- How the independent business owner competitive landscape is shrinking year over year
- What happens to market share and pricing power when acquirers enter a local market
- The strategic disadvantage of remaining independent when well-capitalized competitors are consolidating

Vertical: {ctx_dict['vertical']}
Employees: {ctx_dict['employees'] or 'unknown'}
Services: {ctx_dict['services'] or 'not specified'}

{NARRATIVE_INSTRUCTIONS}"""


def _prompt_value_maximization(ctx_dict):
    return f"""You are a senior M&A advisor at Next Chapter, a sell-side advisory firm.

Write a "Value Maximization" narrative for the owner of {ctx_dict['company_name']} ({ctx_dict['vertical']}, {ctx_dict['city']}, {ctx_dict['state']}).

This section makes the financial case:
- What EBITDA multiples look like in this vertical today (be honest about the range)
- How a competitive, well-run sale process can add 1–3x to the multiple vs. a single buyer negotiation
- The difference between a reactive sale (someone approaches you) and a proactive sale (Next Chapter runs a full process)
- How the timing of a sale — while the business is performing well — is the single biggest lever on price

Known financials:
- Revenue: {ctx_dict['revenue'] or 'not disclosed'}
- EBITDA: {ctx_dict['ebitda'] or 'not disclosed'}

{NARRATIVE_INSTRUCTIONS}"""


def _prompt_risk_of_waiting(ctx_dict):
    return f"""You are a senior M&A advisor at Next Chapter, a sell-side advisory firm.

Write a "Risk of Waiting" narrative for the owner of {ctx_dict['company_name']} ({ctx_dict['vertical']}, {ctx_dict['city']}, {ctx_dict['state']}).

This section honestly addresses the downside risks of delaying a sale:
- Market cycle risk: buyer multiples compress during economic uncertainty
- Key-person risk: the owner IS the business — what happens to value if health or circumstances change
- Regulatory and industry headwinds that may affect this specific vertical
- The compounding complexity of selling later vs. now (more documentation, more scrutiny, more time)

Vertical: {ctx_dict['vertical']}
Years in business: {ctx_dict['years_in_business'] or 'unknown'}
Flags from research: {json.dumps(ctx_dict['flags']) if ctx_dict['flags'] else 'none recorded'}

{NARRATIVE_INSTRUCTIONS}"""


def _prompt_buyer_pitch(company_ctx, buyer):
    buyer_name = buyer.get("buyer_company_name", "the buyer")
    buyer_type = buyer.get("buyer_type", "strategic acquirer")
    buyer_thesis = buyer.get("investment_thesis") or buyer.get("notes") or ""
    buyer_portfolio = buyer.get("portfolio_companies") or ""
    acquisitions = buyer.get("recent_acquisitions") or ""
    fit_score = buyer.get("fit_score", "")

    return f"""You are a senior M&A advisor at Next Chapter, a sell-side advisory firm.

Write a "Why Sell to {buyer_name}" narrative. This will be read by the seller ({company_ctx['company_name']}) to understand why this buyer is a strong match.

Seller:
- Company: {company_ctx['company_name']}
- Vertical: {company_ctx['vertical']}
- Location: {company_ctx['city']}, {company_ctx['state']}
- Revenue: {company_ctx['revenue'] or 'not disclosed'}
- EBITDA: {company_ctx['ebitda'] or 'not disclosed'}

Buyer:
- Name: {buyer_name}
- Type: {buyer_type}
- Fit score: {fit_score}/100
- Investment thesis: {buyer_thesis[:400] if buyer_thesis else 'not available'}
- Portfolio / past acquisitions: {(str(buyer_portfolio) + ' ' + str(acquisitions)).strip()[:400] or 'not available'}

Cover:
- Why this buyer is strategically attracted to businesses like this one
- What they typically offer sellers (culture preservation, operator respect, growth resources)
- Why this is a better outcome than selling to a random competitor or sitting on the sideline
- One concrete reason this specific buyer stands out as a strong match

{NARRATIVE_INSTRUCTIONS}"""


# ─── Core Generation Functions ────────────────────────────────────────────────


def generate_why_sell(company_id, entity="next_chapter"):
    """
    Generate all 5 'Why Sell NOW' narrative components for a selling company.

    Pulls company data from deal_research, runs 5 LLM prompts, stores output
    in why_sell_narratives table keyed by company_id.

    Returns: dict with all 5 narrative strings + metadata
    """
    log(f"\n{'='*60}")
    log(f"GENERATE WHY SELL: company_id={company_id}, entity={entity}")
    log(f"{'='*60}")

    company = load_company(company_id)
    if not company:
        log(f"  ERROR: No company found for id={company_id}")
        return None

    company_name = company.get("company_name", str(company_id))
    log(f"  Company: {company_name}")

    ctx_dict = _company_context(company)

    components = {
        "market_timing": None,
        "owner_lifecycle": None,
        "competitive_pressure": None,
        "value_maximization": None,
        "risk_of_waiting": None,
    }

    prompts = {
        "market_timing": _prompt_market_timing(ctx_dict),
        "owner_lifecycle": _prompt_owner_lifecycle(ctx_dict),
        "competitive_pressure": _prompt_competitive_pressure(ctx_dict),
        "value_maximization": _prompt_value_maximization(ctx_dict),
        "risk_of_waiting": _prompt_risk_of_waiting(ctx_dict),
    }

    for component, prompt in prompts.items():
        log(f"  Generating {component}…")
        text = generate_text(prompt)
        if text:
            components[component] = text
            log(f"    OK ({len(text)} chars)")
        else:
            log(f"    FAILED — storing placeholder")
            components[component] = f"[{component} narrative pending generation]"
        time.sleep(1)

    now = datetime.utcnow().isoformat()
    record = {
        "company_id": str(company_id),
        "company_name": company_name,
        "entity": entity,
        "market_timing": components["market_timing"],
        "owner_lifecycle": components["owner_lifecycle"],
        "competitive_pressure": components["competitive_pressure"],
        "value_maximization": components["value_maximization"],
        "risk_of_waiting": components["risk_of_waiting"],
        "generated_at": now,
        "status": "generated",
    }

    try:
        saved = sb_upsert("why_sell_narratives", record, on_conflict="company_id")
        log(f"  Saved to why_sell_narratives: company_id={company_id}")
    except Exception as e:
        log(f"  Supabase upsert failed: {e} — storing in proposals instead")
        _store_in_proposals_fallback(company_id, record)

    log(f"  DONE: {company_name}")
    return record


def generate_buyer_pitch(company_id, buyer_id, entity="next_chapter"):
    """
    Generate "why sell to THIS buyer" narrative for a specific seller/buyer pair.

    Returns: dict with buyer_pitch narrative + metadata
    """
    log(f"\n{'='*60}")
    log(f"GENERATE BUYER PITCH: company_id={company_id}, buyer_id={buyer_id}")
    log(f"{'='*60}")

    company = load_company(company_id)
    buyer = load_buyer(buyer_id)

    if not company:
        log(f"  ERROR: No company found for id={company_id}")
        return None
    if not buyer:
        log(f"  ERROR: No buyer found for id={buyer_id}")
        return None

    company_name = company.get("company_name", str(company_id))
    buyer_name = buyer.get("buyer_company_name", str(buyer_id))
    log(f"  Seller: {company_name} | Buyer: {buyer_name}")

    ctx_dict = _company_context(company)
    prompt = _prompt_buyer_pitch(ctx_dict, buyer)

    log(f"  Generating buyer pitch…")
    text = generate_text(prompt)
    if not text:
        log(f"  FAILED — storing placeholder")
        text = f"[Buyer pitch for {buyer_name} pending generation]"
    else:
        log(f"  OK ({len(text)} chars)")

    now = datetime.utcnow().isoformat()
    record = {
        "company_id": str(company_id),
        "company_name": company_name,
        "buyer_id": str(buyer_id),
        "buyer_name": buyer_name,
        "entity": entity,
        "buyer_pitch": text,
        "generated_at": now,
        "status": "generated",
    }

    try:
        saved = sb_upsert(
            "why_sell_buyer_pitches", record, on_conflict="company_id,buyer_id"
        )
        log(f"  Saved to why_sell_buyer_pitches")
    except Exception as e:
        log(f"  Supabase upsert failed: {e}")

    return record


def batch_generate(proposal_id, entity="next_chapter"):
    """
    Generate why-sell narratives for all buyers in a proposal.

    Steps:
    1. Load the proposal
    2. Generate the 5 company-level narratives (once)
    3. Generate per-buyer pitches for all buyers (up to 20)
    4. Return summary dict
    """
    log(f"\n{'='*60}")
    log(f"BATCH GENERATE: proposal_id={proposal_id}")
    log(f"{'='*60}")

    proposal = load_proposal(proposal_id)
    if not proposal:
        log(f"  ERROR: Proposal {proposal_id} not found")
        return None

    company_id = proposal.get("company_id") or proposal.get("target_company_id")
    company_name = proposal.get("company_name") or proposal.get("target_company", "unknown")
    log(f"  Proposal company: {company_name} (id={company_id})")

    results = {
        "proposal_id": proposal_id,
        "company_id": company_id,
        "company_name": company_name,
        "why_sell": None,
        "buyer_pitches": [],
        "errors": [],
    }

    # Step 2: Company-level narratives
    if company_id:
        try:
            ws = generate_why_sell(company_id, entity=entity)
            results["why_sell"] = ws
        except Exception as e:
            log(f"  Why-sell generation error: {e}")
            results["errors"].append(str(e))
    else:
        log(f"  WARNING: No company_id on proposal — skipping company narratives")

    # Step 3: Per-buyer pitches
    buyers = load_buyers_for_proposal(proposal_id)
    log(f"  Buyers loaded: {len(buyers)}")
    capped = buyers[:50]

    for i, buyer in enumerate(capped):
        buyer_id = buyer.get("id")
        buyer_name = buyer.get("buyer_company_name", "unknown")
        log(f"  [{i+1}/{len(capped)}] Pitching {buyer_name}…")
        try:
            bp = generate_buyer_pitch(company_id, buyer_id, entity=entity)
            if bp:
                results["buyer_pitches"].append(bp)
        except Exception as e:
            log(f"    Error: {e}")
            results["errors"].append(f"{buyer_name}: {e}")
        time.sleep(1)

    # Update proposal record with narrative status
    if company_id:
        try:
            sb_update(
                "proposals",
                "id",
                proposal_id,
                {
                    "why_sell_status": "generated",
                    "why_sell_generated_at": datetime.utcnow().isoformat(),
                },
            )
            log(f"  Updated proposals record with why_sell_status=generated")
        except Exception as e:
            log(f"  Could not update proposals: {e}")

    log(f"\n  BATCH COMPLETE: {len(results['buyer_pitches'])} buyer pitches, {len(results['errors'])} errors")
    return results


# ─── Fallback Storage ─────────────────────────────────────────────────────────


def _store_in_proposals_fallback(company_id, record):
    """
    If why_sell_narratives table doesn't exist yet, store narratives as JSON
    inside the proposals table's why_sell_narratives column (JSONB field).
    """
    try:
        proposals = sb_get("proposals", f"company_id=eq.{company_id}&limit=1")
        if proposals:
            proposal_id = proposals[0]["id"]
            sb_update(
                "proposals",
                "id",
                proposal_id,
                {
                    "why_sell_narratives": json.dumps(record, default=str),
                    "why_sell_status": "generated",
                },
            )
            log(f"  Fallback: stored in proposals.why_sell_narratives for proposal {proposal_id}")
        else:
            log(f"  Fallback: no proposals row found for company_id={company_id}")
    except Exception as e:
        log(f"  Fallback storage failed: {e}")


# ─── CLI Entry Point ──────────────────────────────────────────────────────────


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python why_sell_engine.py why_sell <company_id> [entity]")
        print("  python why_sell_engine.py buyer_pitch <company_id> <buyer_id>")
        print("  python why_sell_engine.py batch <proposal_id>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "why_sell":
        company_id = sys.argv[2]
        entity = sys.argv[3] if len(sys.argv) > 3 else "next_chapter"
        result = generate_why_sell(company_id, entity=entity)
        if result:
            print("\n=== GENERATED NARRATIVES ===")
            for k in ["market_timing", "owner_lifecycle", "competitive_pressure", "value_maximization", "risk_of_waiting"]:
                print(f"\n--- {k.upper()} ---")
                print(result[k])

    elif cmd == "buyer_pitch":
        company_id = sys.argv[2]
        buyer_id = sys.argv[3]
        result = generate_buyer_pitch(company_id, buyer_id)
        if result:
            print("\n=== BUYER PITCH ===")
            print(result["buyer_pitch"])

    elif cmd == "batch":
        proposal_id = sys.argv[2]
        result = batch_generate(proposal_id)
        if result:
            print(f"\n=== BATCH COMPLETE ===")
            print(f"Company: {result['company_name']}")
            print(f"Buyer pitches: {len(result['buyer_pitches'])}")
            print(f"Errors: {result['errors']}")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
