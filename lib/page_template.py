#!/usr/bin/env python3
"""
Master Page Template System
============================
Wraps any page content in a professional, responsive template with consistent
styling, navigation, sidebar, comment/version widgets, and deal-side framing.

Used by company_hub.py and any future page generators.

Feature #39 additions:
  - PAGE_TYPES   : layout configs for every typed page
  - ENTITY_THEMES: color palettes for nc, and_capital, revsup
  - render_page() : typed, entity-aware, view-mode-aware renderer
  - wrap_page()  : unchanged for backward compatibility
"""

import re
from datetime import datetime


# ============================================================
# PAGE TYPES — layout config for each typed page
# ============================================================

PAGE_TYPES = {
    'buyer_dossier': {
        'css_class':     'page-dossier',
        'meta_type':     'buyer_dossier',
        'title_suffix':  'Buyer Dossier',
        'sidebar':       True,
        'supabase_table': 'dossier_final',
        'key_fields': [
            'company_name', 'hq_city', 'hq_state', 'revenue', 'ebitda',
            'employees', 'founded_year', 'industry', 'fit_score',
            'buyer_acquisition_history', 'contact_name', 'contact_title',
            'contact_email', 'contact_phone',
        ],
    },
    'target_profile': {
        'css_class':     'page-target',
        'meta_type':     'target_profile',
        'title_suffix':  'Target Profile',
        'sidebar':       True,
        'supabase_table': 'companies',
        'key_fields': [
            'company_name', 'hq_city', 'hq_state', 'revenue', 'ebitda',
            'employees', 'industry', 'vertical', 'fit_score',
            'owner_name', 'owner_email', 'owner_phone',
        ],
    },
    'hub': {
        'css_class':     'page-hub',
        'meta_type':     'hub',
        'title_suffix':  'Company Hub',
        'sidebar':       True,
        'supabase_table': 'companies',
        'key_fields': [
            'company_name', 'revenue', 'ebitda', 'employees',
            'deal_side', 'stage', 'assigned_to',
        ],
    },
    'proposal': {
        'css_class':     'page-proposal',
        'meta_type':     'proposal',
        'title_suffix':  'Advisory Proposal',
        'sidebar':       False,
        'supabase_table': 'proposals',
        'key_fields': [
            'company_name', 'deal_side', 'fee_structure', 'retainer',
            'success_fee_pct', 'engagement_start', 'advisor_name',
        ],
    },
    'meeting': {
        'css_class':     'page-meeting',
        'meta_type':     'meeting',
        'title_suffix':  'Meeting Notes',
        'sidebar':       False,
        'supabase_table': 'meetings',
        'key_fields': [
            'meeting_date', 'company_name', 'attendees', 'summary',
            'action_items', 'next_steps', 'transcript_url',
        ],
    },
    'activity_feed': {
        'css_class':     'page-activity',
        'meta_type':     'activity_feed',
        'title_suffix':  'Activity Feed',
        'sidebar':       True,
        'supabase_table': 'activities',
        'key_fields': [
            'activity_type', 'company_name', 'contact_name',
            'notes', 'created_at', 'created_by',
        ],
    },
    'dashboard': {
        'css_class':     'page-dashboard',
        'meta_type':     'dashboard',
        'title_suffix':  'Dashboard',
        'sidebar':       False,
        'supabase_table': None,
        'key_fields': [],
    },
}


# ============================================================
# ENTITY THEMES — color palettes
# ============================================================

