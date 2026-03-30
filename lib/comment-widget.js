/**
 * Section-Level Commenting Widget for Master CRM
 * Injects comment icons on h2 elements, lets Ewing/Mark leave feedback on any section.
 * Reads/writes to Supabase page_comments table via REST API.
 *
 * D→C Feedback Conversation System (Steps 6-9):
 * - Shows conversation threads (comment → system reply → user response)
 * - Displays "thinking..." state while awaiting processor response
 * - Shows Original vs Revised content toggle when revision_ready
 * - Supports threaded replies to clarifying questions
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
    .crm-comment-icon.needs-response { opacity: 1; background: #fce8e6; border-color: #d93025; animation: crm-pulse 2s infinite; }
    @keyframes crm-pulse { 0%,100% { box-shadow: 0 0 0 0 rgba(217,48,37,0.3); } 50% { box-shadow: 0 0 0 6px rgba(217,48,37,0); } }
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
      width: 520px; max-width: 95vw; max-height: 85vh; overflow-y: auto;
      z-index: 9999; display: none; font-family: 'Segoe UI', system-ui, sans-serif;
      color: #1a1a2e;
    }
    .crm-comment-panel-header {
      padding: 16px 20px; border-bottom: 1px solid #eee;
      font-size: 15px; font-weight: 700; display: flex;
      justify-content: space-between; align-items: center;
      position: sticky; top: 0; background: white; z-index: 1;
    }
    .crm-comment-panel-close {
      cursor: pointer; font-size: 20px; color: #999; background: none; border: none;
    }
    .crm-comment-panel-body { padding: 16px 20px; }
    .crm-comment-existing {
      margin-bottom: 16px; border: 1px solid #f0f2f5; border-radius: 8px;
      padding: 12px; background: #fafbfc;
    }
    .crm-comment-meta {
      font-size: 11px; color: #888; margin-bottom: 4px;
      display: flex; justify-content: space-between; flex-wrap: wrap; gap: 4px;
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
    .crm-comment-status-awaiting_response { background: #fce8e6; color: #d93025; }
    .crm-comment-status-responded { background: #cce5ff; color: #004085; }
    .crm-comment-status-revision_ready { background: #d1ecf1; color: #0c5460; }
    .crm-comment-status-acknowledged { background: #cce5ff; color: #004085; }
    .crm-comment-status-applied { background: #d4edda; color: #155724; }
    .crm-comment-status-rejected { background: #f8d7da; color: #721c24; }

    /* Conversation thread */
    .crm-thread { margin-top: 10px; border-left: 3px solid #58a6ff; padding-left: 12px; }
    .crm-thread-msg { margin-bottom: 8px; }
    .crm-thread-msg.system { color: #1a73e8; }
    .crm-thread-msg.user { color: #333; }
    .crm-thread-role { font-size: 10px; font-weight: 700; text-transform: uppercase; color: #888; }
    .crm-thread-text { font-size: 13px; line-height: 1.5; white-space: pre-wrap; }
    .crm-thread-time { font-size: 10px; color: #aaa; }

    /* Thinking state */
    .crm-thinking {
      display: flex; align-items: center; gap: 8px;
      padding: 10px 14px; background: #f0f6ff; border-radius: 8px;
      margin-top: 8px; font-size: 13px; color: #1a73e8;
    }
    .crm-thinking-dots span {
      display: inline-block; width: 6px; height: 6px; border-radius: 50%;
      background: #1a73e8; margin: 0 2px; animation: crm-dot-bounce 1.4s ease-in-out infinite;
    }
    .crm-thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
    .crm-thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes crm-dot-bounce { 0%,80%,100% { transform: scale(0.6); opacity: 0.4; } 40% { transform: scale(1); opacity: 1; } }

    /* Reply area */
    .crm-reply-area { margin-top: 10px; }
    .crm-reply-area textarea {
      width: 100%; padding: 8px 10px; border: 1px solid #58a6ff; border-radius: 6px;
      font-size: 13px; font-family: inherit; min-height: 60px; resize: vertical;
      background: #f8fbff;
    }
    .crm-reply-area button {
      margin-top: 6px; padding: 8px 18px; background: #1a73e8; color: white;
      border: none; border-radius: 6px; font-size: 12px; font-weight: 600;
      cursor: pointer; float: right;
    }
    .crm-reply-area button:hover { background: #1558b0; }
    .crm-reply-area button:disabled { background: #ccc; cursor: not-allowed; }

    /* Revision toggle */
    .crm-revision-toggle {
      display: flex; gap: 0; margin-top: 10px; border-radius: 6px; overflow: hidden;
      border: 1px solid #ddd;
    }
    .crm-revision-tab {
      flex: 1; padding: 8px; text-align: center; font-size: 12px; font-weight: 600;
      cursor: pointer; background: #f5f5f5; color: #666; border: none;
      transition: all 0.2s;
    }
    .crm-revision-tab.active { background: #16213e; color: white; }
    .crm-revision-content {
      margin-top: 8px; padding: 12px; border-radius: 6px;
      font-size: 13px; line-height: 1.6; white-space: pre-wrap;
    }
    .crm-revision-original { background: #fff5f5; border: 1px solid #fce8e6; }
    .crm-revision-revised { background: #f0fff4; border: 1px solid #d4edda; }

    /* Accept/reject buttons for revisions */
    .crm-revision-actions { display: flex; gap: 8px; margin-top: 10px; }
    .crm-revision-actions button {
      flex: 1; padding: 8px; border: none; border-radius: 6px;
      font-size: 12px; font-weight: 600; cursor: pointer;
    }
    .crm-btn-accept { background: #27ae60; color: white; }
    .crm-btn-accept:hover { background: #219a52; }
    .crm-btn-reject { background: #e74c3c; color: white; }
    .crm-btn-reject:hover { background: #c0392b; }

    /* New comment form */
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
    .crm-divider { border: none; border-top: 1px solid #eee; margin: 16px 0; }
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

  // ---- API helpers ----

  async function fetchComments() {
    const params = new URLSearchParams({
      company_name: 'eq.' + ctx.companyName,
      page_type: 'eq.' + ctx.pageType,
      order: 'created_at.asc'
    });
    try {
      const res = await fetch(API + '?' + params.toString(), {
        headers: { 'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY }
      });
      if (!res.ok) return [];
      return await res.json();
    } catch(e) {
      console.error('Comment fetch error:', e);
      return [];
    }
  }

  async function submitComment(sectionId, commenter, commentType, text) {
    const body = {
      page_type: ctx.pageType,
      company_name: ctx.companyName,
      section_id: sectionId,
      comment_text: text,
      comment_type: commentType,
      commenter: commenter,
      status: 'pending'
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

  async function patchComment(commentId, updates) {
    const res = await fetch(API + '?id=eq.' + commentId, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'apikey': SUPABASE_KEY,
        'Authorization': 'Bearer ' + SUPABASE_KEY,
        'Prefer': 'return=representation'
      },
      body: JSON.stringify(updates)
    });
    if (!res.ok) throw new Error('Failed to update: ' + res.status);
    return await res.json();
  }

  // ---- Rendering ----

  function formatDate(iso) {
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) +
           ' ' + d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function renderConversationThread(comment) {
    const thread = comment.conversation_thread || [];
    if (thread.length === 0 && !comment.reply) return '';

    let html = '<div class="crm-thread">';

    // If there's a reply but no thread entries, show the reply directly
    if (comment.reply && thread.length === 0) {
      html += `<div class="crm-thread-msg system">
        <div class="crm-thread-role">System</div>
        <div class="crm-thread-text">${escapeHtml(comment.reply)}</div>
      </div>`;
    }

    // Render thread entries
    for (const msg of thread) {
      const roleClass = msg.role === 'system' ? 'system' : 'user';
      const roleLabel = msg.role === 'system' ? 'System' : comment.commenter || 'User';
      html += `<div class="crm-thread-msg ${roleClass}">
        <div class="crm-thread-role">${escapeHtml(roleLabel)}
          ${msg.timestamp ? '<span class="crm-thread-time"> &middot; ' + formatDate(msg.timestamp) + '</span>' : ''}
        </div>
        <div class="crm-thread-text">${escapeHtml(msg.text)}</div>
      </div>`;
    }

    html += '</div>';
    return html;
  }

  function renderThinkingState() {
    return `<div class="crm-thinking">
      <div class="crm-thinking-dots"><span></span><span></span><span></span></div>
      Processing your comment... Clarifying questions will appear shortly.
    </div>`;
  }

  function renderReplyArea(comment) {
    if (comment.status !== 'awaiting_response') return '';
    return `<div class="crm-reply-area" data-comment-id="${comment.id}">
      <textarea placeholder="Answer the questions above..." class="crm-reply-input"></textarea>
      <button class="crm-reply-submit">Send Response</button>
      <div style="clear:both;"></div>
    </div>`;
  }

  function renderRevisionToggle(comment) {
    if (comment.status !== 'revision_ready') return '';
    const original = comment.original_content || '(original not captured)';
    const revised = comment.revised_content || '(revision pending)';

    return `<div data-comment-id="${comment.id}">
      <div class="crm-revision-toggle">
        <button class="crm-revision-tab active" data-view="revised">Revised</button>
        <button class="crm-revision-tab" data-view="original">Original</button>
      </div>
      <div class="crm-revision-content crm-revision-revised crm-rev-revised">${escapeHtml(revised)}</div>
      <div class="crm-revision-content crm-revision-original crm-rev-original" style="display:none;">${escapeHtml(original)}</div>
      <div class="crm-revision-actions">
        <button class="crm-btn-accept crm-accept-revision">Accept Revision</button>
        <button class="crm-btn-reject crm-reject-revision">Reject</button>
      </div>
    </div>`;
  }

  function renderComment(c) {
    let statusLabel = c.status.replace(/_/g, ' ');

    let html = `<div class="crm-comment-existing" data-id="${c.id}">
      <div class="crm-comment-meta">
        <span><strong>${escapeHtml(c.commenter)}</strong>
          <span class="crm-comment-type-tag crm-comment-type-${c.comment_type}">${c.comment_type.replace(/_/g,' ')}</span>
        </span>
        <span>
          <span class="crm-comment-status-tag crm-comment-status-${c.status}">${statusLabel}</span>
          ${formatDate(c.created_at)}
        </span>
      </div>
      <div class="crm-comment-text">${escapeHtml(c.comment_text)}</div>`;

    // Show thinking state for pending comments
    if (c.status === 'pending') {
      html += renderThinkingState();
    }

    // Show conversation thread
    html += renderConversationThread(c);

    // Show reply input if awaiting response
    html += renderReplyArea(c);

    // Show revision toggle if ready
    html += renderRevisionToggle(c);

    // Show resolution if applied
    if (c.resolution) {
      html += `<div style="margin-top:8px;font-size:12px;color:#27ae60;"><strong>Resolution:</strong> ${escapeHtml(c.resolution)}</div>`;
    }

    html += '</div>';
    return html;
  }

  function openPanel(sectionId, sectionTitle, comments) {
    const sectionComments = comments.filter(c => c.section_id === sectionId && !c.parent_comment_id);
    let existingHtml = '';
    if (sectionComments.length === 0) {
      existingHtml = '<div class="crm-comment-empty">No comments on this section yet.</div>';
    } else {
      for (const c of sectionComments) {
        existingHtml += renderComment(c);
      }
    }

    panel.innerHTML = `
      <div class="crm-comment-panel-header">
        <span>${escapeHtml(sectionTitle)}</span>
        <button class="crm-comment-panel-close" id="crm-close-btn">&times;</button>
      </div>
      <div class="crm-comment-panel-body">
        ${existingHtml}
        <hr class="crm-divider">
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

    // Close button
    document.getElementById('crm-close-btn').addEventListener('click', closePanel);

    // Submit new comment
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

    // Bind reply submit buttons
    panel.querySelectorAll('.crm-reply-submit').forEach(btn => {
      btn.addEventListener('click', async function() {
        const area = this.closest('.crm-reply-area');
        const commentId = area.dataset.commentId;
        const textarea = area.querySelector('.crm-reply-input');
        const text = textarea.value.trim();
        if (!text) { alert('Please enter a response.'); return; }

        this.disabled = true;
        this.textContent = 'Sending...';

        try {
          // Get current thread
          const comment = sectionComments.find(c => c.id === commentId);
          const thread = (comment && comment.conversation_thread) || [];
          thread.push({
            role: 'user',
            text: text,
            timestamp: new Date().toISOString()
          });

          await patchComment(commentId, {
            user_response: text,
            status: 'responded',
            conversation_thread: thread
          });

          this.textContent = 'Sent!';
          this.style.background = '#27ae60';
          setTimeout(async () => {
            closePanel();
            await init();
          }, 800);
        } catch(e) {
          this.disabled = false;
          this.textContent = 'Send Response';
          alert('Error sending response: ' + e.message);
        }
      });
    });

    // Bind revision toggle tabs
    panel.querySelectorAll('.crm-revision-toggle').forEach(toggle => {
      toggle.querySelectorAll('.crm-revision-tab').forEach(tab => {
        tab.addEventListener('click', function() {
          const container = this.closest('[data-comment-id]');
          const view = this.dataset.view;

          // Toggle active tab
          toggle.querySelectorAll('.crm-revision-tab').forEach(t => t.classList.remove('active'));
          this.classList.add('active');

          // Toggle content
          const revised = container.querySelector('.crm-rev-revised');
          const original = container.querySelector('.crm-rev-original');
          if (view === 'revised') {
            revised.style.display = 'block';
            original.style.display = 'none';
          } else {
            revised.style.display = 'none';
            original.style.display = 'block';
          }
        });
      });
    });

    // Bind accept/reject buttons
    panel.querySelectorAll('.crm-accept-revision').forEach(btn => {
      btn.addEventListener('click', async function() {
        const container = this.closest('[data-comment-id]');
        const commentId = container.dataset.commentId;
        this.disabled = true;
        this.textContent = 'Accepting...';
        try {
          await patchComment(commentId, { status: 'applied' });
          this.textContent = 'Accepted!';
          this.style.background = '#219a52';
          setTimeout(async () => {
            closePanel();
            await init();
          }, 800);
        } catch(e) {
          this.disabled = false;
          this.textContent = 'Accept Revision';
          alert('Error: ' + e.message);
        }
      });
    });

    panel.querySelectorAll('.crm-reject-revision').forEach(btn => {
      btn.addEventListener('click', async function() {
        const container = this.closest('[data-comment-id]');
        const commentId = container.dataset.commentId;
        this.disabled = true;
        this.textContent = 'Rejecting...';
        try {
          await patchComment(commentId, { status: 'rejected' });
          this.textContent = 'Rejected';
          this.style.background = '#999';
          setTimeout(async () => {
            closePanel();
            await init();
          }, 800);
        } catch(e) {
          this.disabled = false;
          this.textContent = 'Reject';
          alert('Error: ' + e.message);
        }
      });
    });
  }

  // ---- Icon injection ----

  async function init() {
    document.querySelectorAll('.crm-comment-icon').forEach(el => el.remove());

    const comments = await fetchComments();
    const h2s = document.querySelectorAll('h2');

    h2s.forEach(h2 => {
      const sectionId = sectionIdFromH2(h2);
      const sectionTitle = h2.textContent.trim();
      const sectionComments = comments.filter(c => c.section_id === sectionId);
      const count = sectionComments.length;
      const needsResponse = sectionComments.some(c => c.status === 'awaiting_response');
      const hasRevision = sectionComments.some(c => c.status === 'revision_ready');

      const icon = document.createElement('span');
      let iconClass = 'crm-comment-icon';
      if (needsResponse) iconClass += ' needs-response';
      else if (count > 0) iconClass += ' has-comments';
      icon.className = iconClass;

      let badge = '';
      if (needsResponse) {
        badge = '<span class="crm-comment-badge" style="background:#d93025;">!</span>';
      } else if (hasRevision) {
        badge = '<span class="crm-comment-badge" style="background:#0c5460;">R</span>';
      } else if (count > 0) {
        badge = `<span class="crm-comment-badge">${count}</span>`;
      }

      icon.innerHTML = '\uD83D\uDCAC' + badge;
      icon.title = needsResponse ? 'Action needed: respond to clarifying question'
                  : hasRevision ? 'Revision ready for review'
                  : count > 0 ? `${count} comment${count > 1 ? 's' : ''}`
                  : 'Add comment';

      icon.addEventListener('click', function(e) {
        e.stopPropagation();
        openPanel(sectionId, sectionTitle, comments);
      });

      h2.appendChild(icon);
    });

    // Auto-refresh every 30 seconds to pick up processor responses
    if (!window._crmCommentRefreshTimer) {
      window._crmCommentRefreshTimer = setInterval(async () => {
        // Only refresh icons, don't re-open panel
        if (panel.style.display !== 'block') {
          document.querySelectorAll('.crm-comment-icon').forEach(el => el.remove());
          const freshComments = await fetchComments();
          const h2s = document.querySelectorAll('h2');
          h2s.forEach(h2 => {
            const sectionId = sectionIdFromH2(h2);
            const sectionTitle = h2.textContent.trim();
            const sectionComments = freshComments.filter(c => c.section_id === sectionId);
            const count = sectionComments.length;
            const needsResponse = sectionComments.some(c => c.status === 'awaiting_response');
            const hasRevision = sectionComments.some(c => c.status === 'revision_ready');

            const icon = document.createElement('span');
            let iconClass = 'crm-comment-icon';
            if (needsResponse) iconClass += ' needs-response';
            else if (count > 0) iconClass += ' has-comments';
            icon.className = iconClass;

            let badge = '';
            if (needsResponse) badge = '<span class="crm-comment-badge" style="background:#d93025;">!</span>';
            else if (hasRevision) badge = '<span class="crm-comment-badge" style="background:#0c5460;">R</span>';
            else if (count > 0) badge = `<span class="crm-comment-badge">${count}</span>`;

            icon.innerHTML = '\uD83D\uDCAC' + badge;
            icon.title = needsResponse ? 'Action needed' : hasRevision ? 'Revision ready' : count > 0 ? `${count} comment${count > 1 ? 's' : ''}` : 'Add comment';
            icon.addEventListener('click', function(e) {
              e.stopPropagation();
              openPanel(sectionId, sectionTitle, freshComments);
            });
            h2.appendChild(icon);
          });
        }
      }, 30000);
    }
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
