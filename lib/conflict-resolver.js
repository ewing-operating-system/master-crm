/**
 * Conflict Resolution Modal for Master CRM
 *
 * SYSTEM RULE: Every page, every section, every element must have feedback capability.
 * The comment widget (comment-widget.js) MUST be present on ALL HTML pages.
 *
 * Detects when two commenters leave conflicting feedback on the same section.
 * Shows a red banner + floating modal for resolution.
 * Stores resolutions in the conflict_resolutions table via Supabase REST API.
 */
(function() {
  'use strict';

  const SUPABASE_URL = 'https://dwrnfpjcvydhmhnvyzov.supabase.co';
  const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3NTcyOTAsImV4cCI6MjA5MDMzMzI5MH0.z0Gu1TWdGPcdptB5W7efnYMmxBbvD353ExG99ftQivY';
  const COMMENTS_API = SUPABASE_URL + '/rest/v1/page_comments';
  const CONFLICTS_API = SUPABASE_URL + '/rest/v1/conflict_resolutions';

  const headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': 'Bearer ' + SUPABASE_KEY,
    'Content-Type': 'application/json'
  };

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
    const m = title.match(/^(.+?)(\s*[—\-|]|$)/);
    if (m) companyName = m[1].trim();
    return { pageType, companyName };
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function formatDate(iso) {
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) +
           ' ' + d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  }

  // Inject styles for conflict resolution
  const style = document.createElement('style');
  style.textContent = `
    .crm-conflict-banner {
      position: fixed; top: 0; left: 0; right: 0; z-index: 100000;
      background: #dc3545; color: white; padding: 12px 20px;
      font-family: 'Segoe UI', system-ui, sans-serif;
      font-size: 15px; font-weight: 700; text-align: center;
      box-shadow: 0 2px 12px rgba(220,53,69,0.4);
      cursor: pointer; display: none;
    }
    .crm-conflict-banner:hover { background: #c82333; }
    .crm-conflict-section-highlight {
      outline: 3px solid #dc3545 !important;
      outline-offset: 4px;
      position: relative;
    }
    .crm-conflict-arrow {
      position: absolute; top: -30px; left: 50%; transform: translateX(-50%);
      font-size: 24px; color: #dc3545; animation: crm-bounce 1s infinite;
      z-index: 100;
    }
    @keyframes crm-bounce {
      0%, 100% { transform: translateX(-50%) translateY(0); }
      50% { transform: translateX(-50%) translateY(-8px); }
    }
    .crm-conflict-overlay {
      position: fixed; top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0,0,0,0.5); z-index: 100001; display: none;
    }
    .crm-conflict-modal {
      position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
      background: white; border-radius: 16px;
      box-shadow: 0 12px 60px rgba(0,0,0,0.35);
      width: 600px; max-width: 95vw; max-height: 85vh; overflow-y: auto;
      z-index: 100002; display: none;
      font-family: 'Segoe UI', system-ui, sans-serif; color: #1a1a2e;
    }
    .crm-conflict-modal-header {
      padding: 20px 24px; border-bottom: 2px solid #dc3545;
      font-size: 17px; font-weight: 700; display: flex;
      justify-content: space-between; align-items: center;
      color: #dc3545;
    }
    .crm-conflict-modal-close {
      cursor: pointer; font-size: 22px; color: #999; background: none; border: none;
    }
    .crm-conflict-modal-body { padding: 20px 24px; }
    .crm-conflict-side {
      background: #f8f9fa; border-radius: 8px; padding: 14px; margin-bottom: 12px;
      border-left: 4px solid #007bff;
    }
    .crm-conflict-side.side-b { border-left-color: #28a745; }
    .crm-conflict-side h4 { margin: 0 0 6px; font-size: 14px; color: #333; }
    .crm-conflict-side .meta { font-size: 11px; color: #888; margin-bottom: 6px; }
    .crm-conflict-side .text { font-size: 13px; line-height: 1.5; }
    .crm-conflict-resolution-form { margin-top: 16px; }
    .crm-conflict-resolution-form label {
      display: block; font-size: 13px; font-weight: 600; color: #555; margin-bottom: 6px;
    }
    .crm-conflict-resolution-form textarea {
      width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px;
      font-size: 13px; font-family: inherit; min-height: 100px; resize: vertical;
    }
    .crm-conflict-resolution-form select {
      width: 100%; padding: 8px 10px; border: 1px solid #ddd; border-radius: 6px;
      font-size: 13px; font-family: inherit; margin-bottom: 12px;
    }
    .crm-conflict-resolve-btn {
      margin-top: 14px; padding: 12px 24px; background: #28a745; color: white;
      border: none; border-radius: 8px; font-size: 14px; font-weight: 600;
      cursor: pointer; width: 100%;
    }
    .crm-conflict-resolve-btn:hover { background: #218838; }
    .crm-conflict-resolve-btn:disabled { background: #ccc; cursor: not-allowed; }
    .crm-conflict-count-badge {
      display: inline-block; background: white; color: #dc3545;
      border-radius: 50%; width: 24px; height: 24px; text-align: center;
      line-height: 24px; font-size: 13px; font-weight: 700; margin-left: 8px;
    }
  `;
  document.head.appendChild(style);

  // Create banner
  const banner = document.createElement('div');
  banner.className = 'crm-conflict-banner';
  document.body.appendChild(banner);

  // Create overlay and modal
  const overlay = document.createElement('div');
  overlay.className = 'crm-conflict-overlay';
  document.body.appendChild(overlay);

  const modal = document.createElement('div');
  modal.className = 'crm-conflict-modal';
  document.body.appendChild(modal);

  overlay.addEventListener('click', closeModal);

  function closeModal() {
    modal.style.display = 'none';
    overlay.style.display = 'none';
  }

  /**
   * Detect conflicts: two different commenters on the same company+section
   * with different comment_type or contradictory content, both pending/acknowledged.
   */
  function detectConflicts(comments) {
    const grouped = {};
    for (const c of comments) {
      if (c.status === 'applied' || c.status === 'rejected') continue;
      const key = c.company_name + '::' + c.section_id;
      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(c);
    }

    const conflicts = [];
    for (const key of Object.keys(grouped)) {
      const group = grouped[key];
      // Get unique commenters
      const byCommenter = {};
      for (const c of group) {
        if (!byCommenter[c.commenter]) byCommenter[c.commenter] = [];
        byCommenter[c.commenter].push(c);
      }
      const commenters = Object.keys(byCommenter);
      if (commenters.length < 2) continue;

      // Check pairs for conflicts
      for (let i = 0; i < commenters.length; i++) {
        for (let j = i + 1; j < commenters.length; j++) {
          const a = byCommenter[commenters[i]];
          const b = byCommenter[commenters[j]];
          // Use most recent from each commenter
          const commentA = a[0]; // already sorted desc by created_at
          const commentB = b[0];
          // Conflict if different types or both have substance
          if (commentA.comment_type !== commentB.comment_type ||
              (commentA.comment_text && commentB.comment_text)) {
            conflicts.push({
              section_id: commentA.section_id,
              company_name: commentA.company_name,
              commentA: commentA,
              commentB: commentB
            });
          }
        }
      }
    }
    return conflicts;
  }

  function openConflictModal(conflict) {
    const a = conflict.commentA;
    const b = conflict.commentB;

    modal.innerHTML = `
      <div class="crm-conflict-modal-header">
        <span>Conflict Resolution: ${escapeHtml(conflict.section_id.replace(/_/g, ' '))}</span>
        <button class="crm-conflict-modal-close" id="crm-conflict-close">&times;</button>
      </div>
      <div class="crm-conflict-modal-body">
        <div class="crm-conflict-side">
          <h4>${escapeHtml(a.commenter)}</h4>
          <div class="meta">${a.comment_type.replace('_', ' ')} &mdash; ${formatDate(a.created_at)}</div>
          <div class="text">${escapeHtml(a.comment_text)}</div>
        </div>
        <div class="crm-conflict-side side-b">
          <h4>${escapeHtml(b.commenter)}</h4>
          <div class="meta">${b.comment_type.replace('_', ' ')} &mdash; ${formatDate(b.created_at)}</div>
          <div class="text">${escapeHtml(b.comment_text)}</div>
        </div>
        <div class="crm-conflict-resolution-form">
          <label>Who is resolving?</label>
          <select id="crm-conflict-resolver">
            <option value="ewing">Ewing</option>
            <option value="mark">Mark</option>
          </select>
          <label>Resolution — combine both perspectives or choose one:</label>
          <textarea id="crm-conflict-text" placeholder="Type the resolved version here..."></textarea>
          <button class="crm-conflict-resolve-btn" id="crm-conflict-submit">Resolve Conflict</button>
        </div>
      </div>
    `;

    modal.style.display = 'block';
    overlay.style.display = 'block';

    document.getElementById('crm-conflict-close').addEventListener('click', closeModal);
    document.getElementById('crm-conflict-submit').addEventListener('click', async function() {
      const btn = this;
      const resolver = document.getElementById('crm-conflict-resolver').value;
      const text = document.getElementById('crm-conflict-text').value.trim();
      if (!text) { alert('Please enter a resolution.'); return; }

      btn.disabled = true;
      btn.textContent = 'Saving...';

      try {
        // Store resolution
        const resData = {
          company_name: conflict.company_name,
          section_id: conflict.section_id,
          comment_id_a: a.id,
          commenter_a: a.commenter,
          comment_id_b: b.id,
          commenter_b: b.commenter,
          resolution_options: JSON.stringify([{ text: text, chosen: true }]),
          chosen_option: 0,
          chosen_by: resolver,
          resolution_text: text,
          resolved_at: new Date().toISOString()
        };

        await fetch(CONFLICTS_API, {
          method: 'POST',
          headers: { ...headers, 'Prefer': 'return=representation' },
          body: JSON.stringify(resData)
        });

        // Mark both comments as applied with the resolution
        for (const cid of [a.id, b.id]) {
          await fetch(COMMENTS_API + '?id=eq.' + cid, {
            method: 'PATCH',
            headers: { ...headers, 'Prefer': 'return=minimal' },
            body: JSON.stringify({ status: 'applied', resolution: text })
          });
        }

        btn.textContent = 'Resolved!';
        btn.style.background = '#17a2b8';
        setTimeout(() => {
          closeModal();
          init(); // re-check for remaining conflicts
        }, 800);
      } catch(e) {
        btn.disabled = false;
        btn.textContent = 'Resolve Conflict';
        alert('Error saving resolution: ' + e.message);
      }
    });
  }

  function highlightSection(sectionId) {
    // Find the section element
    const h2s = document.querySelectorAll('h2');
    for (const h2 of h2s) {
      const sid = h2.id || (h2.closest('[id]') || {}).id ||
        h2.textContent.trim().toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/_+$/, '');
      if (sid === sectionId) {
        const section = h2.closest('.section, .card, section') || h2.parentElement;
        section.classList.add('crm-conflict-section-highlight');
        // Add bouncing arrow
        const arrow = document.createElement('div');
        arrow.className = 'crm-conflict-arrow';
        arrow.innerHTML = '&#11015;';
        section.style.position = 'relative';
        section.prepend(arrow);
        return;
      }
    }
  }

  async function init() {
    // Remove previous highlights and arrows
    document.querySelectorAll('.crm-conflict-section-highlight').forEach(el => {
      el.classList.remove('crm-conflict-section-highlight');
    });
    document.querySelectorAll('.crm-conflict-arrow').forEach(el => el.remove());

    const ctx = getPageContext();
    if (!ctx.companyName) return;

    // Fetch all active comments for this company
    const params = new URLSearchParams({
      company_name: 'eq.' + ctx.companyName,
      order: 'created_at.desc'
    });
    try {
      const res = await fetch(COMMENTS_API + '?' + params.toString(), { headers });
      if (!res.ok) return;
      const comments = await res.json();

      // Also check if there are already unresolved conflicts
      const resParams = new URLSearchParams({
        company_name: 'eq.' + ctx.companyName,
        resolved_at: 'is.null'
      });
      const resRes = await fetch(CONFLICTS_API + '?' + resParams.toString(), { headers });
      const existingConflicts = resRes.ok ? await resRes.json() : [];

      const conflicts = detectConflicts(comments);
      // Filter out already-resolved conflicts
      const resolvedPairs = new Set(existingConflicts.map(c =>
        c.comment_id_a + '::' + c.comment_id_b));

      const unresolvedConflicts = conflicts.filter(c => {
        const key1 = c.commentA.id + '::' + c.commentB.id;
        const key2 = c.commentB.id + '::' + c.commentA.id;
        return !resolvedPairs.has(key1) && !resolvedPairs.has(key2);
      });

      if (unresolvedConflicts.length === 0) {
        banner.style.display = 'none';
        return;
      }

      // Show banner
      banner.innerHTML = '\u26A0\uFE0F CONFLICT RESOLUTION NEEDED' +
        '<span class="crm-conflict-count-badge">' + unresolvedConflicts.length + '</span>';
      banner.style.display = 'block';

      // Highlight first conflict section
      highlightSection(unresolvedConflicts[0].section_id);

      // Click banner → open first conflict modal
      banner.onclick = function() {
        openConflictModal(unresolvedConflicts[0]);
      };

      // Push body down for banner
      document.body.style.paddingTop = (parseInt(getComputedStyle(document.body).paddingTop) || 0) + 48 + 'px';

    } catch(e) {
      console.error('[conflict-resolver] Error:', e);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    // Delay slightly to let comment-widget load first
    setTimeout(init, 500);
  }
})();