ENTITY_THEMES = {
    'nc': {
        'css_class':   'theme-nc',
        'name':        'Next Chapter',
        'primary':     '#58a6ff',
        'secondary':   '#1f6feb',
        'background':  '#0d1117',
        'surface':     '#161b22',
        'badge_bg':    '#1f6feb',
        'badge_text':  '#f0f6fc',
        'gradient':    'linear-gradient(135deg, #161b22 0%, #0d1117 50%, #161b22 100%)',
    },
    'next_chapter': {  # alias used in existing code
        'css_class':   'theme-nc',
        'name':        'Next Chapter',
        'primary':     '#58a6ff',
        'secondary':   '#1f6feb',
        'background':  '#0d1117',
        'surface':     '#161b22',
        'badge_bg':    '#1f6feb',
        'badge_text':  '#f0f6fc',
        'gradient':    'linear-gradient(135deg, #161b22 0%, #0d1117 50%, #161b22 100%)',
    },
    'and_capital': {
        'css_class':   'theme-and',
        'name':        'AND Capital',
        'primary':     '#d4af37',
        'secondary':   '#b8922a',
        'background':  '#0e0e1a',
        'surface':     '#1a1a2e',
        'badge_bg':    '#d4af37',
        'badge_text':  '#0e0e1a',
        'gradient':    'linear-gradient(135deg, #1a1a2e 0%, #0e0e1a 50%, #1a1a2e 100%)',
    },
    'and': {  # short alias
        'css_class':   'theme-and',
        'name':        'AND Capital',
        'primary':     '#d4af37',
        'secondary':   '#b8922a',
        'background':  '#0e0e1a',
        'surface':     '#1a1a2e',
        'badge_bg':    '#d4af37',
        'badge_text':  '#0e0e1a',
        'gradient':    'linear-gradient(135deg, #1a1a2e 0%, #0e0e1a 50%, #1a1a2e 100%)',
    },
    'revsup': {
        'css_class':   'theme-ru',
        'name':        'RevsUp',
        'primary':     '#dc3545',
        'secondary':   '#a71d2a',
        'background':  '#120505',
        'surface':     '#1e0808',
        'badge_bg':    '#dc3545',
        'badge_text':  '#f0f6fc',
        'gradient':    'linear-gradient(135deg, #2d0a0a 0%, #120505 50%, #2d0a0a 100%)',
    },
    'ru': {  # short alias
        'css_class':   'theme-ru',
        'name':        'RevsUp',
        'primary':     '#dc3545',
        'secondary':   '#a71d2a',
        'background':  '#120505',
        'surface':     '#1e0808',
        'badge_bg':    '#dc3545',
        'badge_text':  '#f0f6fc',
        'gradient':    'linear-gradient(135deg, #2d0a0a 0%, #120505 50%, #2d0a0a 100%)',
    },
    'default': {
        'css_class':   'theme-default',
        'name':        '',
        'primary':     '#58a6ff',
        'secondary':   '#1f6feb',
        'background':  '#0d1117',
        'surface':     '#161b22',
        'badge_bg':    '#30363d',
        'badge_text':  '#f0f6fc',
        'gradient':    'linear-gradient(135deg, #161b22 0%, #0d1117 50%, #161b22 100%)',
    },
}


# ============================================================
# VIEW MODE LABELS
# ============================================================

VIEW_MODES = {
    'internal': {'label': 'INTERNAL VIEW — admin only',  'css_class': 'view-internal'},
    'client':   {'label': 'CLIENT VIEW — editable draft', 'css_class': 'view-client'},
    'buyer':    {'label': 'BUYER VIEW — polished package', 'css_class': 'view-buyer'},
}


# ============================================================
# render_page() — typed, entity-aware, view-mode-aware
# ============================================================

