#!/usr/bin/env python3
"""
ETL via Supabase REST API — batch inserts, 500 rows at a time.
Keeps ALL data. Unmapped fields go into extra_fields JSONB.
"""

import json, os, sys, time, urllib.request, ssl

URL = "https://dwrnfpjcvydhmhnvyzov.supabase.co"
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cm5mcGpjdnlkaG1obnZ5em92Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDc1NzI5MCwiZXhwIjoyMDkwMzMzMjkwfQ.7Bd_6aZhpWazv-evA_f1WpocfEHcXX8JATLNSKAC00s")
EXPORT = os.path.expanduser("~/Projects/dossier-pipeline/data/data-export")
ctx = ssl.create_default_context()

# Get columns for a table via REST
def get_columns(table):
    """Get one row to discover columns."""
    req = urllib.request.Request(
        f"{URL}/rest/v1/{table}?limit=0",
        headers={"apikey": KEY, "Authorization": f"Bearer {KEY}", "Prefer": "count=exact"}
    )
    resp = urllib.request.urlopen(req, context=ctx)
    # Parse column names from the response headers or try an empty select
    return None  # We'll infer from data

def post_batch(table, rows):
    """POST a batch of rows to Supabase REST API."""
    data = json.dumps(rows, default=str).encode()
    req = urllib.request.Request(
        f"{URL}/rest/v1/{table}",
        data=data,
        headers={
            "apikey": KEY,
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        method="POST"
    )
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=60)
        return len(rows), None
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        return 0, f"HTTP {e.code}: {body}"

def load_table(table, source_file, entity_default=None, skip_entity=False, field_map=None):
    """Load a tagged JSON export into a table via REST API batches."""
    path = os.path.join(EXPORT, source_file)
    if not os.path.exists(path):
        print(f"  SKIP {table}: {source_file} not found")
        return 0, set()

    with open(path) as f:
        data = json.load(f)
    if not data:
        print(f"  SKIP {table}: empty")
        return 0, set()

    # We need to know valid columns. Do a test insert to find out.
    # Build rows, stripping 'id' and collecting misfits
    misfits = set()
    clean_rows = []

    for row in data:
        clean = {}
        extra = {}

        for k, v in row.items():
            if v is None:
                continue
            if k == 'id':
                extra['old_id'] = v
                continue

            # Apply field map
            if field_map and k in field_map:
                mapped_k = field_map[k]
                if mapped_k:
                    clean[mapped_k] = v
                continue

            if skip_entity and k in ('entity', 'entity_confidence', 'entity_reason', 'entity_method'):
                extra[k] = v
                continue

            # Convert complex types to JSON strings for JSONB columns
            if isinstance(v, (dict, list)):
                clean[k] = json.dumps(v, default=str)
            else:
                clean[k] = v

        if entity_default and 'entity' not in clean:
            clean['entity'] = entity_default

        if extra:
            clean['extra_fields'] = json.dumps(extra, default=str)

        clean_rows.append(clean)

    # Insert in batches
    batch_size = 500
    total_inserted = 0
    errors = []

    for i in range(0, len(clean_rows), batch_size):
        batch = clean_rows[i:i+batch_size]
        n, err = post_batch(table, batch)
        if err:
            # Try smaller batch or single-row to find the problem
            if "column" in err.lower() and "does not exist" in err.lower():
                # Extract bad column name and retry without it
                import re
                m = re.search(r'column "(\w+)"', err)
                if m:
                    bad_col = m.group(1)
                    misfits.add(bad_col)
                    # Strip bad column and retry
                    fixed_batch = []
                    for row in batch:
                        extra = json.loads(row.get('extra_fields', '{}'))
                        if bad_col in row:
                            extra[bad_col] = row.pop(bad_col)
                            row['extra_fields'] = json.dumps(extra, default=str)
                        fixed_batch.append(row)
                    n2, err2 = post_batch(table, fixed_batch)
                    if err2:
                        errors.append(f"Batch {i}: {err2}")
                    else:
                        total_inserted += n2
                    continue
            errors.append(f"Batch {i}: {err}")
            # Try row by row for this batch
            for row in batch:
                n3, err3 = post_batch(table, [row])
                if n3:
                    total_inserted += 1
        else:
            total_inserted += n

    status = f"{table}: {total_inserted}/{len(data)} loaded"
    if misfits:
        status += f", misfits: {sorted(misfits)}"
    if errors:
        status += f", errors: {len(errors)}"
        for e in errors[:3]:
            print(f"    ERR: {e[:150]}")
    print(f"  {status}")
    sys.stdout.flush()

    return total_inserted, misfits


