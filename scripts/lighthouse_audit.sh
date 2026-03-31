#!/usr/bin/env bash
# lighthouse_audit.sh — Mobile readiness audit for client-facing pages
# Usage:
#   ./lighthouse_audit.sh                        # audit default URL list
#   ./lighthouse_audit.sh https://example.com    # audit a single URL
#   ./lighthouse_audit.sh -f urls.txt            # audit a file of URLs (one per line)
#
# Checks per page:
#   [VIEWPORT]   presence of <meta name="viewport"> — required to prevent mobile zoom
#   [MOBILE-CSS] presence of mobile-fixes.css link
#   [FONT-SIZE]  body font-size >= 14px (scans inline styles/css for obvious violations)
#   [PAGE-SIZE]  total download size via curl (warn if > 500 KB)
#   [TTFB]       time-to-first-byte via curl (warn if > 1.5 s)
#   [REQUESTS]   estimated request count (counts <script>, <link>, <img> tags in HTML)
#   [TOUCH-TGT]  presence of .touch-target or min-height:44 in the page
#
# Output: human-readable report with PASS / WARN / FAIL per check

set -euo pipefail

# ── Color codes ─────────────────────────────────────────────────────────────
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

PASS="${GREEN}PASS${RESET}"
WARN="${YELLOW}WARN${RESET}"
FAIL="${RED}FAIL${RESET}"

# ── Default URL list ─────────────────────────────────────────────────────────
# Change BASE_URL to match your deployment (local dev or production)
BASE_URL="${BASE_URL:-http://localhost:3000}"

DEFAULT_URLS=(
    # Interactive proposals (6)
    "${BASE_URL}/interactive-air-control.html"
    "${BASE_URL}/interactive-aquascience.html"
    "${BASE_URL}/interactive-design-precast.html"
    "${BASE_URL}/interactive-hrcom-ltd.html"
    "${BASE_URL}/interactive-springer-floor.html"
    "${BASE_URL}/interactive-wieser-concrete.html"

    # Data rooms (6)
    "${BASE_URL}/dataroom-air-control.html"
    "${BASE_URL}/dataroom-aquascience.html"
    "${BASE_URL}/dataroom-design-precast-and-pipe-inc.html"
    "${BASE_URL}/dataroom-hrcom-ltd.html"
    "${BASE_URL}/dataroom-springer-floor.html"
    "${BASE_URL}/dataroom-wieser-concrete-products-inc.html"

    # Hubs (6)
    "${BASE_URL}/air-control-hub.html"
    "${BASE_URL}/aquascience-hub.html"
    "${BASE_URL}/design-precast-and-pipe-inc-hub.html"
    "${BASE_URL}/hrcom-ltd-hub.html"
    "${BASE_URL}/springer-floor-hub.html"
    "${BASE_URL}/wieser-concrete-products-inc-hub.html"
)

# ── Argument parsing ─────────────────────────────────────────────────────────
URLS=()

