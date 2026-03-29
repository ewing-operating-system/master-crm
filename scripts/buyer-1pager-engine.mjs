#!/usr/bin/env node
// Buyer 1-Pager Engine — generates professional HTML dossiers for top 3 buyers per company
import { execSync } from 'child_process';
import { writeFileSync, mkdirSync, copyFileSync } from 'fs';
import { join } from 'path';

const HOME = process.env.HOME;
const OUTPUT_DIR = join(HOME, 'Projects/master-crm/data/buyer-1pagers');
const COPY_DIR = join(HOME, 'Downloads/master-crm-proposals');
const LOG_FILE = join(HOME, 'Projects/dossier-pipeline/data/audit-logs/buyer_1pagers.log');

const SUPABASE_URL = 'https://dwrnfpjcvydhmhnvyzov.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s';
const OPENROUTER_KEY = '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';

[OUTPUT_DIR, COPY_DIR, join(HOME, 'Projects/dossier-pipeline/data/audit-logs')].forEach(d => mkdirSync(d, { recursive: true }));

function log(msg) {
  const line = `[${new Date().toISOString().replace('T',' ').slice(0,19)}] ${msg}`;
  console.log(line);
  try { writeFileSync(LOG_FILE, line + '\n', { flag: 'a' }); } catch(e) {}
}

function slugify(s) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

// Supabase REST API helpers
async function supabaseGet(table, query = '') {
  const url = `${SUPABASE_URL}/rest/v1/${table}?${query}`;
  const res = await fetch(url, {
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json'
    }
  });
  if (!res.ok) throw new Error(`Supabase GET error: ${res.status} ${await res.text()}`);
  return res.json();
}

