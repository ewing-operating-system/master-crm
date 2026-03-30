"""
exa_client_v2.py — Optimized Exa.ai client for Next Chapter M&A Advisory
Uses curl subprocess (urllib blocked by Exa WAF/Cloudflare).
All 12 search templates pre-configured with per-template optimizations.

Drop-in replacement for lib/exa_client.py

Usage:
    from exa_client_v2 import ExaClient
    client = ExaClient()
    results = client.search("company_search", company_name="AquaScience Inc", city="Scottsdale", state="Arizona", vertical="water treatment")
    results = client.find_similar("https://example-target-company.com", num_results=20)
"""

import subprocess
import json
import os
import re
import time
from typing import Optional, Dict, Any, List

# ── API Key ──────────────────────────────────────────────
EXA_KEY = os.environ.get("EXA_API_KEY", "")

# ── SEO farms to always exclude ──────────────────────────
SEO_EXCLUDE = [
    "swottemplate.com", "portersfiveforce.com", "pestel-analysis.com",
    "matrixbcg.com", "template.net", "slideteam.net", "sketchbubble.com",
    "edrawmax.com", "sampletemplates.com", "creately.com",
]

# ── High-value financial sources ─────────────────────────
FINANCIAL_DOMAINS = [
    "sec.gov", "crunchbase.com", "pitchbook.com", "bloomberg.com",
    "reuters.com", "wsj.com", "ft.com", "ibisworld.com",
    "macrotrends.net", "zoominfo.com", "dnb.com",
]

TRANSCRIPT_DOMAINS = [
    "seekingalpha.com", "fool.com", "nasdaq.com",
    "businesswire.com", "prnewswire.com", "globenewswire.com",
]

LINKEDIN_DOMAINS = ["linkedin.com"]

NEWS_DOMAINS = [
    "reuters.com", "bloomberg.com", "wsj.com", "ft.com",
    "businesswire.com", "prnewswire.com", "globenewswire.com",
    "mergermarket.com", "dealogic.com",
]

