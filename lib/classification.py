"""
Entity Classification Engine — Deterministic Decision Tree
Implements the Entity Classification Guide as pure Python.

Priority order: Intent → Company Type → Person Role → Channel
Fail-safe: Never force classification. No tag if confidence < 2.

Entity values: next_chapter, and_capital, revsup, the_forge, biolev, sea_sweet, precision_exploration
"""

import re

# ─── Keyword dictionaries ────────────────────────────────────────────────────

AND_CAPITAL_KEYWORDS = {
    # Industry
    "healthcare", "hospital", "wellness", "longevity", "health-tech", "bio-tech",
    "med-tech", "medical device", "wound care", "wound prevention", "functional beverages",
    "wellness properties", "integrated platforms", "energy", "hydrocarbons", "midstream",
    "renewables", "energy transition", "orri", "royalty interest", "minerals",
    "critical minerals", "gold", "brownfield", "central asia", "oil and gas", "oil & gas",
    # Finance / LP
    "family office", "lp", "limited partner", "fund", "institutional investor",
    "accredited investor", "qualified purchaser", "capital raise", "subscription",
    "allocation", "endowment", "pension", "ria", "wealth advisor",
    # Company names in AND orbit
    "euchee valley", "little rock heart", "fiomet", "geosense", "smartfit", "opolee",
    "spiga capital", "andean capital",
}

NEXT_CHAPTER_KEYWORDS = {
    # Industry
    "home services", "plumbing", "hvac", "roofing", "pest control", "water treatment",
    "flooring", "steel", "concrete", "precast", "trades", "contractor",
    "electric", "electrical", "electrician", "termite", "pest", "air conditioning",
    "heating", "cooling", "foundation", "crawl space", "environmental",
    # Transaction
    "sell my business", "business sale", "succession", "exit planning", "retirement",
    "business acquisition", "business broker", "acquirer", "buyer", "seller",
    "sde", "seller's discretionary earnings", "business valuation",
    "main street", "lower mid-market",
    # Company names in NC orbit
    "springer floor", "air control", "aquascience", "hr.com", "weiser concrete",
    "design precast", "prasab",
}

REVSUP_KEYWORDS = {
    "saas", "software", "vc-backed", "venture-backed", "startup", "tech company",
    "series a", "series b", "growth stage", "arr", "mrr", "recurring revenue",
    "sales hiring", "recruiting", "headhunter", "contingent search",
    "talent acquisition", "candidate", "placement",
}

INTENT_HIRING = {
    "hiring", "recruiting", "headcount", "open roles", "candidates", "placement",
    "talent acquisition", "search fee", "contingent search",
}

INTENT_TRANSACTION = {
    "sell my business", "acquisition", "buyer", "seller", "valuation", "exit",
    "roll-up", "rollup", "succession", "sell-side", "buy-side", "m&a advisory",
    "business sale", "business broker",
}

INTENT_CAPITAL = {
    "investing", "capital raise", "fundraising", "fund", "lp", "limited partner",
    "allocation", "subscription", "endowment", "pension", "ria",
    "family office", "carried interest", "management fee", "preferred return",
}

# Person routing
PERSON_ENTITY_MAP = {
    "chris rex": "and_capital",      # ONLY AND Capital
    "teruel carrasco": "and_capital",
    "rod heard": "and_capital",
    "denise brown": "and_capital",
    "joe park": "and_capital",
    "loren brink": "and_capital",
}

PERSON_NEVER_MAP = {
    "john kelly": {"and_capital"},    # NEVER AND Capital
    "ewing gillaspy": {"revsup"},     # NEVER RevsUp in Salesfinity
}

# Standalone entity keywords
STANDALONE_KEYWORDS = {
    "boomerang": "the_forge",
    "biolev": "biolev",
    "sea sweet": "sea_sweet",
    "precision exploration": "precision_exploration",
    "nmr science": "precision_exploration",
    # Note: "pec" removed — too many false positives (specialist, inspection, etc.)
    # Use "precision exploration" as the keyword instead
}


