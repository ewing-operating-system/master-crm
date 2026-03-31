#!/usr/bin/env python3
"""
Buyer Page Generator — Rich HTML from story_narrative
=====================================================
Parses structured narratives (9 sections) into rich, styled HTML pages.
Falls back to single-block display for unstructured narratives.
"""

import psycopg2
import psycopg2.extras
import json
import os
import re
import sys
import datetime
import html as html_mod

# --- Config ---
DB_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:6543/postgres")
OUTPUT_DIR = os.path.expanduser("~/Projects/master-crm/data/buyer-1pagers")
WEB_DIR = os.path.expanduser("~/Projects/master-crm-web/public")
LOG_FILE = os.path.expanduser("~/Projects/dossier-pipeline/data/audit-logs/buyer_page_fix.log")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(msg):
    ts = datetime.datetime.now().isoformat()
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def slugify(s):
    if not s:
        return "unknown"
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')[:60]


def esc(text):
    """HTML-escape text."""
    if not text:
        return ""
    return html_mod.escape(str(text))


def is_structured(narrative):
    """Detect if narrative has structured sections."""
    if not narrative:
        return False
    indicators = ["**1.", "FIT NARRATIVE", "GOLDEN NUGGETS", "**2.", "CEO VISION", "M&A APPETITE",
                   "COMPETITIVE MOAT", "KEY EARNINGS QUOTES", "BUSINESS MODEL INTEGRATION"]
    return any(ind in narrative for ind in indicators)


def parse_sections(narrative):
    """Parse structured narrative into named sections.

    Numbered sections (**1. TITLE**, **2. TITLE**) and known top-level headers
    like **KEY EARNINGS QUOTES** are primary sections.
    Sub-headers like **THE STRATEGIC LOGIC** within a numbered section
    are kept as content (not split out as separate sections).
    """
    sections = {}
    if not narrative:
        return sections

    # Known top-level section names (unnumbered but primary)
    TOP_LEVEL_NAMES = {
        "KEY EARNINGS QUOTES", "EARNINGS QUOTES", "KEY QUOTES",
    }

    # Match all bold headers: **N. TITLE** or **TITLE**
    header_pattern = re.compile(
        r'^\*\*(?:(\d+)\.\s+)?([^*]+)\*\*\s*$',
        re.MULTILINE
    )

    headers = list(header_pattern.finditer(narrative))
    if not headers:
        return {"full": narrative}

    # Identify which headers are primary (numbered or known top-level)
    primary_indices = []
    for i, match in enumerate(headers):
        num = match.group(1)
        title = match.group(2).strip().upper()
        if num is not None:
            # Numbered section -> always primary
            primary_indices.append(i)
        elif title in TOP_LEVEL_NAMES or any(title.startswith(t) for t in TOP_LEVEL_NAMES):
            primary_indices.append(i)

    if not primary_indices:
        return {"full": narrative}

    for pi_idx, header_idx in enumerate(primary_indices):
        match = headers[header_idx]
        num = match.group(1)
        title = match.group(2).strip()

        start = match.end()
        # End is the start of the next primary section (or end of narrative)
        if pi_idx + 1 < len(primary_indices):
            end = headers[primary_indices[pi_idx + 1]].start()
        else:
            end = len(narrative)
        content = narrative[start:end].strip()

        key = title.upper().strip()
        sections[key] = {
            "number": num,
            "title": title,
            "content": content
        }

    return sections


def parse_golden_nuggets(content):
    """Parse golden nuggets section into individual nuggets."""
    nuggets = []
    # Split on **Nugget N** patterns
    nugget_pattern = re.compile(r'\*\*Nugget\s+(\d+)\*\*\s*[-\u2014\u2013]?\s*(.+?)(?=\*\*Nugget|\Z)', re.DOTALL)
    matches = nugget_pattern.findall(content)

    for num, block in matches:
        nugget = {"number": num, "speaker": "", "quote": "", "opener": "", "why": ""}

        # Extract speaker name (after the dash)
        speaker_match = re.match(r'([A-Z][a-zA-Z\s]+?)(?:\n|$)', block.strip())
        if speaker_match:
            nugget["speaker"] = speaker_match.group(1).strip()

        # Extract quote (in > blockquote)
        quote_match = re.search(r'>\s*["\u201c]?(.+?)["\u201d]?\s*$', block, re.MULTILINE)
        if quote_match:
            nugget["quote"] = quote_match.group(1).strip().strip('""\u201c\u201d')

        # Extract opener
        opener_match = re.search(r'\*\*Opener:\*\*\s*(.+?)(?=\*Why it works|\*\*Why|\n\n|\Z)', block, re.DOTALL)
        if opener_match:
            nugget["opener"] = opener_match.group(1).strip()

        # Extract why it works
        why_match = re.search(r'\*(?:Why it works|Why it works:)\*[:\s]*(.+?)(?=\n\n|\Z)', block, re.DOTALL)
        if not why_match:
            why_match = re.search(r'\*\*Why it works:\*\*\s*(.+?)(?=\n\n|\Z)', block, re.DOTALL)
        if why_match:
            nugget["why"] = why_match.group(1).strip()

        nuggets.append(nugget)

    return nuggets


