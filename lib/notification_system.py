
def notify_on_comment(comment_id):
    """Send notification to the other person when a comment is posted."""
    import psycopg2, json, subprocess, os
    conn = psycopg2.connect('postgresql://postgres:MakeMoneyNow1!@db.dwrnfpjcvydhmhnvyzov.supabase.co:6543/postgres')
    conn.autocommit = True
    cur = conn.cursor()
    
    cur.execute("""SELECT commenter, company_name, section_id, comment_text, comment_type
                   FROM page_comments WHERE id = %s""", (str(comment_id),))
    row = cur.fetchone()
    if not row:
        conn.close()
        return
    
    commenter, company, section, text, ctype = row
    
    # Notify the OTHER person
    recipient = 'ewing@chapter.guide' if commenter == 'mark' else 'mark@chapter.guide'
    other_name = 'Ewing' if commenter == 'mark' else 'Mark'
    
    title = f"{commenter.title()} commented on {company} — {section}"
    message = f"{ctype}: {text[:200]}"
    link = f"https://master-crm-web-eight.vercel.app/interactive-{company.lower().replace(' ', '-')}.html"
    
    cur.execute("""INSERT INTO notifications (recipient, notification_type, title, message, link, company_name, metadata)
        VALUES (%s, 'comment', %s, %s, %s, %s, %s)""",
        (recipient, title, message, link, company,
         json.dumps({'comment_id': str(comment_id), 'commenter': commenter, 'section': section})))
    
    # Try iMessage
    try:
        bridge = os.path.expanduser('~/.imessage-bridge/imessage-bridge.sh')
        if os.path.exists(bridge):
            imsg = f"[Argus] {commenter.title()} commented on {company}/{section}: {text[:100]}"
            subprocess.run([bridge, imsg], capture_output=True, timeout=15)
    except:
        pass
    
    conn.close()