if [[ $# -eq 0 ]]; then
    URLS=("${DEFAULT_URLS[@]}")
elif [[ $# -eq 2 && "$1" == "-f" ]]; then
    FILE="$2"
    if [[ ! -f "$FILE" ]]; then
        echo "Error: file not found: $FILE" >&2
        exit 1
    fi
    while IFS= read -r line; do
        [[ -z "$line" || "$line" == \#* ]] && continue
        URLS+=("$line")
    done < "$FILE"
else
    # Treat all positional args as URLs
    URLS=("$@")
fi

if [[ ${#URLS[@]} -eq 0 ]]; then
    echo "No URLs to audit." >&2
    exit 1
fi

# ── Thresholds ────────────────────────────────────────────────────────────────
SIZE_WARN_KB=500        # warn above 500 KB
SIZE_FAIL_KB=1500       # fail above 1.5 MB
TTFB_WARN_S="1.500"     # warn above 1.5 s
TTFB_FAIL_S="3.000"     # fail above 3.0 s
REQUEST_WARN=40         # warn above 40 tagged resources

# ── Helpers ──────────────────────────────────────────────────────────────────
bc_compare() {
    # Returns 0 (true) if $1 > $2 using awk (avoids bc dependency)
    awk "BEGIN { exit !($1 > $2) }"
}

pad_right() {
    # Usage: pad_right "string" width
    printf "%-${2}s" "$1"
}

# ── Audit a single URL ────────────────────────────────────────────────────────
audit_url() {
    local url="$1"
    local page_name
    page_name=$(basename "$url")

    echo ""
    echo -e "${BOLD}${CYAN}── ${page_name}${RESET}"
    echo -e "   URL: ${url}"

    # Fetch page with curl, capturing timing and body
    local tmpfile
    tmpfile=$(mktemp)
    local http_code ttfb size_bytes

    if ! curl -s -o "$tmpfile" \
              -w "%{http_code} %{time_starttransfer} %{size_download}" \
              --max-time 15 \
              --compressed \
              "$url" > /tmp/_curl_stats_$$.txt 2>&1; then
        echo -e "   ${FAIL} Could not reach URL (curl error)"
        rm -f "$tmpfile" /tmp/_curl_stats_$$.txt
        return
    fi

    read -r http_code ttfb size_bytes < /tmp/_curl_stats_$$.txt
    rm -f /tmp/_curl_stats_$$.txt

    if [[ "$http_code" != "200" ]]; then
        echo -e "   ${FAIL} HTTP ${http_code} — page not reachable (is the server running?)"
        rm -f "$tmpfile"
        return
    fi

    local html
    html=$(cat "$tmpfile")
    rm -f "$tmpfile"

    # ── [VIEWPORT] ───────────────────────────────────────────
    local vp_status
    if echo "$html" | grep -qi 'name="viewport"'; then
        vp_status="$PASS"
    else
        vp_status="$FAIL  — missing <meta name=\"viewport\">"
    fi
    echo -e "   [VIEWPORT]   ${vp_status}"

    # ── [MOBILE-CSS] ─────────────────────────────────────────
    local css_status
    if echo "$html" | grep -q 'mobile-fixes\.css'; then
        css_status="$PASS"
    else
        css_status="$FAIL  — mobile-fixes.css not linked"
    fi
    echo -e "   [MOBILE-CSS] ${css_status}"

    # ── [FONT-SIZE] — scan for obvious sub-14px body declarations ──
    local font_status="$PASS"
    # Look for inline body font-size below 14px (e.g. font-size:12px or font-size: 12px)
    if echo "$html" | grep -qiE 'body\s*\{[^}]*font-size\s*:\s*(([0-9]|1[0-3])px)'; then
        font_status="$WARN  — body font-size appears < 14px in inline styles"
    fi
    echo -e "   [FONT-SIZE]  ${font_status}"

    # ── [PAGE-SIZE] ──────────────────────────────────────────
    local size_kb
    size_kb=$(awk "BEGIN { printf \"%.0f\", $size_bytes / 1024 }")
    local size_status
    if (( size_kb > SIZE_FAIL_KB )); then
        size_status="${FAIL}  — ${size_kb} KB (>${SIZE_FAIL_KB} KB limit)"
    elif (( size_kb > SIZE_WARN_KB )); then
        size_status="${WARN}  — ${size_kb} KB (>${SIZE_WARN_KB} KB threshold)"
    else
        size_status="${PASS}  — ${size_kb} KB"
    fi
    echo -e "   [PAGE-SIZE]  ${size_status}"

    # ── [TTFB] ───────────────────────────────────────────────
    local ttfb_status
    if bc_compare "$ttfb" "$TTFB_FAIL_S" 2>/dev/null; then
        ttfb_status="${FAIL}  — ${ttfb}s (>${TTFB_FAIL_S}s)"
    elif bc_compare "$ttfb" "$TTFB_WARN_S" 2>/dev/null; then
        ttfb_status="${WARN}  — ${ttfb}s (>${TTFB_WARN_S}s)"
    else
        ttfb_status="${PASS}  — ${ttfb}s"
    fi
    echo -e "   [TTFB]       ${ttfb_status}"

    # ── [REQUESTS] — count <script>, <link rel="stylesheet">, <img> ──
    local req_count
    req_count=$(echo "$html" | grep -ciE '<(script|link[^>]+rel="stylesheet"|img)[^>]*(src|href)=' || true)
    local req_status
    if (( req_count > REQUEST_WARN )); then
        req_status="${WARN}  — ~${req_count} resource tags (consider bundling)"
    else
        req_status="${PASS}  — ~${req_count} resource tags"
    fi
    echo -e "   [REQUESTS]   ${req_status}"

    # ── [TOUCH-TGT] — check for touch-target class or 44px min-height ──
    local touch_status
    if echo "$html" | grep -qE 'touch-target|min-height:\s*44px|min-height:44px'; then
        touch_status="$PASS"
    else
        touch_status="${WARN}  — no explicit touch-target found; verify manually"
    fi
    echo -e "   [TOUCH-TGT]  ${touch_status}"
}

# ── Main ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}=================================================${RESET}"
echo -e "${BOLD}  Next Chapter Mobile Readiness Audit${RESET}"
echo -e "${BOLD}  $(date '+%Y-%m-%d %H:%M:%S')${RESET}"
echo -e "${BOLD}  Base URL: ${BASE_URL}${RESET}"
echo -e "${BOLD}  Pages to audit: ${#URLS[@]}${RESET}"
echo -e "${BOLD}=================================================${RESET}"

# Track summary counts
total=0
pass_count=0
fail_count=0
warn_count=0

for url in "${URLS[@]}"; do
    audit_url "$url"
    total=$((total + 1))
done

echo ""
echo -e "${BOLD}=================================================${RESET}"
echo -e "${BOLD}  Audit complete — ${total} pages checked${RESET}"
echo -e "${BOLD}  Legend: ${PASS} all checks green  |  ${WARN} review recommended  |  ${FAIL} fix required${RESET}"
echo -e "${BOLD}=================================================${RESET}"
echo ""
