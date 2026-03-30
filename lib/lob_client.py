#!/usr/bin/env python3
"""
Lob API client for Master CRM — sends physical letters via Lob.com
Uses urllib (no external deps). Reads LOB_API_KEY from env.
"""

import json, os, urllib.request, urllib.parse, ssl, base64, hashlib, hmac
from datetime import datetime

LOB_API_KEY = os.environ.get("LOB_API_KEY", "")
LOB_WEBHOOK_SECRET = os.environ.get("LOB_WEBHOOK_SECRET", "")
LOB_BASE = "https://api.lob.com/v1"

def _auth_header():
    """Lob uses HTTP Basic Auth with API key as username."""
    creds = base64.b64encode(f"{LOB_API_KEY}:".encode()).decode()
    return {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}

def _request(method, path, data=None):
    """Make a request to Lob API."""
    url = f"{LOB_BASE}/{path}"
    headers = _auth_header()
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    ctx = ssl.create_default_context()
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read())

def send_letter(to_address, from_address, html_content, description="", metadata=None):
    """
    Send a physical letter via Lob.

    to_address: dict with keys: name, address_line1, address_city, address_state, address_zip
    from_address: dict with same keys
    html_content: HTML string for letter content
    description: optional description
    metadata: optional dict of metadata (max 20 keys)

    Returns: Lob letter object with id, url, tracking info
    """
    payload = {
        "to": to_address,
        "from": from_address,
        "file": html_content,
        "color": False,
        "description": description,
    }
    if metadata:
        payload["metadata"] = metadata
    return _request("POST", "letters", payload)

def get_letter(letter_id):
    """Get letter status and tracking info."""
    return _request("GET", f"letters/{letter_id}")

def cancel_letter(letter_id):
    """Cancel a letter (only if not yet in production)."""
    return _request("DELETE", f"letters/{letter_id}")

def list_letters(limit=10, offset=0):
    """List recent letters."""
    return _request("GET", f"letters?limit={limit}&offset={offset}")

def verify_webhook(payload_body, signature, timestamp):
    """Verify a Lob webhook signature."""
    if not LOB_WEBHOOK_SECRET:
        return False
    signed_payload = f"{timestamp}.{payload_body}"
    expected = hmac.new(LOB_WEBHOOK_SECRET.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

def create_address(name, line1, city, state, zip_code, company=None):
    """Create a reusable address in Lob."""
    payload = {
        "name": name,
        "address_line1": line1,
        "address_city": city,
        "address_state": state,
        "address_zip": zip_code,
    }
    if company:
        payload["company"] = company
    return _request("POST", "addresses", payload)

# Next Chapter return address
NC_RETURN_ADDRESS = {
    "name": "Next Chapter Advisory",
    "address_line1": os.environ.get("NC_RETURN_ADDRESS_LINE1", ""),
    "address_city": os.environ.get("NC_RETURN_ADDRESS_CITY", ""),
    "address_state": os.environ.get("NC_RETURN_ADDRESS_STATE", ""),
    "address_zip": os.environ.get("NC_RETURN_ADDRESS_ZIP", ""),
}