def parse_earnings_quotes(content):
    """Parse KEY EARNINGS QUOTES into individual quotes with attribution."""
    quotes = []
    # Pattern: - **Speaker** (Quarter Year): "quote text"
    quote_pattern = re.compile(
        r'-\s*\*\*(.+?)\*\*\s*\(([^)]+)\):\s*["\u201c](.+?)["\u201d]?\s*$',
        re.MULTILINE
    )
    for match in quote_pattern.finditer(content):
        quotes.append({
            "speaker": match.group(1).strip(),
            "period": match.group(2).strip(),
            "quote": match.group(3).strip().rstrip('""\u201c\u201d')
        })
    return quotes


def render_paragraphs(text):
    """Convert text with double-newlines to <p> tags, preserving inline bold/italic."""
    if not text:
        return ""
    paragraphs = re.split(r'\n\n+', text.strip())
    html_parts = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        # Skip sub-headers that are bold
        if re.match(r'^\*\*[A-Z][A-Z\s]+\*\*$', p):
            title = p.strip('*').strip()
            html_parts.append(f'<h3 style="font-size:14px;font-weight:600;color:#58a6ff;margin:16px 0 8px;">{esc(title)}</h3>')
            continue
        # Convert **bold** to <strong>
        p = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', p)
        # Convert *italic* to <em>
        p = re.sub(r'\*(.+?)\*', r'<em>\1</em>', p)
        # Convert > quotes to styled blockquote inline
        if p.startswith('>'):
            p = p.lstrip('>').strip()
            html_parts.append(f'<blockquote style="border-left:3px solid #58a6ff;padding-left:16px;margin:12px 0;font-style:italic;color:#8b949e;">{p}</blockquote>')
        else:
            html_parts.append(f'<p>{p}</p>')
    return '\n'.join(html_parts)


def build_contacts_table(contacts):
    """Build HTML table from verified_contacts JSONB."""
    if not contacts:
        return ""
    rows = ""
    for c in contacts:
        name = esc(c.get("name", ""))
        title = esc(c.get("title", ""))
        company = esc(c.get("company", ""))
        url = c.get("url", "")
        status = c.get("status", "")
        confidence = c.get("confidence", "")

        status_color = "#27ae60" if status == "VERIFIED" else "#f39c12" if status == "NEW" else "#8b949e"
        linkedin_link = f'<a href="{esc(url)}" target="_blank" style="color:#58a6ff;">LinkedIn</a>' if url else ""

        rows += f"""<tr>
            <td style="font-weight:600;color:#f0f6fc;">{name}</td>
            <td>{title}</td>
            <td>{company}</td>
            <td><span style="color:{status_color};font-weight:600;">{esc(status)}</span></td>
            <td>{esc(confidence)}</td>
            <td>{linkedin_link}</td>
        </tr>"""

    return f"""<table>
        <thead><tr>
            <th>Name</th><th>Title</th><th>Company</th><th>Status</th><th>Confidence</th><th>LinkedIn</th>
        </tr></thead>
        <tbody>{rows}</tbody>
    </table>"""