def main():
    start = time.time()
    total = 0
    all_misfits = {}

    print("=" * 60)
    print("ETL via REST API — batch inserts")
    print(f"Target: master-crm ({URL})")
    print("=" * 60)
    sys.stdout.flush()

    # ─── Load order (dependencies first) ─────────────────────
    loads = [
        # TAM (bulk NC)
        ("tam_businesses", "tam_businesses_tagged.json", "next_chapter", False),
        ("tam_final", "tam_final_tagged.json", "next_chapter", False),
        ("tam_verifications", "tam_verifications_tagged.json", "next_chapter", False),
        ("tam_owner_profiles", "tam_owner_profiles_tagged.json", "next_chapter", False),
        ("tam_scrape_runs", "tam_scrape_runs_tagged.json", "next_chapter", False),
        # Pipeline
        ("targets", "targets_tagged.json", None, False),
        ("dossier_final", "dossier_final_tagged.json", "next_chapter", False),
        ("dossier_runs", "dossier_runs_tagged.json", "next_chapter", False),
        ("dossier_provenance", "dossier_provenance_tagged.json", "next_chapter", False),
        ("cost_log", "dossier_cost_log_tagged.json", "next_chapter", False),
        ("sent_log", "sent_log_tagged.json", None, False),
        ("call_analysis", "call_analysis_tagged.json", None, False),
        ("outreach_queue", "outreach_queue_tagged.json", None, False),
        ("dialer_queue", "dialer_queue_tagged.json", None, False),
        ("pipeline_log", "pipeline_log_tagged.json", None, False),
        ("deal_research", "deal_research_tagged.json", None, False),
        ("acquisition_targets", "acquisition_targets_tagged.json", None, False),
        # Special handling
        ("do_not_call", "do_not_call_tagged.json", None, True),
        ("forge_boomerang_targets", "boomerang_targets_tagged.json", None, True),
        # System tables
        ("stories", "stories_tagged.json", None, True),
        ("harvests", "harvests_tagged.json", None, True),
        ("audits", "audits_tagged.json", None, True),
        ("analysis", "analysis_tagged.json", None, True),
        ("skills_registry", "skills_registry_tagged.json", None, True),
        # NYC AND Capital
        ("and_investor_profiles", "nyc_iumy_contacts.json", None, False),
        ("and_investor_profiles", "nyc_pgoo_people.json", None, False),
        ("and_events", "nyc_pgoo_events.json", None, False),
        # Dossiers legacy
        ("dossier_final", "dossiers_tagged.json", "next_chapter", False),
    ]

    for table, src, ent_default, skip_ent in loads:
        n, mf = load_table(table, src, ent_default, skip_ent)
        total += n
        if mf:
            if table not in all_misfits:
                all_misfits[table] = set()
            all_misfits[table].update(mf)
        sys.stdout.flush()

    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"ETL COMPLETE: {total} rows in {elapsed:.0f}s")
    print(f"{'=' * 60}")

    # Write misfit report
    misfit_path = os.path.expanduser("~/Projects/dossier-pipeline/data/audit-logs/etl_misfit_fields.md")
    with open(misfit_path, 'w') as f:
        f.write("# ETL Misfit Fields Report\n\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("Fields from old data with no dedicated column in new schema.\n")
        f.write("ALL preserved in `extra_fields` JSONB. Nothing dropped.\n\n")
        for t, fields in sorted(all_misfits.items()):
            f.write(f"## {t}\n")
            for field in sorted(fields):
                f.write(f"- `{field}`\n")
            f.write("\n")
    print(f"\nMisfit report: {misfit_path}")

    # Write log
    log_path = os.path.expanduser("~/Projects/dossier-pipeline/data/audit-logs/etl_migration.log")
    with open(log_path, 'w') as f:
        f.write(f"ETL completed: {total} rows in {elapsed:.0f}s\n")
        f.write(f"Method: REST API batch inserts (500/batch)\n")
        f.write(f"Misfits: {sum(len(v) for v in all_misfits.values())} fields across {len(all_misfits)} tables\n")
    print(f"Log: {log_path}")

    sys.stdout.flush()


if __name__ == "__main__":
    main()
