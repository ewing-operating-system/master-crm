#!/bin/bash
# Buyer 1-Pager Engine
# Generates professional HTML dossiers for top 3 buyers per company
set -euo pipefail

LOG_FILE="$HOME/Projects/dossier-pipeline/data/audit-logs/buyer_1pagers.log"
OUTPUT_DIR="$HOME/Projects/master-crm/data/buyer-1pagers"
COPY_DIR="$HOME/Downloads/master-crm-proposals"
DATA_FILE="/tmp/buyers_data.json"
DB_URL="postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:5432/postgres"

OPENROUTER_KEY="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"
OPENROUTER_MODEL="deepseek/deepseek-chat-v3-0324"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

mkdir -p "$OUTPUT_DIR" "$COPY_DIR" "$(dirname "$LOG_FILE")"

log "=== Buyer 1-Pager Engine Started ==="

# Extract top 3 buyers per company from saved JSON
TOP_BUYERS=$(cd /tmp && node -e "
const data = require('./buyers_data.json');
const grouped = {};
data.forEach(r => {
  if (!grouped[r.seller_company]) grouped[r.seller_company] = [];
  grouped[r.seller_company].push(r);
});
const top3 = [];
Object.values(grouped).forEach(buyers => {
  buyers.slice(0, 3).forEach(b => top3.push(b));
});
console.log(JSON.stringify(top3));
")

TOTAL=$(echo "$TOP_BUYERS" | node -e "const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')); console.log(d.length);")
log "Processing $TOTAL buyer 1-pagers"

slugify() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//'
}

generate_with_claude() {
  local prompt="$1"
  local result
  # Try Claude CLI first with 60s timeout
  result=$(echo "$prompt" | timeout 120 claude -p --output-format text 2>/dev/null) && {
    echo "$result"
    return 0
  }
  # Fallback to OpenRouter DeepSeek
  log "Claude CLI failed/timed out, falling back to OpenRouter DeepSeek"
  result=$(curl -s --max-time 120 https://openrouter.ai/api/v1/chat/completions \
    -H "Authorization: Bearer $OPENROUTER_KEY" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg prompt "$prompt" '{
      model: "deepseek/deepseek-chat-v3-0324",
      messages: [{role: "user", content: $prompt}],
      temperature: 0.7,
      max_tokens: 4000
    }')" | jq -r '.choices[0].message.content') && {
    echo "$result"
    return 0
  }
  log "ERROR: Both Claude and OpenRouter failed"
  return 1
}