# ══════════════════════════════════════════════════════════
# TEMPLATE CONFIGS — per-template optimizations
# ══════════════════════════════════════════════════════════
TEMPLATES = {

    # ── Template 1: Company Search ────────────────────────
    "company_search": {
        "query": "{company_name} {city} {state} {vertical} company",
        "type": "deep",
        "category": "company",
        "num_results": 8,
        "content_mode": "highlights",
        "max_characters": 2000,
        "use_autoprompt": True,
        "exclude_domains": SEO_EXCLUDE,
        "include_domains": [],
        "max_age_hours": None,
        "include_text": None,
    },

    # ── Template 2: Owner/Founder Search ──────────────────
    "owner_search": {
        "query": "{company_name} owner founder president {city}",
        "type": "auto",
        "category": "people",
        "num_results": 5,
        "content_mode": "highlights",
        "max_characters": 2000,
        "use_autoprompt": True,
        "exclude_domains": [],
        "include_domains": LINKEDIN_DOMAINS,
        "max_age_hours": None,
        "include_text": None,
    },

    # ── Template 3: Reviews and Reputation ────────────────
    "reviews_search": {
        "query": "{company_name} reviews BBB rating {city}",
        "type": "auto",
        "category": "news",
        "num_results": 5,
        "content_mode": "highlights",
        "max_characters": 2000,
        "use_autoprompt": False,
        "exclude_domains": SEO_EXCLUDE,
        "include_domains": [],
        "max_age_hours": None,
        "include_text": None,
    },

    # ── Template 4: Financial Signals ─────────────────────
    "financials_search": {
        "query": "{company_name} {city} employees revenue size",
        "type": "deep",
        "category": "company",
        "num_results": 8,
        "content_mode": "text",
        "max_characters": 5000,
        "use_autoprompt": True,
        "exclude_domains": SEO_EXCLUDE,
        "include_domains": FINANCIAL_DOMAINS,
        "max_age_hours": None,
        "include_text": None,
    },

    # ── Template 5: Industry M&A Activity ─────────────────
    "industry_ma": {
        "query": "{vertical} company acquisition multiples 2025 2026",
        "type": "auto",
        "category": "news",
        "num_results": 10,
        "content_mode": "highlights",
        "max_characters": 2000,
        "use_autoprompt": True,
        "exclude_domains": SEO_EXCLUDE,
        "include_domains": [],
        "max_age_hours": 48,
        "include_text": "acquisition",
    },

    # ── Template 6: Buyer Identification ──────────────────
    "buyer_search": {
        "query": "{vertical} companies acquired {state} 2024 2025 PE roll-up",
        "type": "auto",
        "category": "company",
        "num_results": 12,
        "content_mode": "highlights",
        "max_characters": 2000,
        "use_autoprompt": True,
        "exclude_domains": SEO_EXCLUDE,
        "include_domains": [],
        "max_age_hours": None,
        "include_text": None,
    },

    # ── Template 7: Earnings Call Quotes ──────────────────
    "earnings_call": {
        "query": "{company_name} CEO earnings call 2024 2025 strategy {topic}",
        "type": "deep",
        "category": None,
        "num_results": 8,
        "content_mode": "text",
        "max_characters": 5000,
        "use_autoprompt": False,
        "exclude_domains": SEO_EXCLUDE,
        "include_domains": TRANSCRIPT_DOMAINS,
        "max_age_hours": None,
        "include_text": None,
    },

    # ── Template 8: M&A Deal History ──────────────────────
    "ma_history": {
        "query": "{company_name} acquisition 2023 2024 2025 {topic}",
        "type": "deep",
        "category": "news",
        "num_results": 10,
        "content_mode": "text",
        "max_characters": 5000,
        "use_autoprompt": True,
        "exclude_domains": SEO_EXCLUDE,
        "include_domains": NEWS_DOMAINS,
        "max_age_hours": 720,
        "include_text": None,
    },

    # ── Template 9: Buyer Contact Search ──────────────────
    "buyer_contacts": {
        "query": "{company_name} VP Corporate Development M&A LinkedIn",
        "type": "auto",
        "category": "people",
        "num_results": 5,
        "content_mode": "highlights",
        "max_characters": 2000,
        "use_autoprompt": False,
        "exclude_domains": [],
        "include_domains": LINKEDIN_DOMAINS,
        "max_age_hours": None,
        "include_text": None,
    },

    # ── Template 10: Strategic Fit Signals ────────────────
    "strategic_fit": {
        "query": "{company_name} {topic} strategy investment thesis",
        "type": "deep",
        "category": None,
        "num_results": 8,
        "content_mode": "text",
        "max_characters": 5000,
        "use_autoprompt": True,
        "exclude_domains": SEO_EXCLUDE,
        "include_domains": [],
        "max_age_hours": None,
        "include_text": None,
    },

    # ── Template 11: Company Financials (Buyer) ───────────
    "company_financials": {
        "query": "{company_name} annual revenue employees company overview",
        "type": "deep",
        "category": "company",
        "num_results": 8,
        "content_mode": "text",
        "max_characters": 5000,
        "use_autoprompt": True,
        "exclude_domains": SEO_EXCLUDE,
        "include_domains": FINANCIAL_DOMAINS,
        "max_age_hours": None,
        "include_text": None,
    },

    # ── Template 12: Contact Enrichment ───────────────────
    "contact_enrichment": {
        "query": '"{owner_name}" "{company_name}" {city} {state} phone email contact LinkedIn',
        "type": "auto",
        "category": "people",
        "num_results": 5,
        "content_mode": "highlights",
        "max_characters": 2000,
        "use_autoprompt": False,
        "exclude_domains": [],
        "include_domains": [],
        "max_age_hours": None,
        "include_text": None,
    },
}

# ── Regex extractors for contact enrichment ──────────────
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?:\+1)?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
LINKEDIN_RE = re.compile(r"https?://(?:www\.)?linkedin\.com/in/[\w-]+/?")


