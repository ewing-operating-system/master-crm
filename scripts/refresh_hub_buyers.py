#!/usr/bin/env python3
"""
refresh_hub_buyers.py — Populate & sync buyer hub pages for any deal.

WHAT IT DOES:
  1. Pulls all engagement_buyers for a given proposal_id from Supabase
  2. Fills null buyer_city / buyer_state from the HQ_MAP lookup below
  3. Fills null fit_score from confidence (HIGH=8, MEDIUM=6, LOW=4)
  4. Writes updates back to Supabase
  5. Regenerates the <seller>-hub.html buyer table with all rows linked

WHEN TO RUN:
  - After importing new buyers into engagement_buyers
  - After generating new buyer 1-pager HTML files
  - Any time the hub page shows blank city or score

USAGE:
  python3 scripts/refresh_hub_buyers.py --proposal <proposal_id> --hub <hub_file> --prefix <slug_prefix>

EXAMPLES:
  python3 scripts/refresh_hub_buyers.py \
    --proposal 63642786-ab16-456d-bac3-8f277f36ddc5 \
    --hub public/hrcom-ltd-hub.html \
    --prefix hr-com-ltd

  python3 scripts/refresh_hub_buyers.py \
    --proposal deed565b-156f-4d92-aa51-254802c71c6a \
    --hub public/springer-floor-hub.html \
    --prefix springer-floor

ADD NEW COMPANIES:
  Add entries to HQ_MAP below. Key = exact buyer_company_name in Supabase.
"""

import argparse
import os
import re
import sys
import requests

# ── Config ──────────────────────────────────────────────────────────────────

SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://dwrnfpjcvydhmhnvyzov.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
    '.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ'
    '.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s'
)

PUBLIC_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'master-crm-web', 'public')

CONFIDENCE_TO_SCORE = {'HIGH': 8, 'MEDIUM': 6, 'LOW': 4}

# ── HQ Map ───────────────────────────────────────────────────────────────────
# Key = exact buyer_company_name in Supabase, Value = (city, state/country)
# Add new buyers here as they're imported. Never remove old entries.