generate_html() {
  local buyer_json="$1"
  local one_pager_json="$2"

  local buyer_company=$(echo "$buyer_json" | jq -r '.buyer_company_name')
  local buyer_contact=$(echo "$buyer_json" | jq -r '.buyer_contact_name')
  local buyer_title=$(echo "$buyer_json" | jq -r '.buyer_title')
  local buyer_type=$(echo "$buyer_json" | jq -r '.buyer_type')
  local buyer_city=$(echo "$buyer_json" | jq -r '.buyer_city // ""')
  local buyer_state=$(echo "$buyer_json" | jq -r '.buyer_state // ""')
  local fit_score=$(echo "$buyer_json" | jq -r '.fit_score')
  local seller_company=$(echo "$buyer_json" | jq -r '.seller_company')
  local seller_owner=$(echo "$buyer_json" | jq -r '.seller_owner')
  local seller_vertical=$(echo "$buyer_json" | jq -r '.seller_vertical')
  local seller_city=$(echo "$buyer_json" | jq -r '.seller_city // ""')
  local seller_state=$(echo "$buyer_json" | jq -r '.seller_state // ""')
  local seller_revenue=$(echo "$buyer_json" | jq -r '.seller_revenue // "N/A"')

  local narrative=$(echo "$one_pager_json" | jq -r '.buyer_narrative')
  local why_seller=$(echo "$one_pager_json" | jq -r '.why_this_seller')
  local approach=$(echo "$one_pager_json" | jq -r '.approach_angle')
  local timeline=$(echo "$one_pager_json" | jq -r '.timeline')

  # Build acquisition history HTML
  local acq_html=$(echo "$one_pager_json" | jq -r '.acquisition_history // [] | map("<li>" + . + "</li>") | join("")')

  # Build talking points HTML
  local tp_html=$(echo "$one_pager_json" | jq -r '.talking_points // [] | map("<li>" + . + "</li>") | join("")')

  # Build risk factors HTML
  local risk_html=$(echo "$one_pager_json" | jq -r '.risk_factors // [] | map("<li>" + . + "</li>") | join("")')

  # Score color
  local score_color="#e74c3c"
  if [ "$fit_score" -ge 8 ] 2>/dev/null; then score_color="#27ae60";
  elif [ "$fit_score" -ge 6 ] 2>/dev/null; then score_color="#f39c12"; fi

  local buyer_location=""
  if [ -n "$buyer_city" ] && [ "$buyer_city" != "null" ]; then
    buyer_location="$buyer_city, $buyer_state"
  fi

  cat <<HTMLEOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Buyer Dossier: ${buyer_company} | ${seller_company}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #f8f9fa;
    color: #2c3e50;
    line-height: 1.6;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  .page {
    max-width: 900px;
    margin: 0 auto;
    background: white;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  }

  @media print {
    body { background: white; }
    .page { box-shadow: none; max-width: 100%; }
  }

  .header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white;
    padding: 40px 48px 32px;
    position: relative;
    overflow: hidden;
  }

  .header::after {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
    border-radius: 50%;
  }

  .header-label {
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 3px;
    color: rgba(255,255,255,0.5);
    margin-bottom: 8px;
    font-weight: 500;
  }

  .header h1 {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 4px;
    letter-spacing: -0.5px;
  }

  .header-meta {
    display: flex;
    gap: 24px;
    margin-top: 12px;
    flex-wrap: wrap;
  }

  .header-meta span {
    font-size: 13px;
    color: rgba(255,255,255,0.7);
    font-weight: 400;
  }

  .header-meta span strong {
    color: rgba(255,255,255,0.95);
    font-weight: 600;
  }

  .score-badge {
    position: absolute;
    top: 40px;
    right: 48px;
    width: 72px;
    height: 72px;
    border-radius: 50%;
    background: ${score_color};
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  }

  .score-badge .score-num {
    font-size: 28px;
    font-weight: 700;
    line-height: 1;
  }

  .score-badge .score-label {
    font-size: 8px;
    text-transform: uppercase;
    letter-spacing: 1px;
    opacity: 0.8;
    margin-top: 2px;
  }

  .context-bar {
    background: #f1f5f9;
    border-bottom: 1px solid #e2e8f0;
    padding: 16px 48px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
  }

  .context-bar .seller-info {
    font-size: 14px;
    color: #475569;
  }

  .context-bar .seller-info strong {
    color: #1e293b;
  }

  .context-bar .date {
    font-size: 12px;
    color: #94a3b8;
  }

  .content {
    padding: 36px 48px 48px;
  }

  .section {
    margin-bottom: 32px;
  }

  .section-title {
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #0f3460;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid #e2e8f0;
  }

  .section p {
    font-size: 14.5px;
    line-height: 1.75;
    color: #374151;
    margin-bottom: 12px;
  }

  .section ul {
    list-style: none;
    padding: 0;
  }

  .section ul li {
    font-size: 14px;
    line-height: 1.7;
    color: #374151;
    padding: 6px 0 6px 24px;
    position: relative;
    border-bottom: 1px solid #f1f5f9;
  }

  .section ul li:last-child {
    border-bottom: none;
  }

  .section ul li::before {
    content: '';
    position: absolute;
    left: 0;
    top: 14px;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #0f3460;
    opacity: 0.4;
  }

  .two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32px;
  }

  @media (max-width: 700px) {
    .two-col { grid-template-columns: 1fr; }
    .header { padding: 24px; }
    .content { padding: 24px; }
    .context-bar { padding: 12px 24px; }
    .score-badge { top: 24px; right: 24px; }
  }

  .approach-box {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    padding: 20px 24px;
    margin-top: 8px;
  }

  .approach-box p {
    color: #166534 !important;
    font-size: 14px !important;
  }

  .risk-box {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 20px 24px;
    margin-top: 8px;
  }

  .risk-box li::before {
    background: #dc2626 !important;
  }

  .risk-box li {
    color: #991b1b !important;
    border-bottom-color: #fee2e2 !important;
    font-size: 13.5px;
  }

  .timeline-box {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    padding: 20px 24px;
    margin-top: 8px;
  }

  .timeline-box p {
    color: #1e40af !important;
    font-size: 14px !important;
  }

  .footer {
    background: #1a1a2e;
    color: rgba(255,255,255,0.4);
    text-align: center;
    padding: 16px;
    font-size: 11px;
    letter-spacing: 1px;
  }
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <div class="header-label">Buyer Dossier</div>
    <h1>${buyer_company}</h1>
    <div class="header-meta">
      <span><strong>${buyer_type}</strong></span>
      <span>${buyer_location}</span>
      <span>Contact: <strong>${buyer_contact}</strong>, ${buyer_title}</span>
    </div>
    <div class="score-badge">
      <span class="score-num">${fit_score}</span>
      <span class="score-label">FIT</span>
    </div>
  </div>

  <div class="context-bar">
    <div class="seller-info">
      Prepared for <strong>${seller_company}</strong> &mdash; ${seller_vertical} &mdash; ${seller_city}, ${seller_state}
      ${seller_revenue:+ &mdash; Est. Revenue: \$${seller_revenue}}
    </div>
    <div class="date">Generated $(date '+%B %d, %Y')</div>
  </div>

  <div class="content">
    <div class="section">
      <div class="section-title">Buyer Profile</div>
      <p>${narrative}</p>
    </div>

    <div class="two-col">
      <div class="section">
        <div class="section-title">Acquisition History</div>
        <ul>${acq_html:-<li>No public acquisition history available</li>}</ul>
      </div>

      <div class="section">
        <div class="section-title">Why ${seller_company}</div>
        <p>${why_seller}</p>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Approach Strategy</div>
      <div class="approach-box">
        <p>${approach}</p>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Talking Points</div>
      <ul>${tp_html}</ul>
    </div>

    <div class="two-col">
      <div class="section">
        <div class="section-title">Risk Factors</div>
        <div class="risk-box">
          <ul>${risk_html}</ul>
        </div>
      </div>

      <div class="section">
        <div class="section-title">Expected Timeline</div>
        <div class="timeline-box">
          <p>${timeline}</p>
        </div>
      </div>
    </div>
  </div>

  <div class="footer">
    CONFIDENTIAL &mdash; PREPARED BY GILLASPY HOLDINGS &mdash; $(date '+%Y')
  </div>
