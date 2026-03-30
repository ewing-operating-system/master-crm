/**
 * Version History Slider Widget
 * Injects a version navigation bar at the top of any page stored in page_versions.
 * Works with Supabase REST API using the anon key (RLS allows public reads).
 *
 * Usage: Include this script on any page. It auto-detects company_name and page_type
 * from meta tags or the page URL/title.
 */
(function () {
  'use strict';

  const SUPABASE_URL = 'https://dwrnfpjcvydhmhnvyzov.supabase.co';
  const ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3NTcyOTAsImV4cCI6MjA5MDMzMzI5MH0.z0Gu1TWdGPcdptB5W7efnYMmxBbvD353ExG99ftQivY';

  // ── Detect page identity from meta tags ──
  function getPageIdentity() {
    const metaCompany = document.querySelector('meta[name="company-name"]');
    const metaType = document.querySelector('meta[name="page-type"]');
    const metaVersion = document.querySelector('meta[name="page-version"]');

    let companyName = metaCompany ? metaCompany.content : null;
    let pageType = metaType ? metaType.content : null;
    let currentVersion = metaVersion ? parseInt(metaVersion.content, 10) : null;

    // Fallback: parse from title "Company Name — Type"
    if (!companyName) {
      const title = document.title || '';
      const match = title.match(/^(.+?)\s*[—\-|]\s*/);
      if (match) companyName = match[1].trim();
    }

    // Fallback: guess page type from URL or title
    if (!pageType) {
      const url = window.location.pathname.toLowerCase();
      const title = (document.title || '').toLowerCase();
      if (url.includes('hub') || title.includes('hub')) pageType = 'hub';
      else if (url.includes('data-room') || url.includes('dataroom') || title.includes('data room')) pageType = 'data_room';
      else if (url.includes('meeting') || title.includes('meeting')) pageType = 'meeting';
      else if (url.includes('proposal') || title.includes('advisory') || title.includes('proposal')) pageType = 'proposal';
      else if (url.includes('research') || title.includes('research')) pageType = 'research';
      else pageType = 'proposal';
    }

    return { companyName, pageType, currentVersion };
  }

  // ── Supabase REST helper ──
  async function supabaseGet(params) {
    const qs = new URLSearchParams(params).toString();
    const resp = await fetch(`${SUPABASE_URL}/rest/v1/page_versions?${qs}`, {
      headers: {
        'apikey': ANON_KEY,
        'Authorization': `Bearer ${ANON_KEY}`,
      },
    });
    if (!resp.ok) throw new Error(`Supabase error ${resp.status}`);
    return resp.json();
  }

  // ── Format date ──
  function fmtDate(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', {
      year: 'numeric', month: 'long', day: 'numeric',
    }) + ' ' + d.toLocaleTimeString('en-US', {
      hour: 'numeric', minute: '2-digit', hour12: true,
    });
  }

  // ── Build the version bar ──
  function createBar() {
    const bar = document.createElement('div');
    bar.id = 'version-bar';
    bar.style.cssText = [
      'position:fixed', 'top:0', 'left:0', 'right:0', 'z-index:99999',
      'padding:8px 20px', 'font-family:system-ui,sans-serif', 'font-size:14px',
      'display:flex', 'align-items:center', 'justify-content:space-between',
      'box-shadow:0 2px 8px rgba(0,0,0,0.15)', 'transition:background 0.3s',
    ].join(';');
    bar.innerHTML = `
      <div style="display:flex;align-items:center;gap:12px">
        <button id="vb-prev" style="background:none;border:1px solid rgba(255,255,255,0.5);color:inherit;border-radius:4px;padding:2px 10px;cursor:pointer;font-size:16px" title="Previous version">&#9664;</button>
        <span id="vb-label" style="font-weight:600"></span>
        <button id="vb-next" style="background:none;border:1px solid rgba(255,255,255,0.5);color:inherit;border-radius:4px;padding:2px 10px;cursor:pointer;font-size:16px" title="Next version">&#9654;</button>
      </div>
      <div id="vb-status" style="display:flex;align-items:center;gap:10px"></div>
    `;
    return bar;
  }

  // ── Main controller ──
  async function init() {
    const identity = getPageIdentity();
    if (!identity.companyName) return; // cannot detect — skip

    const companyName = identity.companyName;
    const pageType = identity.pageType;

    // Fetch version metadata (not full html) to know total count
    let versions;
    try {
      versions = await supabaseGet({
        'company_name': `eq.${companyName}`,
        'page_type': `eq.${pageType}`,
        'select': 'version,created_at,is_stale',
        'order': 'version.asc',
      });
    } catch (e) {
      console.warn('[version-widget] Could not fetch versions:', e);
      return;
    }

    if (!versions || versions.length === 0) return; // no versions stored

    const totalVersions = versions.length;
    const maxVersion = versions[totalVersions - 1].version;
    let currentVer = identity.currentVersion || maxVersion;

    // Store original page HTML so we can restore without a fetch
    const originalHTML = document.documentElement.innerHTML;

    // Push body down to make room for bar
    document.body.style.marginTop = '48px';

    const bar = createBar();
    document.body.prepend(bar);

    const btnPrev = document.getElementById('vb-prev');
    const btnNext = document.getElementById('vb-next');
    const label = document.getElementById('vb-label');
    const status = document.getElementById('vb-status');

    function render() {
      const vMeta = versions.find(v => v.version === currentVer);
      const dateStr = vMeta ? fmtDate(vMeta.created_at) : '';
      const isCurrent = currentVer === maxVersion;

      label.textContent = `Version ${currentVer} of ${maxVersion}`;

      btnPrev.disabled = currentVer <= 1;
      btnNext.disabled = currentVer >= maxVersion;
      btnPrev.style.opacity = btnPrev.disabled ? '0.3' : '1';
      btnNext.style.opacity = btnNext.disabled ? '0.3' : '1';

      if (isCurrent) {
        bar.style.background = '#1e8449';
        bar.style.color = '#fff';
        status.innerHTML = `<span>&#10003; Current Version (Version ${currentVer}) &mdash; ${dateStr}</span>`;
      } else {
        bar.style.background = '#c0392b';
        bar.style.color = '#fff';
        status.innerHTML = `
          <span>&#9888;&#65039; You are viewing Version ${currentVer} of ${maxVersion} &mdash; NOT the current version. Generated ${dateStr}</span>
          <button id="vb-load-current" style="background:#fff;color:#c0392b;border:none;border-radius:4px;padding:4px 12px;cursor:pointer;font-weight:600;font-size:13px;margin-left:8px">Load Current Version &rarr;</button>
        `;
        document.getElementById('vb-load-current').addEventListener('click', () => {
          currentVer = maxVersion;
          loadVersion(currentVer);
        });
      }
    }

    async function loadVersion(ver) {
      if (ver === maxVersion && originalHTML) {
        // Restore original page, then re-inject widget
        const parser = new DOMParser();
        const doc = parser.parseFromString(originalHTML, 'text/html');
        // Replace body content only (keep our bar)
        const bodyContent = doc.body.innerHTML;
        // Remove the bar temporarily, replace body, re-add bar
        bar.remove();
        document.body.innerHTML = bodyContent;
        document.body.style.marginTop = '48px';
        document.body.prepend(bar);
        render();
        return;
      }

      try {
        const data = await supabaseGet({
          'company_name': `eq.${companyName}`,
          'page_type': `eq.${pageType}`,
          'version': `eq.${ver}`,
          'select': 'html_content,version,created_at',
        });

        if (data && data.length > 0) {
          const html = data[0].html_content;
          // Parse the fetched HTML and replace body content
          const parser = new DOMParser();
          const doc = parser.parseFromString(html, 'text/html');
          bar.remove();
          document.body.innerHTML = doc.body.innerHTML;
          document.body.style.marginTop = '48px';
          document.body.prepend(bar);
          // Re-bind the bar event listeners (they are still attached to the same nodes)
          render();
        }
      } catch (e) {
        console.error('[version-widget] Error loading version:', e);
        status.innerHTML = '<span style="color:#ffe0e0">Error loading version. Try again.</span>';
      }
    }

    btnPrev.addEventListener('click', () => {
      if (currentVer > 1) {
        currentVer--;
        loadVersion(currentVer);
      }
    });

    btnNext.addEventListener('click', () => {
      if (currentVer < maxVersion) {
        currentVer++;
        loadVersion(currentVer);
      }
    });

    // Initial render
    render();
  }

  // Run when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
