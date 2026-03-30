/**
 * Section-Level Commenting Widget for Master CRM
 * Injects comment icons on h2 elements, lets Ewing/Mark leave feedback on any section.
 * Reads/writes to Supabase page_comments table via REST API.
 */
(function() {
  const SUPABASE_URL = 'https://dwrnfpjcvydhmhnvyzov.supabase.co';
  const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3NTcyOTAsImV4cCI6MjA5MDMzMzI5MH0.z0Gu1TWdGPcdptB5W7efnYMmxBbvD353ExG99ftQivY';
  const API = SUPABASE_URL + '/rest/v1/page_comments';

  // Detect page context from URL and page content
  function getPageContext() {
    const path = window.location.pathname;
    const title = document.title || '';
    let pageType = 'hub';
    let companyName = '';

    if (path.includes('/proposal') || title.includes('Proposal')) pageType = 'proposal';
    else if (path.includes('/data') || title.includes('Data Room')) pageType = 'data_room';
    else if (path.includes('/meeting') || title.includes('Meeting')) pageType = 'meeting';
    else if (path.includes('/buyer') || title.includes('Buyer')) pageType = 'buyer_1pager';
    else if (path.includes('-hub') || title.includes('Hub')) pageType = 'hub';

    // Extract company name from title (format: "Company Name — Something")
    const m = title.match(/^(.+?)(\s*[—\-|]|$)/);
    if (m) companyName = m[1].trim();

    return { pageType, companyName };
  }

  function sectionIdFromH2(h2) {
    // Use id attribute if present, else slugify the text
    if (h2.id) return h2.id;
    const parent = h2.closest('.section, .card, section, [id]');
    if (parent && parent.id) return parent.id;
    return h2.textContent.trim().toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/_+$/, '');
  }

  // Inject styles
  const style = document.createElement('style');
  style.textContent = `
    .crm-comment-icon {
      display: inline-flex; align-items: center; justify-content: center;
      width: 26px; height: 26px; margin-left: 8px; cursor: pointer;
      border-radius: 50%; font-size: 14px; vertical-align: middle;
      background: transparent; border: 1px solid #ccc; opacity: 0.5;
      transition: all 0.2s; position: relative;
    }
    .crm-comment-icon:hover { opacity: 1; background: #eef6ff; border-color: #58a6ff; }
    .crm-comment-icon.has-comments { opacity: 1; background: #fff3cd; border-color: #f39c12; }
    .crm-comment-badge {
      position: absolute; top: -5px; right: -5px;
      background: #e74c3c; color: white; font-size: 9px; font-weight: 700;
      border-radius: 50%; width: 16px; height: 16px;
      display: flex; align-items: center; justify-content: center;
    }
    .crm-comment-overlay {
      position: fixed; top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0,0,0,0.3); z-index: 9998; display: none;
    }
    .crm-comment-panel {
      position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
      background: white; border-radius: 12px; box-shadow: 0 8px 40px rgba(0,0,0,0.25);
      width: 460px; max-width: 95vw; max-height: 80vh; overflow-y: auto;
      z-index: 9999; display: none; font-family: 'Segoe UI', system-ui, sans-serif;
      color: #1a1a2e;
    }
    .crm-comment-panel-header {
      padding: 16px 20px; border-bottom: 1px solid #eee;
      font-size: 15px; font-weight: 700; display: flex;
      justify-content: space-between; align-items: center;
    }
    .crm-comment-panel-close {
      cursor: pointer; font-size: 20px; color: #999; background: none; border: none;
    }
    .crm-comment-panel-body { padding: 16px 20px; }
    .crm-comment-existing {
      margin-bottom: 16px; border-bottom: 1px solid #f0f2f5; padding-bottom: 12px;
    }
    .crm-comment-existing:last-of-type { border-bottom: none; }
    .crm-comment-meta {
      font-size: 11px; color: #888; margin-bottom: 4px;
      display: flex; justify-content: space-between;
    }
    .crm-comment-text { font-size: 13px; line-height: 1.5; }
    .crm-comment-type-tag {
      display: inline-block; padding: 1px 6px; border-radius: 8px;
      font-size: 10px; font-weight: 600; margin-left: 6px;
    }
    .crm-comment-type-feedback { background: #e8f4fd; color: #1a73e8; }
    .crm-comment-type-fact_correction { background: #fce8e6; color: #d93025; }
    .crm-comment-type-tone_adjustment { background: #fef7e0; color: #e37400; }
    .crm-comment-type-addition_request { background: #e6f4ea; color: #137333; }
    .crm-comment-type-approval { background: #e6f4ea; color: #137333; }
    .crm-comment-type-rejection { background: #fce8e6; color: #d93025; }
    .crm-comment-status-tag {
      display: inline-block; padding: 1px 6px; border-radius: 8px;
      font-size: 10px; font-weight: 600;
    }
    .crm-comment-status-pending { background: #fff3cd; color: #856404; }
    .crm-comment-status-acknowledged { background: #cce5ff; color: #004085; }
    .crm-comment-status-applied { background: #d4edda; color: #155724; }
    .crm-comment-status-rejected { background: #f8d7da; color: #721c24; }
    .crm-comment-form label {
      display: block; font-size: 12px; font-weight: 600; color: #555;
      margin-bottom: 4px; margin-top: 12px;
    }
    .crm-comment-form select, .crm-comment-form textarea {
      width: 100%; padding: 8px 10px; border: 1px solid #ddd; border-radius: 6px;
      font-size: 13px; font-family: inherit;
    }
    .crm-comment-form textarea { min-height: 80px; resize: vertical; }
    .crm-comment-form button {
      margin-top: 14px; padding: 10px 24px; background: #16213e; color: white;
      border: none; border-radius: 6px; font-size: 13px; font-weight: 600;
      cursor: pointer; width: 100%;
    }
    .crm-comment-form button:hover { background: #1a5276; }
    .crm-comment-form button:disabled { background: #ccc; cursor: not-allowed; }
    .crm-comment-empty { font-size: 13px; color: #999; font-style: italic; margin-bottom: 12px; }
  `;
  document.head.appendChild(style);

  // Create overlay and panel
  const overlay = document.createElement('div');
  overlay.className = 'crm-comment-overlay';
  document.body.appendChild(overlay);

  const panel = document.createElement('div');
  panel.className = 'crm-comment-panel';
  document.body.appendChild(panel);

  overlay.addEventListener('click', closePanel);

  function closePanel() {
    panel.style.display = 'none';
    overlay.style.display = 'none';
  }

  const ctx = getPageContext();

  // Fetch all comments for this page
  async function fetchComments() {
    const params = new URLSearchParams({
      company_name: 'eq.' + ctx.companyName,
      page_type: 'eq.' + ctx.pageType,
      order: 'created_at.desc'
    });
    try {
      const res = await fetch(API + '?' + params.toString(), {
        headers: {
          'apikey': SUPABASE_KEY,
          'Authorization': 'Bearer ' + SUPABASE_KEY
        }
      });
      if (!res.ok) return [];
      return await res.json();
    } catch(e) {
      console.error('Comment fetch error:', e);
      return [];
    }
  }

  // Submit a comment
  async function submitComment(sectionId, commenter, commentType, text) {
    const body = {
      page_type: ctx.pageType,
      company_name: ctx.companyName,
      section_id: sectionId,
      comment_text: text,
      comment_type: commentType,
      commenter: commenter
    };
    const res = await fetch(API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': SUPABASE_KEY,
        'Authorization': 'Bearer ' + SUPABASE_KEY,
        'Prefer': 'return=representation'
      },
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error('Failed to submit: ' + res.status);
    return await res.json();
  }

  function formatDate(iso) {
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) +
           ' ' + d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  }

  function openPanel(sectionId, sectionTitle, comments) {
    const sectionComments = comments.filter(c => c.section_id === sectionId);
    let existingHtml = '';
    if (sectionComments.length === 0) {
      existingHtml = '<div class="crm-comment-empty">No comments on this section yet.</div>';
    } else {
      for (const c of sectionComments) {
        existingHtml += `
          <div class="crm-comment-existing">
            <div class="crm-comment-meta">
              <span><strong>${c.commenter}</strong>
                <span class="crm-comment-type-tag crm-comment-type-${c.comment_type}">${c.comment_type.replace('_',' ')}</span>
              </span>
              <span>
                <span class="crm-comment-status-tag crm-comment-status-${c.status}">${c.status}</span>
                ${formatDate(c.created_at)}
              </span>
            </div>
            <div class="crm-comment-text">${escapeHtml(c.comment_text)}</div>
            ${c.reply ? '<div style="margin-top:4px;font-size:12px;color:#555;"><strong>Reply:</strong> ' + escapeHtml(c.reply) + '</div>' : ''}
            ${c.resolution ? '<div style="margin-top:4px;font-size:12px;color:#27ae60;"><strong>Resolution:</strong> ' + escapeHtml(c.resolution) + '</div>' : ''}
          </div>`;
      }
    }

    panel.innerHTML = `
      <div class="crm-comment-panel-header">
        <span>${escapeHtml(sectionTitle)}</span>
        <button class="crm-comment-panel-close" id="crm-close-btn">&times;</button>
      </div>
      <div class="crm-comment-panel-body">
        ${existingHtml}
        <div class="crm-comment-form">
          <label>Who are you?</label>
          <select id="crm-commenter">
            <option value="ewing">Ewing</option>
            <option value="mark">Mark</option>
          </select>
          <label>Comment type</label>
          <select id="crm-type">
            <option value="feedback">Feedback</option>
            <option value="fact_correction">Fact Correction</option>
            <option value="tone_adjustment">Tone Adjustment</option>
            <option value="addition_request">Addition Request</option>
            <option value="approval">Approval</option>
            <option value="rejection">Rejection</option>
          </select>
          <label>Comment</label>
          <textarea id="crm-text" placeholder="Type your feedback here..."></textarea>
          <button id="crm-submit">Submit Comment</button>
        </div>
      </div>`;

    panel.style.display = 'block';
    overlay.style.display = 'block';

    document.getElementById('crm-close-btn').addEventListener('click', closePanel);
    document.getElementById('crm-submit').addEventListener('click', async function() {
      const btn = this;
      const commenter = document.getElementById('crm-commenter').value;
      const type = document.getElementById('crm-type').value;
      const text = document.getElementById('crm-text').value.trim();
      if (!text) { alert('Please enter a comment.'); return; }
      btn.disabled = true;
      btn.textContent = 'Submitting...';
      try {
        await submitComment(sectionId, commenter, type, text);
        btn.textContent = 'Submitted!';
        btn.style.background = '#27ae60';
        // Refresh badges and panel after short delay
        setTimeout(async () => {
          closePanel();
          await init();
        }, 800);
      } catch(e) {
        btn.disabled = false;
        btn.textContent = 'Submit Comment';
        alert('Error submitting comment: ' + e.message);
      }
    });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  // Main init: attach icons to all h2 elements
  async function init() {
    // Remove any existing icons (for re-init)
    document.querySelectorAll('.crm-comment-icon').forEach(el => el.remove());

    const comments = await fetchComments();
    const h2s = document.querySelectorAll('h2');

    h2s.forEach(h2 => {
      const sectionId = sectionIdFromH2(h2);
      const sectionTitle = h2.textContent.trim();
      const count = comments.filter(c => c.section_id === sectionId).length;

      const icon = document.createElement('span');
      icon.className = 'crm-comment-icon' + (count > 0 ? ' has-comments' : '');
      icon.innerHTML = '\uD83D\uDCAC' + (count > 0 ? `<span class="crm-comment-badge">${count}</span>` : '');
      icon.title = count > 0 ? `${count} comment${count > 1 ? 's' : ''}` : 'Add comment';
      icon.addEventListener('click', function(e) {
        e.stopPropagation();
        openPanel(sectionId, sectionTitle, comments);
      });

      h2.appendChild(icon);
    });
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
