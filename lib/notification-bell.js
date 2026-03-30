/**
 * Notification Bell Widget for Master CRM
 *
 * SYSTEM RULE: Every page, every section, every element must have feedback capability.
 * The comment widget (comment-widget.js) MUST be present on ALL HTML pages.
 *
 * Injects a notification bell icon in the top-right corner of every page.
 * Shows unread count, click opens dropdown with recent notifications.
 * Reads from Supabase notifications table via REST API.
 */
(function() {
  'use strict';

  const SUPABASE_URL = 'https://dwrnfpjcvydhmhnvyzov.supabase.co';
  const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3NTcyOTAsImV4cCI6MjA5MDMzMzI5MH0.z0Gu1TWdGPcdptB5W7efnYMmxBbvD353ExG99ftQivY';
  const NOTIF_API = SUPABASE_URL + '/rest/v1/notifications';

  const headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': 'Bearer ' + SUPABASE_KEY,
    'Content-Type': 'application/json'
  };

  // Detect current user (default to ewing, can be overridden)
  const currentUser = (localStorage.getItem('crm_user') || 'ewing').toLowerCase();

  // Inject styles
  const style = document.createElement('style');
  style.textContent = `
    .crm-notif-bell {
      position: fixed; top: 12px; right: 16px; z-index: 99998;
      width: 40px; height: 40px; border-radius: 50%;
      background: #16213e; color: white; border: none;
      cursor: pointer; font-size: 20px; display: flex;
      align-items: center; justify-content: center;
      box-shadow: 0 2px 10px rgba(0,0,0,0.2);
      transition: all 0.2s;
    }
    .crm-notif-bell:hover { background: #1a5276; transform: scale(1.1); }
    .crm-notif-badge {
      position: absolute; top: -4px; right: -4px;
      background: #e74c3c; color: white; font-size: 11px; font-weight: 700;
      border-radius: 50%; min-width: 20px; height: 20px;
      display: flex; align-items: center; justify-content: center;
      padding: 0 4px;
    }
    .crm-notif-badge.hidden { display: none; }
    .crm-notif-dropdown {
      position: fixed; top: 58px; right: 16px; z-index: 99999;
      background: white; border-radius: 12px;
      box-shadow: 0 8px 40px rgba(0,0,0,0.25);
      width: 380px; max-width: 95vw; max-height: 70vh; overflow-y: auto;
      display: none; font-family: 'Segoe UI', system-ui, sans-serif;
      color: #1a1a2e;
    }
    .crm-notif-dropdown.open { display: block; }
    .crm-notif-header {
      padding: 14px 18px; border-bottom: 1px solid #eee;
      font-size: 15px; font-weight: 700;
      display: flex; justify-content: space-between; align-items: center;
    }
    .crm-notif-mark-all {
      font-size: 12px; color: #1a73e8; cursor: pointer;
      background: none; border: none; font-weight: 600;
    }
    .crm-notif-mark-all:hover { text-decoration: underline; }
    .crm-notif-item {
      padding: 12px 18px; border-bottom: 1px solid #f5f5f5;
      cursor: pointer; transition: background 0.15s;
    }
    .crm-notif-item:hover { background: #f8f9fa; }
    .crm-notif-item.unread { background: #eef6ff; }
    .crm-notif-item.unread:hover { background: #dceeff; }
    .crm-notif-item-title {
      font-size: 13px; font-weight: 600; margin-bottom: 3px;
    }
    .crm-notif-item-body {
      font-size: 12px; color: #666; line-height: 1.4;
      max-height: 40px; overflow: hidden;
    }
    .crm-notif-item-time {
      font-size: 10px; color: #aaa; margin-top: 4px;
    }
    .crm-notif-empty {
      padding: 30px 18px; text-align: center;
      font-size: 13px; color: #999; font-style: italic;
    }
    .crm-notif-type-icon {
      display: inline-block; margin-right: 6px; font-size: 12px;
    }
  `;
  document.head.appendChild(style);

  // Create bell button
  const bell = document.createElement('button');
  bell.className = 'crm-notif-bell';
  bell.innerHTML = '\uD83D\uDD14<span class="crm-notif-badge hidden" id="crm-notif-count">0</span>';
  bell.title = 'Notifications';
  document.body.appendChild(bell);

  // Create dropdown
  const dropdown = document.createElement('div');
  dropdown.className = 'crm-notif-dropdown';
  document.body.appendChild(dropdown);

  // Toggle dropdown
  bell.addEventListener('click', function(e) {
    e.stopPropagation();
    dropdown.classList.toggle('open');
    if (dropdown.classList.contains('open')) {
      loadNotifications();
    }
  });

  // Close on outside click
  document.addEventListener('click', function(e) {
    if (!dropdown.contains(e.target) && e.target !== bell) {
      dropdown.classList.remove('open');
    }
  });

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function timeAgo(iso) {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return mins + 'm ago';
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return hrs + 'h ago';
    const days = Math.floor(hrs / 24);
    return days + 'd ago';
  }

  function typeIcon(type) {
    const icons = {
      comment: '\uD83D\uDCAC',
      fact_correction: '\u2757',
      conflict: '\u26A0\uFE0F',
      approval: '\u2705',
      rejection: '\u274C',
      system: '\u2699\uFE0F'
    };
    return icons[type] || '\uD83D\uDD14';
  }

  async function fetchNotifications() {
    const params = new URLSearchParams({
      recipient: 'eq.' + currentUser,
      order: 'created_at.desc',
      limit: '30'
    });
    try {
      const res = await fetch(NOTIF_API + '?' + params.toString(), { headers });
      if (!res.ok) return [];
      return await res.json();
    } catch(e) {
      console.error('[notification-bell] Fetch error:', e);
      return [];
    }
  }

  async function markAsRead(id) {
    await fetch(NOTIF_API + '?id=eq.' + id, {
      method: 'PATCH',
      headers: { ...headers, 'Prefer': 'return=minimal' },
      body: JSON.stringify({ is_read: true })
    });
  }

  async function markAllRead() {
    await fetch(NOTIF_API + '?recipient=eq.' + currentUser + '&is_read=eq.false', {
      method: 'PATCH',
      headers: { ...headers, 'Prefer': 'return=minimal' },
      body: JSON.stringify({ is_read: true })
    });
    loadNotifications();
  }

  async function loadNotifications() {
    const notifications = await fetchNotifications();
    const unreadCount = notifications.filter(n => !n.is_read).length;

    // Update badge
    const badge = document.getElementById('crm-notif-count');
    if (unreadCount > 0) {
      badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
      badge.classList.remove('hidden');
    } else {
      badge.classList.add('hidden');
    }

    // Render dropdown
    let html = `
      <div class="crm-notif-header">
        <span>Notifications</span>
        ${unreadCount > 0 ? '<button class="crm-notif-mark-all" id="crm-notif-mark-all">Mark all read</button>' : ''}
      </div>
    `;

    if (notifications.length === 0) {
      html += '<div class="crm-notif-empty">No notifications yet.</div>';
    } else {
      for (const n of notifications) {
        html += `
          <div class="crm-notif-item ${n.is_read ? '' : 'unread'}" data-id="${n.id}" data-link="${escapeHtml(n.link || '')}">
            <div class="crm-notif-item-title">
              <span class="crm-notif-type-icon">${typeIcon(n.notification_type)}</span>
              ${escapeHtml(n.title)}
            </div>
            ${n.body ? '<div class="crm-notif-item-body">' + escapeHtml(n.body) + '</div>' : ''}
            <div class="crm-notif-item-time">${timeAgo(n.created_at)}</div>
          </div>
        `;
      }
    }

    dropdown.innerHTML = html;

    // Bind mark all
    const markAllBtn = document.getElementById('crm-notif-mark-all');
    if (markAllBtn) {
      markAllBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        markAllRead();
      });
    }

    // Bind item clicks
    dropdown.querySelectorAll('.crm-notif-item').forEach(item => {
      item.addEventListener('click', async function() {
        const id = this.getAttribute('data-id');
        const link = this.getAttribute('data-link');
        await markAsRead(id);
        this.classList.remove('unread');
        // Update count
        const remaining = dropdown.querySelectorAll('.crm-notif-item.unread').length;
        const badge = document.getElementById('crm-notif-count');
        if (remaining > 0) {
          badge.textContent = remaining;
          badge.classList.remove('hidden');
        } else {
          badge.classList.add('hidden');
        }
        if (link) window.open(link, '_blank');
      });
    });
  }

  // Initial load (just the count)
  async function initBadge() {
    const params = new URLSearchParams({
      recipient: 'eq.' + currentUser,
      is_read: 'eq.false',
      select: 'id'
    });
    try {
      const res = await fetch(NOTIF_API + '?' + params.toString(), { headers });
      if (!res.ok) return;
      const data = await res.json();
      const badge = document.getElementById('crm-notif-count');
      if (data.length > 0) {
        badge.textContent = data.length > 99 ? '99+' : data.length;
        badge.classList.remove('hidden');
      }
    } catch(e) {
      // silent
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBadge);
  } else {
    initBadge();
  }

  // Poll every 60 seconds for new notifications
  setInterval(initBadge, 60000);
})();