</div>
</body>
</html>
HTMLEOF
}

# Process each buyer
INDEX=0
SUCCESS=0
FAIL=0

echo "$TOP_BUYERS" | node -e "
const data = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
data.forEach((b, i) => {
  require('fs').writeFileSync('/tmp/buyer_' + i + '.json', JSON.stringify(b));
});
console.log(data.length);
" > /tmp/buyer_count.txt

BUYER_COUNT=$(cat /tmp/buyer_count.txt)

for ((i=0; i<BUYER_COUNT; i++)); do
  BUYER_JSON=$(cat /tmp/buyer_${i}.json)

  BUYER_CO=$(echo "$BUYER_JSON" | jq -r '.buyer_company_name')
  SELLER_CO=$(echo "$BUYER_JSON" | jq -r '.seller_company')
  BUYER_ID=$(echo "$BUYER_JSON" | jq -r '.id')
  FIT_SCORE=$(echo "$BUYER_JSON" | jq -r '.fit_score')

  log "[$((i+1))/$BUYER_COUNT] Generating 1-pager: $BUYER_CO -> $SELLER_CO (fit: $FIT_SCORE)"

  SELLER_SLUG=$(slugify "$SELLER_CO")
  BUYER_SLUG=$(slugify "$BUYER_CO")
  FILENAME="${SELLER_SLUG}_${BUYER_SLUG}.html"

  # Build the prompt for Claude
  FIT_NARRATIVE=$(echo "$BUYER_JSON" | jq -r '.fit_narrative // "N/A"')
  APPROACH_STRAT=$(echo "$BUYER_JSON" | jq -r '.approach_strategy // "N/A"')
  SELLER_VERTICAL=$(echo "$BUYER_JSON" | jq -r '.seller_vertical // "N/A"')
  SELLER_REVENUE=$(echo "$BUYER_JSON" | jq -r '.seller_revenue // "N/A"')
  BUYER_TYPE=$(echo "$BUYER_JSON" | jq -r '.buyer_type // "N/A"')
  SELLER_CITY=$(echo "$BUYER_JSON" | jq -r '.seller_city // ""')
  SELLER_STATE=$(echo "$BUYER_JSON" | jq -r '.seller_state // ""')
  ATTACK_PLAN=$(echo "$BUYER_JSON" | jq -r '.attack_plan // "N/A"')

  PROMPT="You are an M&A research analyst. Generate a detailed buyer intelligence dossier in JSON format.