class ExaClient:
    """Curl-based Exa.ai client with per-template optimization."""

    BASE_URL = "https://api.exa.ai"

    def __init__(self, api_key: Optional[str] = None, timeout: int = 60):
        self.api_key = api_key or EXA_KEY
        if not self.api_key:
            raise ValueError("EXA_API_KEY not set. Pass api_key= or set EXA_API_KEY env var.")
        self.timeout = timeout

    # ── Core curl caller ─────────────────────────────────
    def _call(self, endpoint: str, payload: dict) -> dict:
        """POST to Exa via curl subprocess. Returns parsed JSON."""
        url = f"{self.BASE_URL}{endpoint}"
        payload_json = json.dumps(payload)

        result = subprocess.run(
            [
                "curl", "-s", "-X", "POST", url,
                "-H", f"x-api-key: {self.api_key}",
                "-H", "Content-Type: application/json",
                "-d", payload_json,
            ],
            capture_output=True, text=True, timeout=self.timeout,
        )

        if result.returncode != 0:
            raise RuntimeError(f"curl failed (exit {result.returncode}): {result.stderr}")

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            raise RuntimeError(f"Invalid JSON from Exa: {result.stdout[:500]}")

        if "error" in data:
            raise RuntimeError(f"Exa API error: {data['error']}")

        return data

    # ── Template search ──────────────────────────────────
    def search(self, template_name: str, **kwargs) -> dict:
        """
        Run a search using a named template.

        Args:
            template_name: One of the 12 template keys (e.g. "company_search", "earnings_call")
            **kwargs: Template variables (company_name, city, state, vertical, topic, owner_name)

        Returns:
            Full Exa API response dict with results, costDollars, etc.
        """
        if template_name not in TEMPLATES:
            raise ValueError(f"Unknown template: {template_name}. Valid: {list(TEMPLATES.keys())}")

        cfg = TEMPLATES[template_name]
        query = cfg["query"].format(**kwargs)

        payload: Dict[str, Any] = {
            "query": query,
            "type": cfg["type"],
            "numResults": cfg["num_results"],
            "useAutoprompt": cfg["use_autoprompt"],
        }

        # Category (skip for None — lets Exa auto-detect)
        if cfg["category"]:
            payload["category"] = cfg["category"]

        # Content mode: highlights vs full text
        if cfg["content_mode"] == "highlights":
            payload["contents"] = {"highlights": {"maxCharacters": cfg["max_characters"]}}
        else:
            payload["contents"] = {"text": {"maxCharacters": cfg["max_characters"]}}

        # Domain filtering
        if cfg["include_domains"]:
            payload["includeDomains"] = cfg["include_domains"]
        if cfg["exclude_domains"]:
            payload["excludeDomains"] = cfg["exclude_domains"]

        # Freshness
        if cfg["max_age_hours"] is not None:
            payload["maxAgeHours"] = cfg["max_age_hours"]

        # Text filter
        if cfg["include_text"]:
            payload["includeText"] = cfg["include_text"]

        return self._call("/search", payload)

    # ── Raw search (custom query, no template) ───────────
    def raw_search(
        self,
        query: str,
        search_type: str = "auto",
        num_results: int = 10,
        max_characters: int = 3000,
        content_mode: str = "text",
        category: Optional[str] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        max_age_hours: Optional[int] = None,
        include_text: Optional[str] = None,
        use_autoprompt: bool = True,
    ) -> dict:
        """Run a fully custom search outside the template system."""
        payload: Dict[str, Any] = {
            "query": query,
            "type": search_type,
            "numResults": num_results,
            "useAutoprompt": use_autoprompt,
        }
        if category:
            payload["category"] = category
        if content_mode == "highlights":
            payload["contents"] = {"highlights": {"maxCharacters": max_characters}}
        else:
            payload["contents"] = {"text": {"maxCharacters": max_characters}}
        if include_domains:
            payload["includeDomains"] = include_domains
        if exclude_domains:
            payload["excludeDomains"] = exclude_domains
        if max_age_hours is not None:
            payload["maxAgeHours"] = max_age_hours
        if include_text:
            payload["includeText"] = include_text

        return self._call("/search", payload)

    # ── findSimilar — NEW ────────────────────────────────
    def find_similar(
        self,
        url: str,
        num_results: int = 20,
        category: Optional[str] = "company",
        exclude_domains: Optional[List[str]] = None,
        max_characters: int = 2000,
    ) -> dict:
        """
        Find companies/pages similar to a given URL.
        Huge for buyer identification — feed target company URL, get 20 similar companies.
        """
        payload: Dict[str, Any] = {
            "url": url,
            "numResults": num_results,
            "contents": {"highlights": {"maxCharacters": max_characters}},
        }
        if category:
            payload["category"] = category
        if exclude_domains:
            payload["excludeDomains"] = exclude_domains

        return self._call("/findSimilar", payload)

    # ── Contact extraction helpers ───────────────────────
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        return list(set(EMAIL_RE.findall(text)))

    @staticmethod
    def extract_phones(text: str) -> List[str]:
        return list(set(PHONE_RE.findall(text)))

    @staticmethod
    def extract_linkedin(text: str) -> List[str]:
        return list(set(LINKEDIN_RE.findall(text)))

    @staticmethod
    def extract_contacts(text: str) -> dict:
        return {
            "emails": ExaClient.extract_emails(text),
            "phones": ExaClient.extract_phones(text),
            "linkedin": ExaClient.extract_linkedin(text),
        }

    # ── Convenience: run full buyer intel suite ──────────
    def buyer_intel(self, company_name: str, topic: str, delay: float = 0.5) -> dict:
        """
        Run all 5 buyer intelligence templates for one buyer.
        Returns dict with keys: earnings, history, contacts, financials, strategy
        Cost: ~$0.035-$0.060 depending on deep vs auto templates.
        """
        results = {}
        templates = [
            ("earnings", "earnings_call", {"company_name": company_name, "topic": topic}),
            ("history", "ma_history", {"company_name": company_name, "topic": topic}),
            ("contacts", "buyer_contacts", {"company_name": company_name}),
            ("financials", "company_financials", {"company_name": company_name}),
            ("strategy", "strategic_fit", {"company_name": company_name, "topic": topic}),
        ]
        for key, template, kwargs in templates:
            try:
                results[key] = self.search(template, **kwargs)
            except Exception as e:
                results[key] = {"error": str(e)}
            time.sleep(delay)

        return results

    # ── Convenience: run full sell-side dossier suite ────
    def seller_dossier(self, company_name: str, city: str, state: str, vertical: str, delay: float = 0.5) -> dict:
        """
        Run all sell-side templates for one company.
        Returns dict with keys: company, owner, reviews, financials
        Cost: ~$0.028-$0.050
        """
        results = {}
        base = {"company_name": company_name, "city": city, "state": state}
        templates = [
            ("company", "company_search", {**base, "vertical": vertical}),
            ("owner", "owner_search", {**base}),
            ("reviews", "reviews_search", {**base}),
            ("financials", "financials_search", {**base}),
        ]
        for key, template, kwargs in templates:
            try:
                results[key] = self.search(template, **kwargs)
            except Exception as e:
                results[key] = {"error": str(e)}
            time.sleep(delay)

        return results

    # ── Cost estimator ───────────────────────────────────
    @staticmethod
    def estimate_cost(template_name: str) -> float:
        """Estimate per-search cost based on template type."""
        cfg = TEMPLATES.get(template_name, {})
        search_type = cfg.get("type", "auto")
        num_results = cfg.get("num_results", 5)

        # Base cost per 1k requests
        base_per_1k = {"auto": 7, "fast": 7, "instant": 5, "deep": 12, "deep-reasoning": 15}.get(search_type, 7)
        base_cost = base_per_1k / 1000

        # Extra results cost ($1 per 1k for each result beyond 10)
        extra = max(0, num_results - 10)
        extra_cost = (extra / 1000)

        return round(base_cost + extra_cost, 4)