def _normalize(text):
    """Lowercase, strip, collapse whitespace."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', str(text).lower().strip())


def _keyword_score(text, keyword_set):
    """Count how many keywords from the set appear in text. Each match = +1."""
    text = _normalize(text)
    score = 0
    for kw in keyword_set:
        if kw in text:
            score += 1
    return score


def classify_entity(
    company_name=None,
    company_description=None,
    person_name=None,
    person_title=None,
    intent=None,
    industry=None,
    campaign_id=None,
    raw_text=None,
):
    """
    Classify a record into an entity using the deterministic decision tree.

    Returns: {
        "entity": str or None,
        "sub_type": str or None,
        "confidence": float,
        "reason": str,
        "method": str,  # which step resolved it
    }
    """
    # Combine all text signals
    all_text = _normalize(" ".join(filter(None, [
        company_name, company_description, person_name, person_title,
        intent, industry, campaign_id, raw_text,
    ])))

    # ─── Step 0: Campaign prefix (instant resolution) ────────────────────
    if campaign_id:
        prefix = campaign_id.upper().split("-")[0] if "-" in campaign_id else ""
        if prefix == "NC":
            return {"entity": "next_chapter", "sub_type": _nc_subtype(all_text), "confidence": 3.0, "reason": f"Campaign prefix NC: {campaign_id}", "method": "campaign_prefix"}
        if prefix == "AND":
            return {"entity": "and_capital", "sub_type": _and_subtype(all_text), "confidence": 3.0, "reason": f"Campaign prefix AND: {campaign_id}", "method": "campaign_prefix"}
        if prefix in ("RU", "REV"):
            return {"entity": "revsup", "sub_type": "recruiting", "confidence": 3.0, "reason": f"Campaign prefix RU: {campaign_id}", "method": "campaign_prefix"}
        if prefix == "FORGE":
            return {"entity": "the_forge", "sub_type": None, "confidence": 3.0, "reason": f"Campaign prefix FORGE: {campaign_id}", "method": "campaign_prefix"}
        if prefix == "BIOLEV":
            return {"entity": "biolev", "sub_type": None, "confidence": 3.0, "reason": f"Campaign prefix BIOLEV: {campaign_id}", "method": "campaign_prefix"}
        if prefix == "SEASWEET":
            return {"entity": "sea_sweet", "sub_type": None, "confidence": 3.0, "reason": f"Campaign prefix SEASWEET: {campaign_id}", "method": "campaign_prefix"}
        if prefix == "PEC":
            return {"entity": "precision_exploration", "sub_type": None, "confidence": 3.0, "reason": f"Campaign prefix PEC: {campaign_id}", "method": "campaign_prefix"}

    # ─── Step 0.5: Standalone entity keywords ────────────────────────────
    for kw, entity in STANDALONE_KEYWORDS.items():
        if kw in all_text:
            return {"entity": entity, "sub_type": None, "confidence": 2.5, "reason": f"Standalone keyword: {kw}", "method": "standalone_keyword"}

    # ─── Step 0.7: Person hard-routing ───────────────────────────────────
    if person_name:
        pn = _normalize(person_name)
        for name, entity in PERSON_ENTITY_MAP.items():
            if name in pn:
                return {"entity": entity, "sub_type": None, "confidence": 2.5, "reason": f"Person {name} is exclusively {entity}", "method": "person_routing"}

    # ─── Step 1: Intent — Hiring? ────────────────────────────────────────
    hiring_score = _keyword_score(all_text, INTENT_HIRING)
    if hiring_score >= 2:
        return {"entity": "revsup", "sub_type": "recruiting", "confidence": 2.0 + hiring_score * 0.5, "reason": f"Strong hiring intent ({hiring_score} signals)", "method": "intent_hiring"}

    # ─── Step 2: Intent — Transaction? ───────────────────────────────────
    txn_score = _keyword_score(all_text, INTENT_TRANSACTION)
    if txn_score >= 2:
        return {"entity": "next_chapter", "sub_type": _nc_subtype(all_text), "confidence": 2.0 + txn_score * 0.5, "reason": f"Strong transaction intent ({txn_score} signals)", "method": "intent_transaction"}

    # ─── Step 3: Intent — Capital? ───────────────────────────────────────
    capital_score = _keyword_score(all_text, INTENT_CAPITAL)
    if capital_score >= 2:
        sub = "lp" if any(k in all_text for k in ["lp", "family office", "ria", "allocator", "endowment"]) else "investment"
        return {"entity": "and_capital", "sub_type": sub, "confidence": 2.0 + capital_score * 0.5, "reason": f"Strong capital intent ({capital_score} signals)", "method": "intent_capital"}

    # ─── Step 4: Company type fallback ───────────────────────────────────
    nc_score = _keyword_score(all_text, NEXT_CHAPTER_KEYWORDS)
    and_score = _keyword_score(all_text, AND_CAPITAL_KEYWORDS)
    ru_score = _keyword_score(all_text, REVSUP_KEYWORDS)

    scores = {"next_chapter": nc_score, "and_capital": and_score, "revsup": ru_score}

    # Disambiguation: if NC and AND both score, check if this looks like a trades company
    # "Energy Solutions Inc" is a contractor, not an energy fund asset
    if nc_score > 0 and and_score > 0:
        trades_signals = sum(1 for kw in ["llc", "inc", "co.", "services", "service", "company",
                                           "electric", "plumbing", "hvac", "roofing", "pest",
                                           "heating", "cooling", "air conditioning", "repair"]
                            if kw in all_text)
        if trades_signals >= 1:
            scores["and_capital"] = max(0, scores["and_capital"] - 1)

    best_entity = max(scores, key=scores.get)
    best_score = scores[best_entity]

    # Only classify if score >= 2 (moderate+ signal)
    if best_score >= 2:
        # Check person-never rules
        if person_name:
            pn = _normalize(person_name)
            for name, blocked in PERSON_NEVER_MAP.items():
                if name in pn and best_entity in blocked:
                    # Remove blocked, try next best
                    del scores[best_entity]
                    best_entity = max(scores, key=scores.get)
                    best_score = scores[best_entity]
                    if best_score < 2:
                        return {"entity": None, "sub_type": None, "confidence": best_score, "reason": f"Person {name} blocked from {best_entity}, fallback below threshold", "method": "person_block_fallback"}

        sub_type = None
        if best_entity == "next_chapter":
            sub_type = _nc_subtype(all_text)
        elif best_entity == "and_capital":
            sub_type = _and_subtype(all_text)
        elif best_entity == "revsup":
            sub_type = "recruiting" if hiring_score > 0 else None

        return {"entity": best_entity, "sub_type": sub_type, "confidence": 1.0 + best_score * 0.5, "reason": f"Industry match: {best_entity} ({best_score} keywords)", "method": "company_type_fallback"}

    # ─── Step 5: Single weak signal ──────────────────────────────────────
    if best_score == 1:
        return {"entity": best_entity, "sub_type": None, "confidence": 1.0, "reason": f"Weak signal: {best_entity} (1 keyword)", "method": "weak_signal"}

    # ─── Step 6: No classification ───────────────────────────────────────
    return {"entity": None, "sub_type": None, "confidence": 0.0, "reason": "No entity signals found", "method": "no_match"}


def _nc_subtype(text):
    """Determine Next Chapter sub-type: sell-side or buy-side."""
    if any(k in text for k in ["seller", "sell my", "sell-side", "retirement", "exit", "succession"]):
        return "sell_side"
    if any(k in text for k in ["buyer", "buy-side", "acquirer", "acquisition", "roll-up"]):
        return "buy_side"
    return None


def _and_subtype(text):
    """Determine AND Capital sub-type: LP or investment."""
    if any(k in text for k in ["lp", "family office", "ria", "allocator", "endowment", "pension", "fund-of-funds", "capital raise"]):
        return "lp"
    if any(k in text for k in ["hospital", "energy", "medical", "device", "wellness", "mining"]):
        return "investment"
    return None


def classify_batch(records, text_fields=None):
    """
    Classify a batch of records. Each record is a dict.
    text_fields: list of field names to combine for classification.
    Returns list of (record, classification) tuples.
    """
    if text_fields is None:
        text_fields = ["company_name", "owner_name", "category", "vertical", "industry", "description", "title"]

    results = []
    for record in records:
        raw_text = " ".join(str(record.get(f, "")) for f in text_fields if record.get(f))
        classification = classify_entity(
            company_name=record.get("company_name"),
            person_name=record.get("owner_name") or record.get("person_name") or record.get("full_name"),
            person_title=record.get("title") or record.get("owner_title"),
            industry=record.get("category") or record.get("vertical") or record.get("industry"),
            raw_text=raw_text,
        )
        results.append((record, classification))
    return results


# ─── Self-test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        {"company_name": "ABC Plumbing", "industry": "plumbing", "expected": "next_chapter"},
        {"company_name": "Smith HVAC Services", "industry": "hvac", "expected": "next_chapter"},
        {"company_name": "Fiomet Medical Device", "industry": "medical device", "expected": "and_capital"},
        {"company_name": "Acme Family Office", "industry": "family office", "expected": "and_capital"},
        {"company_name": "TechCo SaaS", "intent": "hiring recruiting headcount", "expected": "revsup"},
        {"person_name": "Chris Rex", "company_name": "Anything", "expected": "and_capital"},
        {"person_name": "John Kelly", "company_name": "Some Plumber", "industry": "plumbing", "expected": "next_chapter"},
        {"campaign_id": "NC-SELL-LETTER", "expected": "next_chapter"},
        {"campaign_id": "AND-LP-CALL", "expected": "and_capital"},
        {"company_name": "Boomerang Athletics", "expected": "the_forge"},
        {"company_name": "Random Corp", "expected": None},  # Should not classify
    ]

    passed = 0
    for t in tests:
        expected = t.pop("expected")
        result = classify_entity(**t)
        status = "PASS" if result["entity"] == expected else "FAIL"
        if status == "PASS":
            passed += 1
        print(f"  {status}: expected={expected}, got={result['entity']}, confidence={result['confidence']:.1f}, reason={result['reason']}")

    print(f"\n{passed}/{len(tests)} tests passed")