def generate_structured_html(buyer, seller_info, sections, narrative):
    """Generate rich HTML page from parsed structured sections."""
    buyer_name = esc(buyer.get("buyer_company_name", "Unknown"))
    buyer_type = esc(buyer.get("buyer_type", ""))
    fit_score = buyer.get("fit_score", "")
    contact_name = esc(buyer.get("buyer_contact_name", ""))
    buyer_city = buyer.get("buyer_city", "")
    buyer_state = buyer.get("buyer_state", "")
    location = f"{buyer_city}, {buyer_state}" if buyer_city and buyer_state else (buyer_city or buyer_state or "")
    revenue = esc(buyer.get("buyer_revenue", "") or "")
    employees = esc(buyer.get("buyer_employee_count", "") or "")

    seller_name = esc(seller_info.get("company_name", ""))
    seller_owner = esc(seller_info.get("owner_name", ""))
    seller_vertical = esc(seller_info.get("vertical", ""))
    seller_revenue = esc(seller_info.get("estimated_revenue", ""))

    # Fit score badge color
    try:
        score_val = int(float(str(fit_score)))
    except (ValueError, TypeError):
        score_val = 0
    score_color = "#27ae60" if score_val >= 8 else "#f39c12" if score_val >= 6 else "#e74c3c" if score_val >= 1 else "#30363d"

    now = datetime.datetime.now().strftime('%B %d, %Y')

    # Build section cards
    cards_html = ""

    # --- Section 1: Strategic Fit (FIT NARRATIVE) ---
    fit_keys = [k for k in sections if "FIT NARRATIVE" in k or "FIT" in k]
    if fit_keys:
        fit_content = sections[fit_keys[0]]["content"]
        cards_html += f"""
    <div class="card" id="strategic-fit">
        <h2>Strategic Fit</h2>
        <div class="narrative-content">{render_paragraphs(fit_content)}</div>
    </div>"""

    # --- Section: Asset-to-Product Mapping (if present as subsection) ---
    asset_keys = [k for k in sections if "ASSET" in k]
    if asset_keys:
        cards_html += f"""
    <div class="card" id="asset-mapping">
        <h2>Asset-to-Product Mapping</h2>
        <div class="narrative-content">{render_paragraphs(sections[asset_keys[0]]["content"])}</div>
    </div>"""

    # --- Section: Business Model Integration ---
    bmi_keys = [k for k in sections if "BUSINESS MODEL" in k]
    if bmi_keys:
        cards_html += f"""
    <div class="card" id="business-model">
        <h2>Business Model Integration</h2>
        <div class="narrative-content">{render_paragraphs(sections[bmi_keys[0]]["content"])}</div>
    </div>"""

    # --- Section: Competitive Moat / Urgency (RED BORDER) ---
    moat_keys = [k for k in sections if "COMPETITIVE" in k or "MOAT" in k]
    if moat_keys:
        cards_html += f"""
    <div class="card urgency-card" id="competitive-urgency">
        <h2>Competitive Urgency</h2>
        <div class="narrative-content">{render_paragraphs(sections[moat_keys[0]]["content"])}</div>
    </div>"""

    # --- Section: Golden Nuggets ---
    nugget_keys = [k for k in sections if "GOLDEN" in k or "NUGGET" in k]
    if nugget_keys:
        nugget_content = sections[nugget_keys[0]]["content"]
        nuggets = parse_golden_nuggets(nugget_content)
        if nuggets:
            nuggets_html = ""
            for n in nuggets:
                nuggets_html += f"""
        <div class="nugget-card">
            <div class="nugget-header">Nugget {esc(n["number"])}{" - " + esc(n["speaker"]) if n["speaker"] else ""}</div>
            {f'<blockquote class="ceo-quote">&ldquo;{esc(n["quote"])}&rdquo;</blockquote>' if n["quote"] else ""}
            {f'<div class="nugget-opener"><div class="opener-label">OPENER</div><p>{esc(n["opener"])}</p></div>' if n["opener"] else ""}
            {f'<div class="nugget-why"><strong>Why it works:</strong> {esc(n["why"])}</div>' if n["why"] else ""}
        </div>"""
            cards_html += f"""
    <div class="card" id="golden-nuggets">
        <h2>Golden Nuggets -- Cold Call Openers</h2>
        {nuggets_html}
    </div>"""
        else:
            # Fallback: render as paragraphs
            cards_html += f"""
    <div class="card" id="golden-nuggets">
        <h2>Golden Nuggets -- Cold Call Openers</h2>
        <div class="narrative-content">{render_paragraphs(nugget_content)}</div>
    </div>"""

    # --- Section: CEO Vision ---
    vision_keys = [k for k in sections if "CEO VISION" in k or "VISION" in k.replace("COMPETITIVE", "")]
    # filter out competitive
    vision_keys = [k for k in vision_keys if "COMPETITIVE" not in k]
    if vision_keys:
        cards_html += f"""
    <div class="card" id="ceo-vision">
        <h2>CEO Vision &amp; Strategy</h2>
        <div class="narrative-content">{render_paragraphs(sections[vision_keys[0]]["content"])}</div>
    </div>"""

    # --- Section: M&A Appetite ---
    ma_keys = [k for k in sections if "M&A" in k or "APPETITE" in k]
    if ma_keys:
        cards_html += f"""
    <div class="card" id="ma-appetite">
        <h2>M&amp;A Appetite</h2>
        <div class="narrative-content">{render_paragraphs(sections[ma_keys[0]]["content"])}</div>
    </div>"""

    # --- Section: Challenges & Headwinds ---
    challenge_keys = [k for k in sections if "CHALLENGE" in k or "HEADWIND" in k]
    if challenge_keys:
        cards_html += f"""
    <div class="card" id="challenges">
        <h2>Challenges &amp; Headwinds</h2>
        <div class="narrative-content">{render_paragraphs(sections[challenge_keys[0]]["content"])}</div>
    </div>"""

    # --- Section: Key Earnings Quotes ---
    earnings_keys = [k for k in sections if "EARNINGS" in k or "QUOTES" in k]
    # filter out golden nuggets
    earnings_keys = [k for k in earnings_keys if "GOLDEN" not in k and "NUGGET" not in k]
    if earnings_keys:
        eq_content = sections[earnings_keys[0]]["content"]
        quotes = parse_earnings_quotes(eq_content)
        if quotes:
            quotes_html = ""
            for q in quotes:
                quotes_html += f"""
        <div class="earnings-quote">
            <blockquote class="ceo-quote">&ldquo;{esc(q["quote"])}&rdquo;</blockquote>
            <div class="quote-attribution">-- {esc(q["speaker"])}, {esc(q["period"])}</div>
        </div>"""
            cards_html += f"""
    <div class="card" id="earnings-quotes">
        <h2>Key Earnings Quotes</h2>
        {quotes_html}
    </div>"""
        else:
            cards_html += f"""
    <div class="card" id="earnings-quotes">
        <h2>Key Earnings Quotes</h2>
        <div class="narrative-content">{render_paragraphs(eq_content)}</div>
    </div>"""

    # --- Section: Verified Contacts ---
    contacts = buyer.get("verified_contacts")
    if contacts:
        contacts_html = build_contacts_table(contacts)
        cards_html += f"""
    <div class="card" id="verified-contacts">
        <h2>Verified Contacts</h2>
        {contacts_html}
    </div>"""

    # --- Section: Approach Strategy ---
    call_opener = buyer.get("call_opener", "")
    outreach_seq = buyer.get("outreach_sequence")
    if call_opener or outreach_seq:
        approach_html = ""
        if call_opener:
            approach_html += f"""
        <div class="approach-opener">
            <div class="opener-label">CALL OPENER</div>
            <p>{esc(call_opener)}</p>
        </div>"""
        if outreach_seq:
            if isinstance(outreach_seq, list):
                for step in outreach_seq:
                    if isinstance(step, dict):
                        step_label = step.get("step", step.get("channel", ""))
                        step_content = step.get("content", step.get("message", str(step)))
                        approach_html += f"""
        <div class="outreach-step">
            <div class="step-label">{esc(str(step_label))}</div>
            <p>{esc(str(step_content))}</p>
        </div>"""
                    else:
                        approach_html += f"<p>{esc(str(step))}</p>"
            elif isinstance(outreach_seq, dict):
                for key, val in outreach_seq.items():
                    approach_html += f"""
        <div class="outreach-step">
            <div class="step-label">{esc(str(key))}</div>
            <p>{esc(str(val))}</p>
        </div>"""
        cards_html += f"""
    <div class="card" id="approach-strategy">
        <h2>Approach Strategy</h2>
        {approach_html}
    </div>"""

    # --- Remaining sections not yet rendered ---
    rendered_keys = set()
    for kw in ["FIT", "ASSET", "BUSINESS MODEL", "COMPETITIVE", "MOAT", "GOLDEN", "NUGGET",
                "CEO VISION", "VISION", "M&A", "APPETITE", "CHALLENGE", "HEADWIND", "EARNINGS", "QUOTES"]:
        for k in sections:
            if kw in k:
                rendered_keys.add(k)
    for key, sec in sections.items():
        if key not in rendered_keys and key != "full":
            cards_html += f"""
    <div class="card" id="{slugify(sec["title"])}">
        <h2>{esc(sec["title"])}</h2>
        <div class="narrative-content">{render_paragraphs(sec["content"])}</div>
    </div>"""

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Buyer Dossier: {buyer_name} | {seller_name}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital@0;1&display=swap');
  *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #0d1117;
    color: #c9d1d9;
    line-height: 1.6;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .page {{ max-width: 960px; margin: 0 auto; }}

  /* HEADER */
  .header {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white; padding: 40px 48px 32px; position: relative; overflow: hidden;
    border-bottom: 4px solid;
    border-image: linear-gradient(90deg, #e94560, #f5a623, #e94560) 1;
  }}
  .header::after {{
    content: ''; position: absolute; top: -50%; right: -20%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(255,255,255,0.03) 0%, transparent 70%);
    border-radius: 50%;
  }}
  .header-label {{
    text-transform: uppercase; font-size: 11px; letter-spacing: 3px;
    color: rgba(255,255,255,0.5); margin-bottom: 8px; font-weight: 500;
  }}
  .header h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 4px; letter-spacing: -0.5px; color: #f0f6fc; }}
  .header .subtitle {{ font-size: 14px; color: rgba(255,255,255,0.7); margin-top: 4px; }}
  .header-meta {{ display: flex; gap: 24px; margin-top: 16px; flex-wrap: wrap; }}
  .header-meta .tag {{
    font-size: 12px; padding: 4px 12px; border-radius: 12px;
    background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.85);
  }}
  .score-badge {{
    position: absolute; top: 40px; right: 48px; width: 72px; height: 72px;
    border-radius: 50%; background: {score_color};
    display: flex; align-items: center; justify-content: center; flex-direction: column;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  }}
  .score-badge .score-num {{ font-size: 28px; font-weight: 700; line-height: 1; color: white; }}
  .score-badge .score-label {{ font-size: 8px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8; margin-top: 2px; color: white; }}

  /* CONTEXT BAR */
  .context-bar {{
    background: #161b22; border-bottom: 1px solid #30363d; padding: 14px 48px;
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
    font-size: 13px; color: #8b949e;
  }}
  .context-bar strong {{ color: #c9d1d9; }}

  /* CONTENT */
  .content {{ padding: 24px 48px 48px; }}

  /* CARDS */
  .card {{
    background: #161b22; border: 1px solid #30363d; border-radius: 10px;
    padding: 24px; margin-bottom: 24px;
  }}
  .card h2 {{
    font-size: 15px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px;
    color: #58a6ff; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 1px solid #21262d;
  }}
  .card p {{ margin-bottom: 10px; font-size: 14px; line-height: 1.75; color: #c9d1d9; }}
  .card strong {{ color: #f0f6fc; }}

  /* NARRATIVE CONTENT */
  .narrative-content p {{ margin-bottom: 12px; font-size: 14px; line-height: 1.75; color: #c9d1d9; }}
  .narrative-content blockquote {{
    border-left: 3px solid #58a6ff; padding-left: 16px; margin: 12px 0;
    font-style: italic; color: #8b949e;
  }}

  /* URGENCY CARD (competitive moat) */
  .urgency-card {{
    border: 2px solid #e74c3c !important;
    background: linear-gradient(135deg, #161b22, #1a1015) !important;
  }}
  .urgency-card h2 {{ color: #e74c3c !important; border-bottom-color: #e74c3c40 !important; }}
  .urgency-card::before {{
    content: 'URGENT'; position: absolute; top: -1px; right: 24px;
    background: #e74c3c; color: white; font-size: 10px; font-weight: 700;
    letter-spacing: 1.5px; padding: 4px 12px; border-radius: 0 0 6px 6px;
  }}
  .urgency-card {{ position: relative; }}

  /* GOLDEN NUGGET CARDS */
  .nugget-card {{
    background: #0d1117; border: 1px solid #21262d; border-radius: 8px;
    padding: 20px; margin-bottom: 16px; border-left: 4px solid #f5a623;
  }}
  .nugget-header {{
    font-size: 13px; font-weight: 700; color: #f5a623; margin-bottom: 12px;
    text-transform: uppercase; letter-spacing: 1px;
  }}
  .ceo-quote {{
    font-family: 'Playfair Display', Georgia, serif;
    font-style: italic; font-size: 15px; line-height: 1.7;
    color: #e6e6e6; border-left: 3px solid #58a6ff;
    padding: 12px 0 12px 20px; margin: 12px 0;
  }}
  .nugget-opener {{
    background: #0b2e1a; border: 1px solid #27ae60; border-radius: 6px;
    padding: 14px 18px; margin: 12px 0;
  }}
  .nugget-opener p {{ color: #a3e4b8 !important; margin: 0 !important; font-size: 13px !important; line-height: 1.65 !important; }}
  .opener-label {{
    font-size: 10px; font-weight: 700; letter-spacing: 1.5px;
    color: #27ae60; margin-bottom: 6px; text-transform: uppercase;
  }}
  .nugget-why {{
    font-size: 12.5px; color: #8b949e; margin-top: 10px; line-height: 1.6;
    padding-top: 10px; border-top: 1px solid #21262d;
  }}

  /* EARNINGS QUOTES */
  .earnings-quote {{
    margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #21262d;
  }}
  .earnings-quote:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
  .quote-attribution {{
    font-size: 12px; color: #8b949e; margin-top: 8px; font-weight: 500;
  }}

  /* CONTACTS TABLE */
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{
    text-align: left; padding: 10px 12px; background: #0d1117;
    font-weight: 600; color: #8b949e; font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #30363d;
  }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #21262d; color: #c9d1d9; }}
  tr:hover td {{ background: #1c2128; }}
  a {{ color: #58a6ff; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}

  /* APPROACH */
  .approach-opener {{
    background: #0b2e1a; border: 1px solid #27ae60; border-radius: 8px;
    padding: 18px 22px; margin-bottom: 16px;
  }}
  .approach-opener p {{ color: #a3e4b8 !important; font-size: 14px !important; line-height: 1.7 !important; }}
  .outreach-step {{
    background: #0d1117; border: 1px solid #21262d; border-radius: 6px;
    padding: 14px 18px; margin-bottom: 10px;
  }}
  .step-label {{
    font-size: 11px; font-weight: 700; color: #58a6ff; letter-spacing: 1px;
    text-transform: uppercase; margin-bottom: 4px;
  }}

  /* FOOTER */
  .footer {{
    text-align: center; padding: 24px 48px; color: #484f58; font-size: 12px;
    border-top: 1px solid #21262d; margin-top: 8px;
  }}

  /* RESPONSIVE */
  @media (max-width: 700px) {{
    .header {{ padding: 24px; }}
    .content {{ padding: 16px; }}
    .context-bar {{ padding: 12px 24px; }}
    .score-badge {{ top: 24px; right: 24px; width: 56px; height: 56px; }}
    .score-badge .score-num {{ font-size: 22px; }}
    .card {{ padding: 16px; }}
  }}

  /* PRINT */
  @media print {{
    body {{ background: white; color: #1a1a2e; }}
    .page {{ max-width: 100%; }}
    .header {{ background: #1a1a2e !important; }}
    .card {{ background: white; border: 1px solid #ddd; break-inside: avoid; }}
    .card h2 {{ color: #0f3460; }}
    .card p {{ color: #333; }}
    .urgency-card {{ border-color: #c0392b !important; background: #fff5f5 !important; }}
    .nugget-opener {{ background: #f0fff4; border-color: #27ae60; }}
    .nugget-opener p {{ color: #166534 !important; }}
    .ceo-quote {{ color: #333; }}
    .narrative-content p {{ color: #333; }}
  }}
</style>
</head>
<body>
<div class="page">

  <!-- HEADER -->
  <div class="header">
    <div class="header-label">Buyer Dossier</div>
    <h1>{buyer_name}</h1>
    <div class="subtitle">Prepared for {seller_name}</div>
    <div class="header-meta">
      {"<span class='tag'>Type: " + buyer_type + "</span>" if buyer_type else ""}
      {"<span class='tag'>Contact: " + contact_name + "</span>" if contact_name else ""}
      {"<span class='tag'>" + esc(location) + "</span>" if location else ""}
    </div>
    {"<div class='score-badge'><span class='score-num'>" + str(fit_score) + "</span><span class='score-label'>Fit</span></div>" if fit_score else ""}
  </div>

  <!-- CONTEXT BAR -->
  <div class="context-bar">
    <div>
      <strong>{seller_name}</strong> &bull; {seller_owner} &bull; {seller_vertical}
      {"&bull; " + seller_revenue if seller_revenue and seller_revenue != "Not publicly disclosed" else ""}
    </div>
    <div>{now}</div>
  </div>

  <!-- CONTENT -->
  <div class="content">
    {cards_html}
  </div>

  <!-- FOOTER -->
  <div class="footer">
    Generated {now} &bull; Next Chapter M&A Advisory &bull; Confidential &bull; Internal Use Only
  </div>

</div>

<!-- WIDGETS -->
<script src="/comment-widget.js"></script>
<script src="/version-widget.js"></script>

</body>
</html>"""

    return page_html


def generate_unstructured_html(buyer, seller_info, narrative):
    """Generate simple HTML page for unstructured narratives."""
    buyer_name = esc(buyer.get("buyer_company_name", "Unknown"))
    buyer_type = esc(buyer.get("buyer_type", ""))
    fit_score = buyer.get("fit_score", "")
    contact_name = esc(buyer.get("buyer_contact_name", ""))
    seller_name = esc(seller_info.get("company_name", ""))
    seller_owner = esc(seller_info.get("owner_name", ""))

    try:
        score_val = int(float(str(fit_score)))
    except (ValueError, TypeError):
        score_val = 0
    score_color = "#27ae60" if score_val >= 8 else "#f39c12" if score_val >= 6 else "#e74c3c" if score_val >= 1 else "#30363d"

    now = datetime.datetime.now().strftime('%B %d, %Y')

    # Build contacts if available
    contacts_html = ""
    contacts = buyer.get("verified_contacts")
    if contacts:
        contacts_html = f"""
    <div class="card" id="verified-contacts">
        <h2>Verified Contacts</h2>
        {build_contacts_table(contacts)}
    </div>"""

    # Build approach if available
    approach_html = ""
    call_opener = buyer.get("call_opener", "")
    if call_opener:
        approach_html = f"""
    <div class="card" id="approach">
        <h2>Approach Strategy</h2>
        <div style="background:#0b2e1a;border:1px solid #27ae60;border-radius:8px;padding:18px 22px;">
            <div style="font-size:10px;font-weight:700;letter-spacing:1.5px;color:#27ae60;margin-bottom:6px;text-transform:uppercase;">CALL OPENER</div>
            <p style="color:#a3e4b8;font-size:14px;line-height:1.7;">{esc(call_opener)}</p>
        </div>
    </div>"""

    narrative_html = render_paragraphs(narrative) if narrative else "<p>No narrative available.</p>"

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Buyer Dossier: {buyer_name} | {seller_name}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #0d1117; color: #c9d1d9; line-height: 1.6;
  }}
  .page {{ max-width: 960px; margin: 0 auto; }}
  .header {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white; padding: 40px 48px 32px; position: relative;
    border-bottom: 4px solid; border-image: linear-gradient(90deg, #e94560, #f5a623, #e94560) 1;
  }}
  .header-label {{ text-transform: uppercase; font-size: 11px; letter-spacing: 3px; color: rgba(255,255,255,0.5); margin-bottom: 8px; }}
  .header h1 {{ font-size: 28px; font-weight: 700; color: #f0f6fc; }}
  .header .subtitle {{ font-size: 14px; color: rgba(255,255,255,0.7); margin-top: 4px; }}
  .score-badge {{
    position: absolute; top: 40px; right: 48px; width: 72px; height: 72px;
    border-radius: 50%; background: {score_color};
    display: flex; align-items: center; justify-content: center; flex-direction: column;
  }}
  .score-badge .score-num {{ font-size: 28px; font-weight: 700; color: white; }}
  .score-badge .score-label {{ font-size: 8px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8; color: white; }}
  .context-bar {{
    background: #161b22; border-bottom: 1px solid #30363d; padding: 14px 48px;
    font-size: 13px; color: #8b949e;
  }}
  .context-bar strong {{ color: #c9d1d9; }}
  .content {{ padding: 24px 48px 48px; }}
  .card {{
    background: #161b22; border: 1px solid #30363d; border-radius: 10px;
    padding: 24px; margin-bottom: 24px;
  }}
  .card h2 {{
    font-size: 15px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px;
    color: #58a6ff; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 1px solid #21262d;
  }}
  .card p {{ margin-bottom: 10px; font-size: 14px; line-height: 1.75; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ text-align: left; padding: 10px 12px; background: #0d1117; font-weight: 600; color: #8b949e; font-size: 11px; text-transform: uppercase; border-bottom: 1px solid #30363d; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #21262d; color: #c9d1d9; }}
  tr:hover td {{ background: #1c2128; }}
  a {{ color: #58a6ff; text-decoration: none; }}
  .footer {{ text-align: center; padding: 24px 48px; color: #484f58; font-size: 12px; border-top: 1px solid #21262d; }}
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <div class="header-label">Buyer Dossier</div>
    <h1>{buyer_name}</h1>
    <div class="subtitle">Prepared for {seller_name}</div>
    {"<div class='score-badge'><span class='score-num'>" + str(fit_score) + "</span><span class='score-label'>Fit</span></div>" if fit_score else ""}
  </div>
  <div class="context-bar">
    <strong>{seller_name}</strong> &bull; {seller_owner}
  </div>
  <div class="content">
    <div class="card" id="buyer-profile">
        <h2>Buyer Profile</h2>
        {narrative_html}
    </div>
    {contacts_html}
    {approach_html}
  </div>
  <div class="footer">
    Generated {now} &bull; Next Chapter M&A Advisory &bull; Confidential
  </div>
</div>
<script src="/comment-widget.js"></script>
<script src="/version-widget.js"></script>
</body>
</html>"""

    return page_html


def generate_page(buyer, seller_info):
    """Generate the appropriate HTML page for a buyer."""
    narrative = buyer.get("story_narrative", "") or ""

    if is_structured(narrative):
        sections = parse_sections(narrative)
        return generate_structured_html(buyer, seller_info, sections, narrative)
    elif narrative.strip():
        return generate_unstructured_html(buyer, seller_info, narrative)
    else:
        # No narrative at all - use one_pager_json fallback
        return generate_unstructured_html(buyer, seller_info, buyer.get("fit_narrative", ""))


def process_buyers(seller_filter=None, buyer_filter=None):
    """Main processing function. Filter by seller name or buyer name if provided."""
    log("=" * 70)
    log("BUYER PAGE GENERATOR - RICH NARRATIVE EDITION")
    log("=" * 70)

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    query = """SELECT eb.*, p.company_name as seller_company, p.owner_name as seller_owner,
                      p.vertical as seller_vertical, p.city as seller_city, p.state as seller_state,
                      p.estimated_revenue as seller_revenue
               FROM engagement_buyers eb
               JOIN proposals p ON eb.proposal_id = p.id"""
    params = []

    if seller_filter:
        query += " WHERE p.company_name ILIKE %s"
        params.append(f"%{seller_filter}%")
    if buyer_filter:
        query += " WHERE " if not seller_filter else " AND "
        query += "eb.buyer_company_name ILIKE %s"
        params.append(f"%{buyer_filter}%")

    query += " ORDER BY p.company_name, eb.fit_score DESC NULLS LAST"

    cur.execute(query, params)
    rows = cur.fetchall()
    log(f"Found {len(rows)} buyers to process")

    success = 0
    failed = 0
    current_seller = None

    for row in rows:
        seller_name = row["seller_company"]
        buyer_name = row["buyer_company_name"] or "Unknown"

        if seller_name != current_seller:
            current_seller = seller_name
            log(f"\n--- Seller: {seller_name} ---")

        seller_info = {
            "company_name": seller_name,
            "owner_name": row.get("seller_owner", ""),
            "vertical": row.get("seller_vertical", ""),
            "estimated_revenue": row.get("seller_revenue", ""),
        }

        try:
            narrative = row.get("story_narrative", "") or ""
            structured = is_structured(narrative)
            log(f"  {buyer_name} (fit={row.get('fit_score')}, narrative={len(narrative)} chars, {'structured' if structured else 'unstructured'})")

            html = generate_page(dict(row), seller_info)

            # Save files
            seller_slug = slugify(seller_name)
            buyer_slug = slugify(buyer_name)
            filename = f"{seller_slug}_{buyer_slug}.html"

            output_path = os.path.join(OUTPUT_DIR, filename)
            web_path = os.path.join(WEB_DIR, filename)

            with open(output_path, 'w') as f:
                f.write(html)
            if os.path.isdir(WEB_DIR):
                with open(web_path, 'w') as f:
                    f.write(html)

            # Update DB
            cur.execute(
                "UPDATE engagement_buyers SET one_pager_html = %s WHERE id = %s",
                (html, row["id"])
            )
            conn.commit()

            success += 1
            log(f"    Saved: {filename} ({len(html)} bytes)")

        except Exception as e:
            conn.rollback()
            failed += 1
            log(f"    FAILED: {buyer_name}: {e}")
            import traceback
            log(f"    {traceback.format_exc()}")

    cur.close()
    conn.close()

    log(f"\n{'=' * 70}")
    log(f"COMPLETE: {success} success, {failed} failed, {len(rows)} total")
    log(f"Output: {OUTPUT_DIR}")
    log(f"Web: {WEB_DIR}")
    log(f"{'=' * 70}")

    return success, failed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate rich buyer dossier pages")
    parser.add_argument("--seller", help="Filter by seller company name")
    parser.add_argument("--buyer", help="Filter by buyer company name")
    parser.add_argument("--sap-only", action="store_true", help="Process SAP SuccessFactors only")
    parser.add_argument("--hrcom-only", action="store_true", help="Process HR.com buyers only")
    args = parser.parse_args()

    if args.sap_only:
        process_buyers(seller_filter="HR.com", buyer_filter="SAP")
    elif args.hrcom_only:
        process_buyers(seller_filter="HR.com")
    elif args.seller or args.buyer:
        process_buyers(seller_filter=args.seller, buyer_filter=args.buyer)
    else:
        process_buyers()


if __name__ == "__main__":
    main()