def render_page(page_type, entity, data, view_mode='internal',
                nav_links=None, show_comment_widget=True,
                show_version_widget=True):
    """
    Render a typed CRM page using master-theme.css design system.

    Args:
        page_type (str): One of the PAGE_TYPES keys
                         (e.g. 'hub', 'buyer_dossier', 'proposal', 'meeting',
                          'activity_feed', 'dashboard', 'target_profile')
        entity (str)   : One of the ENTITY_THEMES keys
                         (e.g. 'nc', 'next_chapter', 'and_capital', 'revsup', 'default')
        data (dict)    : Page data. Expected keys vary by page_type (see PAGE_TYPES).
                         At minimum should contain 'title' and optionally 'subtitle',
                         'body_html', 'company_name'.
        view_mode (str): 'internal' | 'client' | 'buyer'  (default: 'internal')
        nav_links (list): list of dicts with 'label', 'href', optional 'active'
        show_comment_widget (bool): include comment-widget.js
        show_version_widget (bool): include version-widget.js

    Returns:
        str: Complete HTML document
    """
    # Resolve type config
    type_cfg   = PAGE_TYPES.get(page_type, PAGE_TYPES['hub'])
    theme_cfg  = ENTITY_THEMES.get(entity, ENTITY_THEMES['default'])
    view_cfg   = VIEW_MODES.get(view_mode, VIEW_MODES['internal'])

    page_css   = type_cfg['css_class']
    entity_css = theme_cfg['css_class']
    view_css   = view_cfg['css_class']
    body_class = f"{entity_css} {page_css} {view_css}"

    title        = data.get('title', data.get('company_name', 'CRM Page'))
    subtitle     = data.get('subtitle', '')
    company_name = data.get('company_name', title)
    body_html    = data.get('body_html', '')

    # Deduce deal_side for framing (fall back to sell_side)
    deal_side    = data.get('deal_side', 'sell_side')
    framing      = get_page_framing(deal_side)

    sections     = _extract_sections(body_html)
    now          = datetime.now().strftime('%B %d, %Y %I:%M %p')

    # Build navigation
    nav_links = nav_links or []
    nav_html = ''
    for link in nav_links:
        active = ' class="active"' if link.get('active') else ''
        nav_html += f'<a href="{link["href"]}"{active}>{link["label"]}</a>\n'

    # Build sidebar (only for types that use it)
    sidebar_html = ''
    if type_cfg.get('sidebar', True) and sections:
        for s in sections:
            sidebar_html += f'<a href="#{s["id"]}" class="sidebar-link">{s["title"]}</a>\n'

    sidebar_block = ''
    if sidebar_html:
        sidebar_block = f'''
  <!-- SIDEBAR -->
  <div class="sidebar">
    <div class="sidebar-heading">Page Sections</div>
    {sidebar_html}
  </div>'''

    # Widget scripts
    widgets = ''
    if show_comment_widget:
        widgets += '<script src="/comment-widget.js"></script>\n'
    if show_version_widget:
        widgets += '<script src="/version-widget.js"></script>\n'

    # View mode banner
    view_banner = f'<div class="view-mode-bar">{view_cfg["label"]}</div>'

    # Entity badge text
    entity_label = theme_cfg['name'] or framing['badge_text']

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — {type_cfg['title_suffix']}</title>
<meta name="company-name" content="{company_name}">
<meta name="page-type" content="{type_cfg['meta_type']}">
<meta name="entity" content="{entity}">
<meta name="view-mode" content="{view_mode}">
<meta name="deal-side" content="{deal_side}">
<link rel="stylesheet" href="/master-theme.css">
<link rel="stylesheet" href="/print-theme.css" media="print">
</head>
<body class="{body_class}">

{view_banner}

<!-- HEADER -->
<div class="page-header">
  <div class="header-inner">
    <div class="header-left">
      <h1>{title}</h1>
      <div class="subtitle">{subtitle}</div>
    </div>
    <div class="header-right">
      <span class="deal-badge">{framing['badge_text']}</span>
    </div>
  </div>
</div>

<!-- NAVIGATION -->
<div class="top-nav">
  {nav_html}
</div>

<!-- LAYOUT -->
<div class="page-layout">
{sidebar_block}

  <!-- MAIN CONTENT -->
  <div class="main-content">
    {body_html}
  </div>

</div>

<!-- FOOTER -->
<div class="page-footer">
  <strong>{entity_label or 'Next Chapter M&A Advisory'}</strong> | {framing['deal_description']}<br>
  Generated {now} | {view_cfg['label']}
</div>

<!-- WIDGETS -->
{widgets}

