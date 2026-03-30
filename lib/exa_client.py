"""
Exa Search Client — uses curl subprocess (urllib is blocked by Exa's WAF).
"""

import subprocess, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

EXA_KEY = "fd8eb73b-d966-4f8b-8699-0ce357dffeea"

def search(query, num_results=5, max_chars=3000):
    """Search Exa. Returns list of results."""
    try:
        from lib.tool_health import report_success, report_failure
    except:
        report_success = lambda x: None
        report_failure = lambda *a, **kw: None

    payload = json.dumps({
        "query": query,
        "num_results": num_results,
        "type": "auto",
        "contents": {"text": {"max_characters": max_chars}}
    })

    try:
        result = subprocess.run([
            "curl", "-s", "-X", "POST", "https://api.exa.ai/search",
            "-H", f"x-api-key: {EXA_KEY}",
            "-H", "Content-Type: application/json",
            "-d", payload
        ], capture_output=True, text=True, timeout=30)

        data = json.loads(result.stdout)

        if "results" in data:
            report_success("exa")
            return data.get("results", []), data.get("costDollars", {}).get("total", 0)
        else:
            error = data.get("error", data.get("message", "unknown"))
            report_failure("exa", "api_error", str(error), query)
            return [], 0
    except Exception as e:
        report_failure("exa", "exception", str(e), query)
        return [], 0


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "test"
    results, cost = search(query, 3)
    print(f"Results: {len(results)}, Cost: ${cost:.3f}")
    for r in results:
        print(f"  {r.get('title', '')[:80]}")
