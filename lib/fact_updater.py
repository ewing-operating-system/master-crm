
def apply_fact_correction(comment_id):
    """Apply a fact correction from an accepted comment to the canonical data."""
    import psycopg2, json, re, os
    conn = psycopg2.connect(os.environ.get("DATABASE_URL", "postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:6543/postgres"))
    conn.autocommit = True
    cur = conn.cursor()
    
    cur.execute("""SELECT company_name, section_id, comment_text, user_response, revised_content, commenter
                   FROM page_comments WHERE id = %s""", (str(comment_id),))
    row = cur.fetchone()
    if not row:
        conn.close()
        return
    
    company, section, text, response, revised, commenter = row
    
    # Extract numbers from the comment
    numbers = re.findall(r'\$([\d,.]+[MmKk]?)', text + ' ' + (response or ''))
    
    # Update proposals table (canonical source per Q9)
    if section == 'valuation' and numbers:
        # Try to parse revenue
        for num_str in numbers:
            try:
                multiplier = 1
                clean = num_str.replace(',', '')
                if clean.upper().endswith('M'):
                    multiplier = 1000000
                    clean = clean[:-1]
                elif clean.upper().endswith('K'):
                    multiplier = 1000
                    clean = clean[:-1]
                value = float(clean) * multiplier
                
                if value > 100000:  # Likely revenue
                    # Store old value
                    cur.execute("""SELECT estimated_revenue FROM proposals WHERE company_name ILIKE %s""", (f'%{company}%',))
                    old = cur.fetchone()
                    old_val = old[0] if old else None
                    
                    # Update
                    cur.execute("""UPDATE proposals SET estimated_revenue = %s WHERE company_name ILIKE %s""",
                                (str(value), f'%{company}%'))
                    
                    # Log to human_corrections
                    cur.execute("""UPDATE companies SET human_corrections = COALESCE(human_corrections, '[]'::jsonb) || %s::jsonb
                                   WHERE company_name ILIKE %s""",
                                (json.dumps([{"field": "estimated_revenue", "old": str(old_val), "new": str(value),
                                             "source": commenter, "date": __import__("time").strftime("%Y-%m-%d")}]),
                                 f'%{company}%'))
                    
                    # Log to estimate_accuracy
                    if old_val:
                        try:
                            old_num = float(str(old_val).replace('$','').replace(',','').replace('M','000000').replace('K','000'))
                            delta = abs(value - old_num) / old_num * 100
                            cur.execute("""INSERT INTO estimate_accuracy (id, company_name, field_name, estimated_value, actual_value, delta_pct, corrected_by)
                                VALUES (gen_random_uuid(), %s, 'estimated_revenue', %s, %s, %s, %s)""",
                                (company, old_num, value, delta, commenter))
                        except:
                            pass
                    break
            except:
                continue
    
    # Mark page as stale
    cur.execute("""UPDATE page_versions SET is_stale = true, stale_reason = 'fact_correction_applied'
                   WHERE company_name ILIKE %s AND version = (
                       SELECT max(version) FROM page_versions WHERE company_name ILIKE %s AND page_type = 'proposal'
                   )""", (f'%{company}%', f'%{company}%'))
    
    # Log to Q&A
    import time
    qa_entry = f"""
### Comment [{time.strftime('%Y-%m-%d %H:%M')}]: {commenter} on {company} — {section}
**Comment:** {text}
**Type:** fact_correction
**Response:** {response or 'N/A'}
**Resolution:** Applied — {revised[:200] if revised else 'direct update'}
"""
    qa_path = 'data/MASTER-QA-LOG.md'
    with open(qa_path, 'a') as f:
        f.write(qa_entry)
    
    # Log to audits table
    cur.execute("""INSERT INTO audits (filename, content, tags) VALUES (%s, %s, %s)""",
        (f'comment_{comment_id}', json.dumps({"commenter": commenter, "company": company, 
         "section": section, "text": text, "response": response}),
         ['feedback', 'fact_correction', company]))
    
    conn.close()
    return True