HQ_MAP = {
    # HR.com buyers
    'Paychex':                              ('Rochester', 'NY'),
    'Workday':                              ('Pleasanton', 'CA'),
    'SAP SuccessFactors':                   ('Newtown Square', 'PA'),
    'ADP':                                  ('Roseland', 'NJ'),
    'Thoma Bravo':                          ('San Francisco', 'CA'),
    'Randstad / Randstad Digital':          ('Atlanta', 'GA'),
    'HG Capital':                           ('London', 'UK'),
    'Deel':                                 ('San Francisco', 'CA'),
    'Lighthouse Research & Advisory':       ('Birmingham', 'AL'),
    'Drake Star Partners (Advisory Lead)':  ('New York', 'NY'),
    'Wolters Kluwer':                       ('Alphen aan den Rijn', 'Netherlands'),
    'EY':                                   ('New York', 'NY'),
    'Hellman & Friedman':                   ('San Francisco', 'CA'),
    'SHRM':                                 ('Alexandria', 'VA'),
    'IBM':                                  ('Armonk', 'NY'),
    'Microsoft':                            ('Redmond', 'WA'),
    'KKR':                                  ('New York', 'NY'),
    'Google':                               ('Mountain View', 'CA'),
    'Remote':                               ('San Francisco', 'CA'),
    'Francisco Partners':                   ('San Francisco', 'CA'),
    'Silver Lake':                          ('Menlo Park', 'CA'),
    'Greenhouse':                           ('New York', 'NY'),
    'Thrive Capital':                       ('New York', 'NY'),
    'OpenAI':                               ('San Francisco', 'CA'),
    'Amazon (AWS)':                         ('Seattle', 'WA'),
    'Industry Dive':                        ('Washington', 'DC'),
    'Shopify':                              ('Ottawa', 'Canada'),
    'Vista Equity Partners':                ('Austin', 'TX'),
    'Paylocity':                            ('Schaumburg', 'IL'),
    'Ceridian (Dayforce)':                  ('Minneapolis', 'MN'),
    'Clearlake Capital':                    ('Santa Monica', 'CA'),
    'Gainsight':                            ('San Francisco', 'CA'),
    'Insight Partners':                     ('New York', 'NY'),
    'Informa':                              ('London', 'UK'),
    'ServiceNow':                           ('Santa Clara', 'CA'),
    'Bevy':                                 ('Palo Alto', 'CA'),
    'Salesforce':                           ('San Francisco', 'CA'),
    'Alight':                               ('Lincolnshire', 'IL'),
    'Cohere':                               ('Toronto', 'Canada'),
    'G2':                                   ('Chicago', 'IL'),
    'HubSpot':                              ('Cambridge', 'MA'),
    'Lattice':                              ('San Francisco', 'CA'),
    'Manpower (ManpowerGroup)':             ('Milwaukee', 'WI'),
    'Accenture':                            ('Dublin', 'Ireland'),
    'Rippling':                             ('San Francisco', 'CA'),
    'PWC':                                  ('New York', 'NY'),
    'TechTarget':                           ('Newton', 'MA'),
    'Thomson Reuters':                      ('Toronto', 'Canada'),
    'ATD':                                  ('Alexandria', 'VA'),
    'Norwest Venture Partners':             ('Palo Alto', 'CA'),
    'Culture Amp':                          ('San Francisco', 'CA'),
    'BambooHR':                             ('Lindon', 'UT'),
    'Oracle HCM':                           ('Austin', 'TX'),
    'Paycom':                               ('Oklahoma City', 'OK'),
    'Dotdash Meredith':                     ('New York', 'NY'),
    'UKG (Ultimate Kronos)':                ('Weston', 'FL'),
    'ZoomInfo':                             ('Vancouver', 'WA'),
    'RELX (Reed Elsevier)':                 ('London', 'UK'),
    'WorldatWork':                          ('Scottsdale', 'AZ'),
    'Indeed':                               ('Austin', 'TX'),
    'Mighty Networks':                      ('Palo Alto', 'CA'),
    'Spark Capital':                        ('San Francisco', 'CA'),
    'MyPeople.ai':                          ('San Francisco', 'CA'),
    'Khoros':                               ('Austin', 'TX'),
    'Anthropic':                            ('San Francisco', 'CA'),
    'Deloitte':                             ('New York', 'NY'),
    'Benchmark':                            ('San Francisco', 'CA'),
    'Wiley':                                ('Hoboken', 'NJ'),
    # Springer Floor buyers
    'Roark Capital / ServiceMaster Brands': ('Atlanta', 'GA'),
    'The Riverside Company / milliCare':    ('New York', 'NY'),
    'Rainier Partners':                     ('Seattle', 'WA'),
    'NEXClean':                             ('West Chester', 'PA'),
    'ABM Industries':                       ('New York', 'NY'),
    'Cintas Corporation':                   ('Cincinnati', 'OH'),
    'COIT Cleaning and Restoration':        ('Burlingame', 'CA'),
    'Stanley Steemer':                      ('Dublin', 'OH'),
    'Marsden Holding':                      ('St. Paul', 'MN'),
    'Pritchard Industries':                 ('New York', 'NY'),
    'Premium Service Brands':              ('Charlottesville', 'VA'),
    'Harvard Maintenance':                  ('New York', 'NY'),
    'Paul Davis Restoration':               ('Jacksonville', 'FL'),
    'OpenWorks':                            ('Phoenix', 'AZ'),
    'Kellermeyer Bergensons Services (KBS)':('Oceanside', 'CA'),
    'Anago Cleaning Systems':               ('Fort Lauderdale', 'FL'),
    'BluSky Restoration':                   ('Englewood', 'CO'),
    'Belfor Holdings':                      ('Birmingham', 'MI'),
    'Incline Equity Partners':              ('Pittsburgh', 'PA'),
    'Jan-Pro Cleaning & Disinfecting':      ('Atlanta', 'GA'),
    'Kinderhook Industries':                ('New York', 'NY'),
    'Seacoast Capital':                     ('Boston', 'MA'),
    'FirstService Brands':                  ('Toronto', 'Canada'),
    'Aftermath Services (Kinderhook)':      ('Aurora', 'IL'),
    'Centre Partners':                      ('New York', 'NY'),
    'ATI Restoration':                      ('Irvine', 'CA'),
    'Vanguard Cleaning Systems':            ('Campbell', 'CA'),
    'Compass Group / Eurest Services':      ('Charlotte', 'NC'),
    'Coverall North America':               ('Deerfield Beach', 'FL'),
    'Restoration 1':                        ('Waco', 'TX'),
    'Summit Park':                          ('Cleveland', 'OH'),
    'H.I.G. Capital':                       ('Miami', 'FL'),
    'Rainbow International (Neighborly/KKR)':('Waco', 'TX'),
    'Building Services of America (BSA)':   ('Overland Park', 'KS'),
    'GI Partners':                          ('San Francisco', 'CA'),
    # Net new — CII Advisors PDF March 2026
    'Guardian Restoration Partners':        ('Denver', 'CO'),
    'Zerorez':                              ('Pleasant Grove', 'UT'),
    'QuickDry Pro':                         ('Gardner', 'KS'),
    'Chem-Dry International':               ('Nashville', 'TN'),
    'Oxi Fresh Carpet Cleaning':            ('Lakewood', 'CO'),
    "Heaven's Best Carpet Cleaning":        ('Rexburg', 'ID'),
    'SERVPRO Industries':                   ('Gallatin', 'TN'),
    'PuroClean':                            ('Tamarac', 'FL'),
    'City Wide Facility Solutions':         ('Lenexa', 'KS'),
    'Corvus Janitorial':                    ('Chicago', 'IL'),
    'Heartland Home Services':              ('Macomb', 'MI'),
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def supabase_headers():
    return {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal',
    }

def slugify(s):
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')[:80]

# ── Step 1: Backfill Supabase ────────────────────────────────────────────────

def backfill_supabase(proposal_id):
    r = requests.get(
        f'{SUPABASE_URL}/rest/v1/engagement_buyers'
        f'?proposal_id=eq.{proposal_id}'
        '&or=(buyer_city.is.null,fit_score.is.null)'
        '&select=id,buyer_company_name,confidence,fit_score,buyer_city,buyer_state'
        '&limit=200',
        headers=supabase_headers()
    )
    buyers = r.json()
    print(f'Buyers needing backfill: {len(buyers)}')

    updated = missing = 0
    for b in buyers:
        name = b['buyer_company_name']
        hq = HQ_MAP.get(name)
        conf = b.get('confidence') or 'HIGH'
        score = CONFIDENCE_TO_SCORE.get(conf, 6)

        patch = {}
        if not b.get('fit_score'):
            patch['fit_score'] = score
        if not b.get('buyer_city'):
            if hq:
                patch['buyer_city'], patch['buyer_state'] = hq
            else:
                print(f'  NO HQ for "{name}" — add to HQ_MAP in this script')
                missing += 1

        if patch:
            r2 = requests.patch(
                f'{SUPABASE_URL}/rest/v1/engagement_buyers?id=eq.{b["id"]}',
                headers=supabase_headers(),
                json=patch
            )
            if r2.status_code in (200, 204):
                updated += 1
            else:
                print(f'  PATCH FAILED {name}: {r2.status_code} {r2.text[:80]}')

    print(f'Updated: {updated} | Missing HQ: {missing}')
    return missing

# ── Step 2: Regenerate hub buyer table ───────────────────────────────────────

def regenerate_hub(proposal_id, hub_file, slug_prefix):
    full_hub = hub_file if os.path.isabs(hub_file) else os.path.join(
        os.path.dirname(__file__), '..', hub_file
    )
    pub_dir = os.path.dirname(full_hub)

    r = requests.get(
        f'{SUPABASE_URL}/rest/v1/engagement_buyers'
        f'?proposal_id=eq.{proposal_id}'
        '&select=buyer_company_name,buyer_type,buyer_city,buyer_state,fit_score,status'
        '&order=fit_score.desc.nullslast&limit=200',
        headers=supabase_headers()
    )
    buyers = r.json()

    rows = []
    for b in buyers:
        name = b['buyer_company_name']
        slug = f'{slug_prefix}_{slugify(name)}.html'
        has_file = os.path.exists(os.path.join(pub_dir, slug))
        city  = b.get('buyer_city') or ''
        state = b.get('buyer_state') or ''
        loc   = ', '.join(p for p in [city, state] if p) or '—'
        fit   = b.get('fit_score') if b.get('fit_score') is not None else '—'
        btype  = b.get('buyer_type') or '—'
        status = b.get('status') or 'researched'
        name_cell = f'<a href="{slug}">{name}</a>' if has_file else name
        rows.append(
            f'        <tr>\n'
            f'            <td>{name_cell}</td>\n'
            f'            <td>{btype}</td>\n'
            f'            <td>{loc}</td>\n'
            f'            <td>{fit}</td>\n'
            f'            <td><span class="badge {"green" if has_file else "orange"}" style="font-size:10px">{"✓ Ready" if has_file else "Pending"}</span></td>\n'
            f'            <td><span class="badge gray" style="font-size:10px">{status}</span></td>\n'
            f'        </tr>'
        )

    with open(full_hub) as f:
        html = f.read()

    pattern = re.compile(
        r'(<tr><th>Company</th><th>Type</th>.*?</th></tr>).*?(</table>)',
        re.DOTALL
    )
    new_html = pattern.sub(r'\1\n' + '\n'.join(rows) + r'\n        \2', html)

    if new_html == html:
        print('WARNING: buyer table pattern not matched — hub not updated')
        return False

    with open(full_hub, 'w') as f:
        f.write(new_html)

    linked = sum(1 for r in rows if '<a href' in r)
    print(f'Hub updated: {len(rows)} rows, {linked} linked')
    return True

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Refresh hub buyer table')
    parser.add_argument('--proposal', required=True, help='proposal_id UUID')
    parser.add_argument('--hub',      required=True, help='Path to hub HTML file')
    parser.add_argument('--prefix',   required=True, help='Slug prefix e.g. hr-com-ltd')
    args = parser.parse_args()

    print(f'\n=== refresh_hub_buyers: {args.prefix} ===')
    missing = backfill_supabase(args.proposal)
    regenerate_hub(args.proposal, args.hub, args.prefix)

    if missing:
        print(f'\nACTION NEEDED: {missing} buyers have no HQ. Add them to HQ_MAP in this script.')
        sys.exit(1)

if __name__ == '__main__':
    main()