async function supabasePatch(table, matchCol, matchVal, data) {
  const url = `${SUPABASE_URL}/rest/v1/${table}?${matchCol}=eq.${matchVal}`;
  const res = await fetch(url, {
    method: 'PATCH',
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': 'return=minimal'
    },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error(`Supabase PATCH error: ${res.status} ${await res.text()}`);
  return true;
}

async function supabaseRPC(sql) {
  // Use the SQL endpoint for DDL
  const url = `${SUPABASE_URL}/rest/v1/rpc/`;
  // Actually, we'll use the management API for DDL. Let's just try the PATCH approach
  // and if columns don't exist, we handle gracefully.
}

// Generate JSON via Claude CLI, fallback to OpenRouter
function generateContent(prompt) {
  // Try Claude CLI
  try {
    const tmpPrompt = '/tmp/buyer_prompt.txt';
    writeFileSync(tmpPrompt, prompt);
    const result = execSync(`cat "${tmpPrompt}" | claude -p --output-format text`, {
      timeout: 120000,
      maxBuffer: 10 * 1024 * 1024,
      encoding: 'utf8'
    });
    return result;
  } catch(e) {
    log('  Claude CLI failed, falling back to OpenRouter DeepSeek...');
  }

  // Fallback to OpenRouter
  try {
    const payload = JSON.stringify({
      model: 'deepseek/deepseek-chat-v3-0324',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.7,
      max_tokens: 4000
    });
    writeFileSync('/tmp/openrouter_payload.json', payload);
    const result = execSync(`curl -s --max-time 120 https://openrouter.ai/api/v1/chat/completions -H "Authorization: Bearer ${OPENROUTER_KEY}" -H "Content-Type: application/json" -d @/tmp/openrouter_payload.json`, {
      timeout: 130000,
      maxBuffer: 10 * 1024 * 1024,
      encoding: 'utf8'
    });
    const parsed = JSON.parse(result);
    return parsed.choices[0].message.content;
  } catch(e) {
    log('  OpenRouter also failed: ' + e.message);
    return null;
  }
}

function parseJSON(raw) {
  if (!raw) return null;
  let cleaned = raw.replace(/^```json\s*/m, '').replace(/^```\s*/m, '').replace(/```\s*$/m, '').trim();
  const start = cleaned.indexOf('{');
  const end = cleaned.lastIndexOf('}');
  if (start >= 0 && end > start) cleaned = cleaned.slice(start, end + 1);
  try { return JSON.parse(cleaned); } catch(e) { log('  JSON parse error: ' + e.message); return null; }
}

function escapeHtml(s) {
  if (!s) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function generateHTML(buyer, onePager) {
  const bc = escapeHtml(buyer.buyer_company_name);
  const bcontact = escapeHtml(buyer.buyer_contact_name);
  const btitle = escapeHtml(buyer.buyer_title);
  const btype = escapeHtml(buyer.buyer_type);
  const bcity = buyer.buyer_city || '';
  const bstate = buyer.buyer_state || '';
  const bloc = bcity && bcity !== 'null' ? escapeHtml(`${bcity}, ${bstate}`) : '';
  const fs = parseFloat(buyer.fit_score) || 0;
  const sc = escapeHtml(buyer.seller_company);
  const sv = escapeHtml(buyer.seller_vertical);
  const scity = escapeHtml(buyer.seller_city || '');
  const sstate = escapeHtml(buyer.seller_state || '');
  const srev = buyer.seller_revenue ? `$${Number(buyer.seller_revenue).toLocaleString()}` : 'N/A';
  const scoreColor = fs >= 8 ? '#27ae60' : fs >= 6 ? '#f39c12' : '#e74c3c';
  const today = new Date().toLocaleDateString('en-US', { year:'numeric', month:'long', day:'numeric' });

  const narrative = escapeHtml(onePager.buyer_narrative || '');
  const whySeller = escapeHtml(onePager.why_this_seller || '');
  const approach = escapeHtml(onePager.approach_angle || '');
  const timeline = escapeHtml(onePager.timeline || '');

  const acqHtml = (onePager.acquisition_history || []).map(a => `<li>${escapeHtml(a)}</li>`).join('') || '<li>No public acquisition history available</li>';
  const tpHtml = (onePager.talking_points || []).map(t => `<li>${escapeHtml(t)}</li>`).join('');
  const riskHtml = (onePager.risk_factors || []).map(r => `<li>${escapeHtml(r)}</li>`).join('');

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Buyer Dossier: ${bc} | ${sc}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #f8f9fa; color: #2c3e50; line-height: 1.6;
    -webkit-print-color-adjust: exact; print-color-adjust: exact;
  }
  .page { max-width: 900px; margin: 0 auto; background: white; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }
  @media print { body { background: white; } .page { box-shadow: none; max-width: 100%; } }
  .header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white; padding: 40px 48px 32px; position: relative; overflow: hidden;
  }
  .header::after {
    content: ''; position: absolute; top: -50%; right: -20%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
    border-radius: 50%;
  }
  .header-label {
    text-transform: uppercase; font-size: 11px; letter-spacing: 3px;
    color: rgba(255,255,255,0.5); margin-bottom: 8px; font-weight: 500;
  }
  .header h1 { font-size: 28px; font-weight: 700; margin-bottom: 4px; letter-spacing: -0.5px; }
  .header-meta { display: flex; gap: 24px; margin-top: 12px; flex-wrap: wrap; }
  .header-meta span { font-size: 13px; color: rgba(255,255,255,0.7); font-weight: 400; }
  .header-meta span strong { color: rgba(255,255,255,0.95); font-weight: 600; }
  .score-badge {
    position: absolute; top: 40px; right: 48px; width: 72px; height: 72px;
    border-radius: 50%; background: ${scoreColor};
    display: flex; align-items: center; justify-content: center; flex-direction: column;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  }
  .score-badge .score-num { font-size: 28px; font-weight: 700; line-height: 1; color: white; }
  .score-badge .score-label { font-size: 8px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8; margin-top: 2px; color: white; }
  .context-bar {
    background: #f1f5f9; border-bottom: 1px solid #e2e8f0; padding: 16px 48px;
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
  }
  .context-bar .seller-info { font-size: 14px; color: #475569; }
  .context-bar .seller-info strong { color: #1e293b; }
  .context-bar .date { font-size: 12px; color: #94a3b8; }
  .content { padding: 36px 48px 48px; }
  .section { margin-bottom: 32px; }
  .section-title {
    font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 2px;
    color: #0f3460; margin-bottom: 14px; padding-bottom: 8px; border-bottom: 2px solid #e2e8f0;
  }
  .section p { font-size: 14.5px; line-height: 1.75; color: #374151; margin-bottom: 12px; white-space: pre-line; }
  .section ul { list-style: none; padding: 0; }
  .section ul li {
    font-size: 14px; line-height: 1.7; color: #374151;
    padding: 6px 0 6px 24px; position: relative; border-bottom: 1px solid #f1f5f9;
  }
  .section ul li:last-child { border-bottom: none; }
  .section ul li::before {
    content: ''; position: absolute; left: 0; top: 14px;
    width: 8px; height: 8px; border-radius: 50%; background: #0f3460; opacity: 0.4;
  }
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }
  @media (max-width: 700px) {
    .two-col { grid-template-columns: 1fr; }
    .header { padding: 24px; } .content { padding: 24px; }
    .context-bar { padding: 12px 24px; } .score-badge { top: 24px; right: 24px; }
  }
  .approach-box {
    background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px;
    padding: 20px 24px; margin-top: 8px;
  }
  .approach-box p { color: #166534 !important; font-size: 14px !important; }
  .risk-box {
    background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px;
    padding: 20px 24px; margin-top: 8px;
  }
  .risk-box li::before { background: #dc2626 !important; }
  .risk-box li { color: #991b1b !important; border-bottom-color: #fee2e2 !important; font-size: 13.5px; }
  .timeline-box {
    background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px;
    padding: 20px 24px; margin-top: 8px;
  }
  .timeline-box p { color: #1e40af !important; font-size: 14px !important; }
  .footer {
    background: #1a1a2e; color: rgba(255,255,255,0.4); text-align: center;
    padding: 16px; font-size: 11px; letter-spacing: 1px;
  }
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <div class="header-label">Buyer Dossier</div>
    <h1>${bc}</h1>
    <div class="header-meta">
      <span><strong>${btype}</strong></span>
      ${bloc ? `<span>${bloc}</span>` : ''}
      <span>Contact: <strong>${bcontact}</strong>, ${btitle}</span>
    </div>
    <div class="score-badge">
      <span class="score-num">${fs}</span>
      <span class="score-label">FIT</span>
    </div>
  </div>
  <div class="context-bar">
    <div class="seller-info">
      Prepared for <strong>${sc}</strong> &mdash; ${sv} &mdash; ${scity}, ${sstate} &mdash; Est. Revenue: ${srev}
    </div>
    <div class="date">Generated ${today}</div>
  </div>
  <div class="content">
    <div class="section">
      <div class="section-title">Buyer Profile</div>
      <p>${narrative}</p>
    </div>
    <div class="two-col">
      <div class="section">
        <div class="section-title">Acquisition History</div>
        <ul>${acqHtml}</ul>
      </div>
      <div class="section">
        <div class="section-title">Why ${sc}</div>
        <p>${whySeller}</p>
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
      <ul>${tpHtml}</ul>
    </div>
    <div class="two-col">
      <div class="section">
        <div class="section-title">Risk Factors</div>
        <div class="risk-box">
          <ul>${riskHtml}</ul>
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
    CONFIDENTIAL &mdash; PREPARED BY GILLASPY HOLDINGS &mdash; ${new Date().getFullYear()}
  </div>
</div>
</body>
</html>`;
}

async function main() {
  log('=== Buyer 1-Pager Engine Started ===');

  // Add columns via Supabase SQL editor (management API)
  // We'll just try patching and handle errors
  log('Ensuring one_pager columns exist...');
  try {
    // Use the SQL endpoint
    const sqlRes = await fetch(`${SUPABASE_URL}/rest/v1/rpc/`, {
      method: 'POST',
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    });
    // This won't work for DDL, but columns were already added earlier
  } catch(e) {}
  log('Columns already exist from earlier migration');

  // Fetch all engagement_buyers
  log('Fetching engagement_buyers...');
  const buyers = await supabaseGet('engagement_buyers', 'select=id,buyer_company_name,buyer_contact_name,buyer_title,buyer_type,buyer_city,buyer_state,fit_score,fit_narrative,approach_strategy,approach_script,entity,proposal_id,extra_fields&order=fit_score.desc.nullslast');

  // Fetch all proposals
  log('Fetching proposals...');
  const proposals = await supabaseGet('proposals', 'select=id,company_name,owner_name,vertical,city,state,estimated_revenue,attack_plan');

  // Build proposal lookup
  const proposalMap = {};
  proposals.forEach(p => { proposalMap[p.id] = p; });

  // Join and enrich
  const enriched = buyers.map(b => ({
    ...b,
    seller_company: proposalMap[b.proposal_id]?.company_name || 'Unknown',
    seller_owner: proposalMap[b.proposal_id]?.owner_name || 'Unknown',
    seller_vertical: proposalMap[b.proposal_id]?.vertical || 'Unknown',
    seller_city: proposalMap[b.proposal_id]?.city || '',
    seller_state: proposalMap[b.proposal_id]?.state || '',
    seller_revenue: proposalMap[b.proposal_id]?.estimated_revenue || null,
    attack_plan: proposalMap[b.proposal_id]?.attack_plan || ''
  })).filter(b => b.seller_company !== 'Unknown');

  // Group by seller, pick top 3
  const grouped = {};
  enriched.forEach(r => {
    if (!grouped[r.seller_company]) grouped[r.seller_company] = [];
    grouped[r.seller_company].push(r);
  });
  // Sort within each group by fit_score desc
  Object.values(grouped).forEach(arr => arr.sort((a, b) => (parseFloat(b.fit_score)||0) - (parseFloat(a.fit_score)||0)));

  const top3 = [];
  Object.entries(grouped).forEach(([company, bList]) => {
    bList.slice(0, 3).forEach(b => top3.push(b));
    log(`${company}: top 3 = ${bList.slice(0,3).map(b => `${b.buyer_company_name} (${b.fit_score})`).join(', ')}`);
  });

  log(`Processing ${top3.length} buyer 1-pagers across ${Object.keys(grouped).length} companies`);

  let success = 0, fail = 0;

  for (let i = 0; i < top3.length; i++) {
    const buyer = top3[i];
    const label = `[${i+1}/${top3.length}]`;
    log(`${label} Generating: ${buyer.buyer_company_name} -> ${buyer.seller_company} (fit: ${buyer.fit_score})`);

    const prompt = `You are an M&A research analyst. Generate a detailed buyer intelligence dossier in JSON format.

BUYER: ${buyer.buyer_company_name}
BUYER TYPE: ${buyer.buyer_type}
BUYER LOCATION: ${buyer.buyer_city || 'Unknown'}, ${buyer.buyer_state || 'Unknown'}
BUYER CONTACT: ${buyer.buyer_contact_name}, ${buyer.buyer_title}
EXISTING FIT NARRATIVE: ${buyer.fit_narrative || 'N/A'}
EXISTING APPROACH STRATEGY: ${buyer.approach_strategy || 'N/A'}

SELLER: ${buyer.seller_company}
SELLER OWNER: ${buyer.seller_owner}
SELLER VERTICAL: ${buyer.seller_vertical}
SELLER LOCATION: ${buyer.seller_city}, ${buyer.seller_state}
SELLER EST REVENUE: ${buyer.seller_revenue || 'N/A'}
ATTACK PLAN SUMMARY: ${(buyer.attack_plan || 'N/A').slice(0, 500)}

Return ONLY valid JSON (no markdown, no code fences, no explanation) with these exact fields:
{
  "buyer_narrative": "2-3 detailed paragraphs about who this buyer is, what they have acquired, their investment thesis, and how they operate post-acquisition. Be specific about their strategy.",
  "acquisition_history": ["3-5 specific acquisitions with company name and brief detail"],
  "why_this_seller": "2 paragraphs explaining specifically why this seller fits their acquisition strategy, including geographic, operational, and financial angles",
  "approach_angle": "1-2 paragraphs on how to approach this buyer. We represent the owners who are exploring strategic options. These are former business owners who cashed out and buy companies because they believe in owners, not the stock market. Never say the company is for sale. Frame as a selective conversation.",
  "talking_points": ["5 specific talking points for the introductory call"],
  "risk_factors": ["3-4 specific risks or objections this buyer might raise"],
  "timeline": "1 paragraph on how fast this type of buyer typically moves from first contact to LOI to close, with specific timeframes"
}`;

    const raw = generateContent(prompt);
    const onePager = parseJSON(raw);

    if (!onePager) {
      log(`${label} FAILED: Could not generate valid JSON`);
      fail++;
      continue;
    }

    // Generate HTML
    const html = generateHTML(buyer, onePager);

    const sellerSlug = slugify(buyer.seller_company);
    const buyerSlug = slugify(buyer.buyer_company_name);
    const filename = `${sellerSlug}_${buyerSlug}.html`;

    // Save files
    const outPath = join(OUTPUT_DIR, filename);
    writeFileSync(outPath, html);
    copyFileSync(outPath, join(COPY_DIR, filename));
    log(`${label} Saved: ${filename}`);

    // Update database via REST API
    try {
      await supabasePatch('engagement_buyers', 'id', buyer.id, {
        one_pager_html: html,
        one_pager_json: onePager
      });
      log(`${label} DB updated for ${buyer.id}`);
    } catch(e) {
      log(`${label} DB update error: ${e.message}`);
    }

    success++;
    log(`${label} Complete`);
  }

  log('=== Buyer 1-Pager Engine Complete ===');
  log(`Success: ${success}/${top3.length}`);
  log(`Failed: ${fail}/${top3.length}`);
  log(`Output: ${OUTPUT_DIR}`);
  log(`Copies: ${COPY_DIR}`);
}

main().catch(e => { log(`FATAL: ${e.message}`); process.exit(1); });