# ══════════════════════════════════════════════════════════
# Quick test when run directly
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("exa_client_v2 — Template configs loaded:")
    print(f"  Templates: {len(TEMPLATES)}")
    for name, cfg in TEMPLATES.items():
        cost = ExaClient.estimate_cost(name)
        print(f"  {name:25s} | type={cfg['type']:6s} | n={cfg['num_results']:2d} | "
              f"mode={cfg['content_mode']:10s} | category={str(cfg['category']):8s} | ~${cost:.4f}/search")

    print(f"\n  SEO domains excluded globally: {len(SEO_EXCLUDE)}")
    print(f"  Financial domains available:   {len(FINANCIAL_DOMAINS)}")
    print(f"  Transcript domains available:  {len(TRANSCRIPT_DOMAINS)}")

    # Cost projection
    monthly_searches = {
        "company_search": 150, "owner_search": 150, "reviews_search": 150,
        "financials_search": 150, "industry_ma": 150, "buyer_search": 150,
        "earnings_call": 750, "ma_history": 750, "buyer_contacts": 750,
        "company_financials": 750, "strategic_fit": 750, "contact_enrichment": 200,
    }
    total_cost = sum(ExaClient.estimate_cost(t) * count for t, count in monthly_searches.items())
    total_searches = sum(monthly_searches.values())
    print(f"\n  Projected monthly: {total_searches:,} searches = ${total_cost:.2f}/month")