BUYER: ${BUYER_CO}
BUYER TYPE: ${BUYER_TYPE}
EXISTING FIT NARRATIVE: ${FIT_NARRATIVE}

SELLER: ${SELLER_CO}
SELLER VERTICAL: ${SELLER_VERTICAL}
SELLER LOCATION: ${SELLER_CITY}, ${SELLER_STATE}
SELLER EST REVENUE: ${SELLER_REVENUE}
ATTACK PLAN: ${ATTACK_PLAN}

Return ONLY valid JSON (no markdown, no code fences) with these fields:
{
  \"buyer_narrative\": \"2-3 paragraphs about who this buyer is, what they've acquired, their investment thesis, and how they operate. Be specific and detailed.\",
  \"acquisition_history\": [\"List of 3-5 known or likely recent acquisitions with brief details\"],
  \"why_this_seller\": \"2 paragraphs explaining specifically why this seller fits their acquisition strategy, including geographic, operational, and financial angles\",
  \"approach_angle\": \"1-2 paragraphs on how to approach this buyer. We represent the owners exploring strategic options. Never say the company is for sale. Frame it as: former business owners who cashed out buy companies because they believe in owners, not the stock market.\",
  \"talking_points\": [\"5 specific talking points for the introductory call\"],
  \"risk_factors\": [\"3-4 specific risks or objections this buyer might raise\"],
  \"timeline\": \"1 paragraph on how fast this type of buyer typically moves from first contact to LOI to close\"
}"

  # Generate the JSON content
  ONE_PAGER_RAW=$(generate_with_claude "$PROMPT" 2>/dev/null) || {
    log "ERROR: Generation failed for $BUYER_CO -> $SELLER_CO"
    FAIL=$((FAIL + 1))
    continue
  }

  # Extract JSON (handle possible markdown wrapping)
  ONE_PAGER_JSON=$(echo "$ONE_PAGER_RAW" | sed 's/^```json//' | sed 's/^```//' | sed 's/```$//' | jq '.' 2>/dev/null)

  if [ -z "$ONE_PAGER_JSON" ] || [ "$ONE_PAGER_JSON" = "null" ]; then
    log "ERROR: Invalid JSON returned for $BUYER_CO -> $SELLER_CO, attempting repair..."
    # Try to extract JSON from the response
    ONE_PAGER_JSON=$(echo "$ONE_PAGER_RAW" | grep -Pzo '\{[\s\S]*\}' | head -1 | jq '.' 2>/dev/null)
    if [ -z "$ONE_PAGER_JSON" ] || [ "$ONE_PAGER_JSON" = "null" ]; then
      log "ERROR: Could not parse JSON for $BUYER_CO -> $SELLER_CO"
      FAIL=$((FAIL + 1))
      continue
    fi
  fi

  # Generate the HTML
  HTML_CONTENT=$(generate_html "$BUYER_JSON" "$ONE_PAGER_JSON")

  # Save files
  echo "$HTML_CONTENT" > "${OUTPUT_DIR}/${FILENAME}"
  cp "${OUTPUT_DIR}/${FILENAME}" "${COPY_DIR}/${FILENAME}"

  log "Saved: ${FILENAME}"

  # Update Supabase
  cd /tmp && node -e "
const { Client } = require('pg');
const fs = require('fs');
const c = new Client({ connectionString: '$DB_URL' });
const html = fs.readFileSync('${OUTPUT_DIR}/${FILENAME}', 'utf8');
const json = $(echo "$ONE_PAGER_JSON" | jq -c '.');
c.connect().then(() => c.query(
  'UPDATE engagement_buyers SET one_pager_html = \$1, one_pager_json = \$2 WHERE id = \$3',
  [html, json, '$BUYER_ID']
)).then(r => {
  console.log('DB updated: ' + r.rowCount + ' row');
  c.end();
}).catch(e => { console.error('DB error:', e.message); c.end(); });
" 2>&1 | while read line; do log "  $line"; done

  SUCCESS=$((SUCCESS + 1))
  log "Completed $((i+1))/$BUYER_COUNT"
done

log "=== Buyer 1-Pager Engine Complete ==="
log "Success: $SUCCESS / $BUYER_COUNT"
log "Failed: $FAIL / $BUYER_COUNT"
log "Output: $OUTPUT_DIR"
log "Copies: $COPY_DIR"
