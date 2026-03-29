"""
Supabase client for master-crm — entity-aware.
Every write MUST include an entity tag. Every read CAN filter by entity.
"""

import json, os, urllib.request, ssl

ctx = ssl.create_default_context()

URL = os.environ.get("SUPABASE_URL", "https://dwrnfpjcvydhmhnvyzov.supabase.co")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s")

# Tables that do NOT require entity column
ENTITY_EXEMPT = {"do_not_call", "audits", "harvests", "stories", "analysis", "skills_registry",
                  "campaigns", "forge_boomerang_targets", "and_events", "and_event_targets",
                  "and_investor_profiles", "nc_owner_profiles", "ru_placements"}

def _headers(prefer=None):
    h = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    if prefer:
        h["Prefer"] = prefer
    return h

def get(table, params="", entity=None):
    """Read from a table. Optionally filter by entity."""
    filter_str = params
    if entity:
        filter_str += f"&entity=eq.{entity}" if params else f"entity=eq.{entity}"
    url = f"{URL}/rest/v1/{table}?{filter_str}"
    req = urllib.request.Request(url, headers=_headers())
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read())

def insert(table, data, entity=None):
    """Insert a row. Entity is required for transactional tables."""
    if table not in ENTITY_EXEMPT:
        if entity:
            data["entity"] = entity
        if "entity" not in data:
            raise ValueError(f"Entity required for table '{table}'. Pass entity= or include 'entity' in data.")

    payload = json.dumps(data, default=str).encode()
    req = urllib.request.Request(
        f"{URL}/rest/v1/{table}",
        data=payload,
        headers=_headers("return=representation"),
        method="POST"
    )
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read())

def upsert(table, data, entity=None):
    """Upsert a row. Entity is required for transactional tables."""
    if table not in ENTITY_EXEMPT:
        if entity:
            data["entity"] = entity
        if "entity" not in data:
            raise ValueError(f"Entity required for table '{table}'.")

    payload = json.dumps(data, default=str).encode()
    req = urllib.request.Request(
        f"{URL}/rest/v1/{table}",
        data=payload,
        headers=_headers("return=representation,resolution=merge-duplicates"),
        method="POST"
    )
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read())

def insert_batch(table, rows, entity=None):
    """Insert multiple rows. Entity is enforced."""
    if table not in ENTITY_EXEMPT and entity:
        for row in rows:
            row["entity"] = entity
    if table not in ENTITY_EXEMPT:
        for row in rows:
            if "entity" not in row:
                raise ValueError(f"Entity required for every row in '{table}'.")

    payload = json.dumps(rows, default=str).encode()
    req = urllib.request.Request(
        f"{URL}/rest/v1/{table}",
        data=payload,
        headers=_headers("return=minimal"),
        method="POST"
    )
    resp = urllib.request.urlopen(req, context=ctx)
    return len(rows)

def dnc_check(phone=None, company_name=None):
    """Check if a phone or company is on the universal DNC list."""
    if phone:
        results = get("do_not_call", f"phone=eq.{phone}")
        if results:
            return True
    if company_name:
        results = get("do_not_call", f"company_name=eq.{company_name}")
        if results and any(r.get("block_company") for r in results):
            return True
    return False

def get_campaign(campaign_id):
    """Load a campaign record by ID (e.g., 'NC-SELL-LETTER')."""
    results = get("campaigns", f"campaign_id=eq.{campaign_id}")
    if not results:
        raise ValueError(f"Campaign '{campaign_id}' not found.")
    return results[0]