</body>
</html>"""

    return html


def get_page_framing(deal_side):
    """Return labels and section names appropriate for buy vs sell side."""
    if deal_side == 'buy_side':
        return {
            'main_heading': 'Acquisition Target Search',
            'valuation_label': 'Target Valuation Assessment',
            'attack_label': 'Target Outreach Plan',
            'buyer_section': 'Acquisition Targets',
            'narrative_label': 'Why Sell to {company}',
            'fee_label': 'Advisory Fee (2-3% Success)',
            'badge_text': 'BUY SIDE',
            'badge_color': '#58a6ff',
            'deal_description': 'Buy-Side Engagement',
        }
    else:
        return {
            'main_heading': 'Sell-Side Advisory Assessment',
            'valuation_label': 'Your Estimated Value Range',
            'attack_label': 'Buyer Outreach Strategy',
            'buyer_section': 'Potential Acquirers',
            'narrative_label': 'Your Company Story',
            'fee_label': 'Advisory Fee (5-10% Success)',
            'badge_text': 'SELL SIDE',
            'badge_color': '#27ae60',
            'deal_description': 'Sell-Side Engagement',
        }


def _extract_sections(body_html):
    """Extract h2 section titles and their IDs from body HTML for sidebar nav."""
    sections = []
    pattern = re.compile(r'<h2[^>]*(?:id=["\']([^"\']*)["\'])?[^>]*>(.*?)</h2>', re.IGNORECASE | re.DOTALL)
    for match in pattern.finditer(body_html):
        section_id = match.group(1)
        title = re.sub(r'<[^>]+>', '', match.group(2)).strip()
        if not section_id:
            section_id = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        sections.append({'id': section_id, 'title': title})
    return sections


def wrap_page(title, subtitle, company_name, deal_side, nav_links, body_html,
              show_comment_widget=True, show_version_widget=True):
    """
    Wrap page content in the master template.

    Args:
        title: Page title (e.g. company name)
        subtitle: Subtitle line (e.g. "Andy Wieser | Maiden Rock, WI | Precast Concrete")
        company_name: Company name for meta tags
        deal_side: 'buy_side' or 'sell_side'
        nav_links: list of dicts with 'label', 'href', and optional 'active' keys
        body_html: The main content HTML to wrap
        show_comment_widget: Include comment widget script
        show_version_widget: Include version widget script

    Returns:
        Complete HTML string
    """
    framing = get_page_framing(deal_side)
    sections = _extract_sections(body_html)
    now = datetime.now().strftime('%B %d, %Y %I:%M %p')

    # Build navigation
    nav_html = ''
    for link in nav_links:
        active = ' class="active"' if link.get('active') else ''
        nav_html += f'<a href="{link["href"]}"{active}>{link["label"]}</a>\n'

    # Build sidebar
    sidebar_html = ''
    for s in sections:
        sidebar_html += f'<a href="#{s["id"]}" class="sidebar-link">{s["title"]}</a>\n'

    # Widget scripts
    widgets = ''
    if show_comment_widget:
        widgets += '<script src="/comment-widget.js"></script>\n'
    if show_version_widget:
        widgets += '<script src="/version-widget.js"></script>\n'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Company Hub</title>
<meta name="company-name" content="{company_name}">
<meta name="page-type" content="hub">
<meta name="deal-side" content="{deal_side}">
<style>
  /* === RESET === */
  *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}

  /* === BASE === */
  body {{
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: #0d1117;
    color: #c9d1d9;
    line-height: 1.6;
    min-height: 100vh;
  }}

  /* === HEADER === */
  .page-header {{
    background: linear-gradient(135deg, #161b22 0%, #0d1117 50%, #161b22 100%);
    border-bottom: 1px solid #30363d;
    padding: 28px 32px 20px;
    position: sticky;
    top: 0;
    z-index: 100;
  }}
  .header-inner {{
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }}
  .header-left h1 {{
    font-size: 26px;
    font-weight: 700;
    color: #f0f6fc;
    letter-spacing: -0.3px;
  }}
  .header-left .subtitle {{
    font-size: 14px;
    color: #8b949e;
    margin-top: 4px;
  }}
  .header-right {{
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
  }}
  .deal-badge {{
    display: inline-block;
    padding: 5px 16px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #f0f6fc;
    background: {framing['badge_color']};
    text-transform: uppercase;
  }}
  .badge {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    color: #f0f6fc;
  }}
  .badge.green {{ background: #27ae60; }}
  .badge.orange {{ background: #f39c12; color: #1a1a2e; }}
  .badge.blue {{ background: #1f6feb; }}
  .badge.red {{ background: #e74c3c; }}
  .badge.gray {{ background: #30363d; }}

  /* === NAVIGATION === */
  .top-nav {{
    background: #161b22;
    border-bottom: 1px solid #30363d;
    padding: 0 32px;
    display: flex;
    gap: 0;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }}
  .top-nav a {{
    color: #8b949e;
    text-decoration: none;
    padding: 12px 18px;
    font-size: 13px;
    font-weight: 500;
    white-space: nowrap;
    border-bottom: 2px solid transparent;
    transition: all 0.15s ease;
  }}
  .top-nav a:hover {{ color: #c9d1d9; border-bottom-color: #30363d; }}
  .top-nav a.active {{ color: #58a6ff; border-bottom-color: #58a6ff; }}

  /* === LAYOUT === */
  .page-layout {{
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    gap: 0;
    min-height: calc(100vh - 160px);
  }}

  /* === SIDEBAR === */
  .sidebar {{
    width: 220px;
    flex-shrink: 0;
    background: #0d1117;
    border-right: 1px solid #21262d;
    padding: 20px 0;
    position: sticky;
    top: 90px;
    height: fit-content;
    max-height: calc(100vh - 120px);
    overflow-y: auto;
  }}
  .sidebar-heading {{
    font-size: 11px;
    font-weight: 600;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 8px 20px;
    margin-bottom: 4px;
  }}
  .sidebar-link {{
    display: block;
    padding: 7px 20px;
    color: #8b949e;
    text-decoration: none;
    font-size: 13px;
    border-left: 2px solid transparent;
    transition: all 0.15s ease;
  }}
  .sidebar-link:hover {{
    color: #c9d1d9;
    background: #161b22;
    border-left-color: #30363d;
  }}
  .sidebar-link:active, .sidebar-link.active {{
    color: #58a6ff;
    border-left-color: #58a6ff;
    background: #161b22;
  }}

  /* === MAIN CONTENT === */
  .main-content {{
    flex: 1;
    padding: 24px 32px;
    min-width: 0;
  }}

  /* === CARDS === */
  .card {{
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
  }}
  .card h2 {{
    font-size: 16px;
    font-weight: 600;
    color: #f0f6fc;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid #21262d;
  }}
  .card p {{ margin-bottom: 10px; }}

  /* === GRIDS === */
  .grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .grid3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }}
  .grid4 {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 16px; }}

  /* === STAT BOXES === */
  .stat {{
    text-align: center;
    padding: 18px 12px;
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 8px;
  }}
  .stat .num {{
    font-size: 30px;
    font-weight: 700;
    color: #f0f6fc;
    line-height: 1.1;
  }}
  .stat .label {{
    font-size: 12px;
    color: #8b949e;
    margin-top: 4px;
  }}

  /* === TABLES === */
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }}
  th {{
    text-align: left;
    padding: 10px 12px;
    background: #0d1117;
    font-weight: 600;
    color: #8b949e;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid #30363d;
  }}
  td {{
    padding: 10px 12px;
    border-bottom: 1px solid #21262d;
    color: #c9d1d9;
  }}
  tr:hover td {{ background: #1c2128; }}

  /* === LINKS === */
  a {{ color: #58a6ff; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}

  /* === LISTS === */
  ul, ol {{ padding-left: 22px; }}
  li {{ margin: 5px 0; }}

  /* === SCRIPT/NARRATIVE BOXES === */
  .narrative-box {{
    background: #0d1117;
    border: 1px solid #21262d;
    border-left: 3px solid #58a6ff;
    padding: 18px 20px;
    border-radius: 6px;
    margin: 12px 0;
    line-height: 1.7;
    white-space: pre-wrap;
    font-size: 14px;
  }}
  .script-box {{
    background: #0d1117;
    border: 1px solid #21262d;
    padding: 16px;
    border-radius: 8px;
    margin: 10px 0;
    white-space: pre-wrap;
    font-size: 13px;
    line-height: 1.6;
  }}
  .script-label {{
    font-weight: 600;
    color: #f0f6fc;
    margin-bottom: 6px;
    font-size: 13px;
  }}

  /* === HIGHLIGHT CARD (for narrative) === */
  .highlight-card {{
    background: linear-gradient(135deg, #161b22, #1c2128);
    border: 1px solid #58a6ff;
    border-radius: 10px;
    padding: 24px;
    margin-bottom: 20px;
  }}
  .highlight-card h2 {{
    color: #58a6ff;
    border-bottom-color: #58a6ff40;
  }}

  /* === FOOTER === */
  .page-footer {{
    text-align: center;
    padding: 24px 32px;
    color: #484f58;
    font-size: 12px;
    border-top: 1px solid #21262d;
    margin-top: 20px;
  }}
  .page-footer strong {{ color: #8b949e; }}

  /* === RESPONSIVE === */
  @media (max-width: 900px) {{
    .sidebar {{ display: none; }}
    .page-layout {{ display: block; }}
    .main-content {{ padding: 16px; }}
    .grid2, .grid3, .grid4 {{ grid-template-columns: 1fr; }}
    .header-inner {{ flex-direction: column; gap: 10px; }}
    .top-nav {{ padding: 0 12px; }}
    .page-header {{ padding: 16px; }}
  }}

  /* === PRINT === */
  @media print {{
    body {{ background: white; color: #1a1a2e; }}
    .page-header {{ background: white; border-bottom: 2px solid #1a1a2e; position: static; }}
    .header-left h1 {{ color: #1a1a2e; }}
    .header-left .subtitle {{ color: #555; }}
    .top-nav {{ display: none; }}
    .sidebar {{ display: none; }}
    .page-layout {{ display: block; }}
    .main-content {{ padding: 0; }}
    .card {{ background: white; border: 1px solid #ddd; box-shadow: none; page-break-inside: avoid; }}
    .card h2 {{ color: #1a1a2e; border-bottom-color: #ddd; }}
    .stat {{ background: #f8f9fa; border-color: #ddd; }}
    .stat .num {{ color: #1a1a2e; }}
    .narrative-box {{ background: #f8f9fa; border-color: #ddd; border-left-color: #3498db; }}
    .highlight-card {{ background: #f8f9fa; border-color: #3498db; }}
    .script-box {{ background: #f8f9fa; border-color: #ddd; }}
    td {{ color: #1a1a2e; }}
    th {{ background: #f0f2f5; color: #555; }}
    .page-footer {{ color: #999; }}
    a {{ color: #1a5276; }}
    .deal-badge {{ print-color-adjust: exact; -webkit-print-color-adjust: exact; }}
    .badge {{ print-color-adjust: exact; -webkit-print-color-adjust: exact; }}
  }}
</style>
</head>
<body>

<!-- HEADER -->
<div class="page-header">
  <div class="header-inner">
    <div class="header-left">
      <h1>{title}</h1>
      <div class="subtitle">{subtitle}</div>
    </div>
    <div class="header-right">
      <span class="deal-badge">{framing['badge_text']}</span>
    </div>
  </div>
</div>

<!-- NAVIGATION -->
<div class="top-nav">
  {nav_html}
</div>

<!-- LAYOUT -->
<div class="page-layout">

  <!-- SIDEBAR -->
  <div class="sidebar">
    <div class="sidebar-heading">Page Sections</div>
    {sidebar_html}
  </div>

  <!-- MAIN CONTENT -->
  <div class="main-content">
    {body_html}
  </div>

</div>

<!-- FOOTER -->
<div class="page-footer">
  <strong>Next Chapter M&A Advisory</strong> | {framing['deal_description']}<br>
  Generated {now} | INTERNAL — Admin View
</div>

<!-- WIDGETS -->
{widgets}

</body>
</html>"""

    return html
