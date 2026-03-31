#!/usr/bin/env python3
"""
build_final_13.py — Implementation Script for Final 13 Features
Master CRM Feature Roadmap: 57/70 → 70/70 (100%)

This script documents the implementation plan, dependencies, and execution
steps for each remaining feature. Run with --plan to see the plan,
or --build <feature_number> to execute a specific feature build.

Features are grouped by effort level:
  - MARK_DONE (4): Already built or superseded, just update roadmap
  - FINISH (3): Partially built, need completion
  - BUILD (6): Need full implementation

Usage:
  python3 scripts/build_final_13.py --plan          # Show full plan
  python3 scripts/build_final_13.py --build 44      # Build feature #44
  python3 scripts/build_final_13.py --build-all     # Build all remaining
  python3 scripts/build_final_13.py --status        # Check implementation status
"""

import json, os, subprocess, sys
from datetime import datetime
from pathlib import Path

MASTER_CRM = Path("/Users/clawdbot/projects/master-crm")
WEB_DIR = Path("/Users/clawdbot/projects/master-crm-web")

# ─────────────────────────────────────────────────────────────
# FEATURE DEFINITIONS
# ─────────────────────────────────────────────────────────────

FEATURES = {
    # ── GROUP 1: MARK AS DONE (already built or superseded) ──
    38: {
        "name": "Interactive Proposal Pages",
        "group": "MARK_DONE",
        "reason": "Superseded by #41 Buy-Side Interactive Proposals (built)",
        "superseded_by": 41,
        "verify_file": str(WEB_DIR / "public/interactive-buyer-proposal.html"),
        "action": "Update roadmap to mark as DONE (superseded by #41)",
    },
    43: {
        "name": "Source Attribution v1",
        "group": "MARK_DONE",
        "reason": "Superseded by #67 Source Attribution UI (built)",
        "superseded_by": 67,
        "verify_file": str(WEB_DIR / "public/source-attribution.html"),
        "action": "Update roadmap to mark as DONE (superseded by #67)",
    },
    47: {
        "name": "Conflict Resolution Modal",
        "group": "MARK_DONE",
        "reason": "Already fully built — conflict-resolver.js (387 lines)",
        "verify_file": str(MASTER_CRM / "lib/conflict-resolver.js"),
        "action": "Update roadmap to mark as DONE",
    },
    55: {
        "name": "Letter Mailing v2 (Handwrytten)",
        "group": "MARK_DONE",
        "reason": "Superseded by Lob integration (#63). Lob client fully built.",
        "superseded_by": 63,
        "verify_file": str(MASTER_CRM / "lib/lob_client.py"),
        "action": "Update roadmap to mark as DONE (superseded by #63 Lob)",
        "note": "DECISION PENDING: Add Handwrytten as premium tier ($8/letter) for high-value targets?",
    },

    # ── GROUP 2: FINISH (partially built, need completion) ──
    39: {
        "name": "Page Template System",
        "group": "FINISH",
        "description": "Master CSS framework with deal_side framing and professional design",
        "existing_code": [
            str(MASTER_CRM / "lib/page_template.py"),
        ],
        "what_exists": "Basic page_template.py wrapper for HTML generation with dark theme styling",
        "what_needs_building": [
            "Master CSS file (public/master-theme.css) with design tokens",
            "Deal-side framing: sell-side pages get blue accent, buy-side get green accent",
            "Typography system: heading hierarchy, body text, captions",
            "Component library: cards, tables, badges, progress bars, stat blocks",
            "Print stylesheet for letter/proposal pages",
            "Entity color coding: NC=#58a6ff, AND=#a855f7, RU=#27ae60",
        ],
        "output_files": [
            str(WEB_DIR / "public/master-theme.css"),
            str(WEB_DIR / "public/print-theme.css"),
            str(MASTER_CRM / "lib/page_template.py"),  # update
        ],
        "effort": "medium",
        "dependencies": [],
    },
    45: {
        "name": "D→C Feedback Conversation",
        "group": "FINISH",
        "description": "System asks clarifying questions before revising content based on user comments",
        "existing_code": [
            str(MASTER_CRM / "lib/comment_processor.py"),  # 620 lines
        ],
        "what_exists": "comment_processor.py with 5-status workflow, Claude CLI integration, template fallbacks",
        "what_needs_building": [
            "Activate the daemon (currently exists but not running)",
            "Wire up the clarifying question UI: when system generates Qs, show them in comment thread",
            "Add HTML widget: feedback-conversation.js that shows Q→A thread below each comment",
            "Connect response handling: user's answer triggers revision pipeline",
            "Dashboard page: public/feedback-conversations.html showing active threads",
        ],
        "output_files": [
            str(WEB_DIR / "public/feedback-conversation.js"),
            str(WEB_DIR / "public/feedback-conversations.html"),
            str(MASTER_CRM / "lib/comment_processor.py"),  # activate
        ],
        "effort": "medium",
        "dependencies": ["comment-widget.js must be on pages"],
    },
    46: {
        "name": "Research Method Learning",
        "group": "FINISH",
        "description": "Mark's corrections become new research techniques — system learns what works",
        "existing_code": [
            str(MASTER_CRM / "lib/research_transparency.py"),
        ],
        "what_exists": "research_methods table (method_code, success_rate, times_used), research_executions tracking, seed methods",
        "what_needs_building": [
            "Learning loop: when Mark corrects a fact, extract the correction pattern",
            "Pattern → new research_method entry with query_template",
            "Success rate updates: track which methods produce accepted vs rejected facts",
            "Dashboard: public/research-learning.html showing method performance",
            "Auto-prioritize high-success methods in future research runs",
        ],
        "output_files": [
            str(MASTER_CRM / "lib/research_learner.py"),
            str(WEB_DIR / "public/research-learning.html"),
        ],
        "effort": "medium",
        "dependencies": ["research_transparency.py", "comment_processor.py"],
    },

    # ── GROUP 3: BUILD (need full implementation) ──
    40: {
        "name": "Why Sell Narratives",
        "group": "BUILD",
        "description": "Standalone buy-side pitch narratives explaining why a target should sell NOW",
        "what_exists": "Letter engine has embedded 'Why NOW' sections; buyer 1-pagers have why_seller fields",
        "spec": {
            "purpose": "For each sell-side company, generate a compelling narrative about why this is the right time to consider a transaction",
            "narrative_components": [
                "Market timing: industry consolidation trends, valuation multiples",
                "Owner lifecycle: succession planning, retirement timeline, partner disputes",
                "Competitive pressure: PE roll-ups in their vertical, shrinking independents",
                "Value maximization: current EBITDA multiples vs historical, buyer demand",
                "Risk of waiting: market cycles, regulatory changes, key-person risk",
            ],
            "output_format": "Standalone HTML page per company + embeddable section for proposals",
            "data_sources": [
                "deal_research table (company data, financials)",
                "engagement_buyers (buyer interest signals)",
                "EBITDA levers (vertical benchmarks)",
                "Research templates (vertical-specific story hooks)",
            ],
        },
        "output_files": [
            str(MASTER_CRM / "lib/why_sell_engine.py"),
            str(WEB_DIR / "public/why-sell-narratives.html"),  # dashboard
        ],
        "effort": "medium",
        "dependencies": ["deal_research data", "ebitda_levers"],
    },
    44: {
        "name": "Diff View on Regeneration",
        "group": "BUILD",
        "description": "Show what changed when pages are auto-regenerated",
        "spec": {
            "purpose": "When auto_regen_daemon rebuilds a page, capture before/after diff and display it",
            "components": [
                "Pre-regen snapshot: save current HTML to page_versions before rebuilding",
                "Post-regen diff: compute text diff between old and new versions",
                "Diff storage: store in page_versions.diff_summary (JSON: added/removed/changed sections)",
                "UI: diff-viewer.html page showing side-by-side or inline diffs",
                "Integration: auto_regen_daemon.py calls diff before/after each rebuild",
            ],
            "diff_algorithm": "Section-level comparison (not line-by-line) — compare named sections",
            "notification": "If >20% of content changed, send Telegram alert with diff summary",
        },
        "output_files": [
            str(MASTER_CRM / "lib/diff_engine.py"),
            str(WEB_DIR / "public/diff-viewer.html"),
            str(MASTER_CRM / "scripts/auto_regen_daemon.py"),  # update
        ],
        "effort": "medium",
        "dependencies": ["auto_regen_daemon.py", "page_versions table"],
    },
    48: {
        "name": "Google Drive Template Pull",
        "group": "BUILD",
        "description": "Hourly sync of Mark's letter/proposal templates from Google Drive",
        "spec": {
            "purpose": "Mark edits letter templates in Google Drive. System pulls latest versions hourly and uses them for letter generation.",
            "components": [
                "Google Drive API client (read-only, using service account)",
                "Template registry: which Drive doc maps to which template_type",
                "Hourly cron: pull changed docs, convert to HTML, store in letter_templates table",
                "Version tracking: hash comparison to detect changes, keep last 5 versions",
                "Dashboard: public/drive-sync.html showing sync status and template versions",
            ],
            "decision_needed": "Which Google Drive folder? Need folder ID from Ewing.",
            "fallback": "If no Drive access, templates are managed directly in Supabase",
        },
        "output_files": [
            str(MASTER_CRM / "lib/drive_sync.py"),
            str(WEB_DIR / "public/drive-sync.html"),
        ],
        "effort": "medium",
        "dependencies": ["Google Drive API credentials", "Drive folder ID"],
    },
    49: {
        "name": "Guardrail Violation Log",
        "group": "BUILD",
        "description": "Dashboard showing when the system wants to break its own rules",
        "spec": {
            "purpose": "Log and display every time the system encounters a guardrail (DNC, entity routing, cost limits, etc.) and either blocked the action or flagged it for review",
            "violation_types": [
                "DNC bypass attempt (target on DNC list but system tried to contact)",
                "Entity misroute (wrong entity tag detected after classification)",
                "Cost overspend (API call would exceed budget threshold)",
                "Hallucination flag (LLM output failed fact-check)",
                "Trust threshold (action attempted below required trust level)",
                "Rate limit hit (Exa, Salesfinity, or Lob rate limits)",
                "Schema violation (missing required field like entity tag)",
            ],
            "storage": "guardrail_violations table: id, violation_type, entity, target_id, details, severity, action_taken, created_at",
            "severity_levels": "critical (blocked), warning (logged), info (noted)",
            "dashboard": "Real-time feed with severity filters, entity breakdown, trend chart",
        },
        "output_files": [
            str(MASTER_CRM / "lib/guardrail_logger.py"),
            str(WEB_DIR / "public/guardrail-violations.html"),
        ],
        "effort": "medium",
        "dependencies": [],
    },
    50: {
        "name": "While You Were Away Summary",
        "group": "BUILD",
        "description": "Changes since last login — activity feed for returning users",
        "spec": {
            "purpose": "When Ewing or Mark opens the dashboard, show a summary of everything that happened since their last visit",
            "components": [
                "Last-seen tracker: store last_login per user in user_sessions table",
                "Activity aggregator: query step_log, plays, page_versions, cost_ledger since last_login",
                "Summary generator: group by category (letters sent, calls made, pages rebuilt, costs incurred)",
                "Highlight detector: flag unusual activity (cost spike, DNC hit, high-urgency play)",
                "UI: modal overlay on dashboard.html OR dedicated away-summary.html page",
                "Dismiss: mark as read, don't show again until next away period",
            ],
            "categories": [
                "Letters: sent, approved, rejected",
                "Calls: loaded to Salesfinity, outcomes received",
                "Research: pages regenerated, new buyers added",
                "Plays: created, executed, completed",
                "Costs: total spend by service (Exa, Lob, Salesfinity)",
                "Alerts: guardrail violations, high-urgency signals",
            ],
        },
        "output_files": [
            str(MASTER_CRM / "lib/away_summary.py"),
            str(WEB_DIR / "public/away-summary.html"),
        ],
        "effort": "medium",
        "dependencies": ["step_log table", "cost_ledger table"],
    },
    71: {
        "name": "Shareable URL Polish",
        "group": "BUILD",
        "description": "Mobile-first optimization, sub-2s load, touch-optimized for client-facing pages",
        "spec": {
            "purpose": "Every shareable URL (proposals, data rooms, hub pages) must look perfect on mobile and load fast",
            "scope": [
                "Audit all client-facing pages on 375px viewport (iPhone SE)",
                "Fix layout breaks: grid→stack, font sizing, padding",
                "Touch targets: minimum 44x44px for all interactive elements",
                "Image optimization: lazy-load, srcset for retina, WebP where possible",
                "Font optimization: preload critical fonts, font-display:swap",
                "JS optimization: defer non-critical scripts, inline critical CSS",
                "Performance budget: <200KB total page weight, <2s LCP",
                "Test pages: interactive proposals, data rooms, company hubs, meeting pages",
            ],
            "priority_pages": [
                "interactive-*.html (6 proposal pages)",
                "dataroom-*.html (6 data room pages)",
                "*-hub.html (6 hub pages)",
                "meeting-*.html (meeting prep pages)",
            ],
            "tools": "Lighthouse CLI for automated scoring, manual iPhone testing",
        },
        "output_files": [
            str(WEB_DIR / "public/master-theme.css"),  # shared with #39
            str(WEB_DIR / "public/mobile-fixes.css"),  # update existing
            str(MASTER_CRM / "scripts/lighthouse_audit.sh"),
        ],
        "effort": "large",
        "dependencies": ["#39 Page Template System (shared CSS)"],
    },
}


# ─────────────────────────────────────────────────────────────
# EXECUTION FUNCTIONS
# ─────────────────────────────────────────────────────────────

def show_plan():
    """Display the full implementation plan."""
    print("=" * 70)
    print("FINAL 13 FEATURES — IMPLEMENTATION PLAN")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)

    groups = {"MARK_DONE": [], "FINISH": [], "BUILD": []}
    for fid, f in FEATURES.items():
        groups[f["group"]].append((fid, f))

    print(f"\n{'─'*70}")
    print("GROUP 1: MARK AS DONE (4 features — already built or superseded)")
    print(f"{'─'*70}")
    for fid, f in groups["MARK_DONE"]:
        status = "✅" if os.path.exists(f.get("verify_file", "")) else "❓"
        print(f"  {status} #{fid} {f['name']}")
        print(f"     → {f['reason']}")
        if f.get("note"):
            print(f"     ⚠️  {f['note']}")

    print(f"\n{'─'*70}")
    print("GROUP 2: FINISH (3 features — partially built, need completion)")
    print(f"{'─'*70}")
    for fid, f in groups["FINISH"]:
        print(f"  🔧 #{fid} {f['name']} [{f['effort']}]")
        print(f"     EXISTS: {f['what_exists']}")
        print(f"     NEEDS:")
        for item in f["what_needs_building"]:
            print(f"       • {item}")
        print(f"     OUTPUT: {', '.join(os.path.basename(p) for p in f['output_files'])}")

    print(f"\n{'─'*70}")
    print("GROUP 3: BUILD (6 features — need full implementation)")
    print(f"{'─'*70}")
    for fid, f in groups["BUILD"]:
        print(f"  🏗️  #{fid} {f['name']} [{f['effort']}]")
        print(f"     {f['description']}")
        if f.get("spec", {}).get("decision_needed"):
            print(f"     ⚠️  DECISION NEEDED: {f['spec']['decision_needed']}")
        print(f"     OUTPUT: {', '.join(os.path.basename(p) for p in f['output_files'])}")

    print(f"\n{'─'*70}")
    print("EXECUTION ORDER (recommended)")
    print(f"{'─'*70}")
    print("  Phase 1: Mark 4 features DONE, update roadmap → 61/70 (87%)")
    print("  Phase 2: #39 Page Template System (foundation for others)")
    print("  Phase 3: #49 Guardrail Log + #50 Away Summary (can parallelize)")
    print("  Phase 4: #44 Diff View + #46 Research Learning (can parallelize)")
    print("  Phase 5: #40 Why Sell + #45 Feedback Conversation (can parallelize)")
    print("  Phase 6: #48 Google Drive Sync (needs credentials)")
    print("  Phase 7: #71 Shareable URL Polish (final pass, depends on #39)")
    print(f"\n  Total: 13 features → roadmap 70/70 (100%)")


def check_status():
    """Check which features are already verifiable."""
    print("FEATURE STATUS CHECK")
    print("=" * 60)
    for fid, f in sorted(FEATURES.items()):
        verify = f.get("verify_file")
        outputs = f.get("output_files", [])

        if verify:
            exists = os.path.exists(verify)
            print(f"  #{fid:2d} {f['name']:40s} {'✅ VERIFIED' if exists else '❌ MISSING'}")
        elif outputs:
            built = sum(1 for o in outputs if os.path.exists(o))
            total = len(outputs)
            print(f"  #{fid:2d} {f['name']:40s} {built}/{total} files exist")
        else:
            print(f"  #{fid:2d} {f['name']:40s} ❓ NO VERIFICATION")


def build_feature(feature_id):
    """Placeholder for building a specific feature."""
    if feature_id not in FEATURES:
        print(f"Unknown feature #{feature_id}")
        return False

    f = FEATURES[feature_id]
    print(f"\n🏗️  Building #{feature_id}: {f['name']}")
    print(f"   Group: {f['group']}")

    if f["group"] == "MARK_DONE":
        print(f"   → This feature is already done: {f['reason']}")
        print(f"   → Action: Update roadmap HTML to mark as complete")
        return True

    print(f"   → Implementation required. Use Claude Code to build:")
    for output in f.get("output_files", []):
        print(f"     • {output}")

    return True


def build_all():
    """Show build order for all features."""
    phases = [
        ("Phase 1: Mark Done", [38, 43, 47, 55]),
        ("Phase 2: Foundation", [39]),
        ("Phase 3: Monitoring (parallel)", [49, 50]),
        ("Phase 4: Intelligence (parallel)", [44, 46]),
        ("Phase 5: Content (parallel)", [40, 45]),
        ("Phase 6: Integration", [48]),
        ("Phase 7: Polish", [71]),
    ]

    for phase_name, feature_ids in phases:
        print(f"\n{'═'*60}")
        print(f"  {phase_name}")
        print(f"{'═'*60}")
        for fid in feature_ids:
            f = FEATURES[fid]
            print(f"  #{fid} {f['name']} — {f['group']}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Final 13 Features Builder")
    parser.add_argument("--plan", action="store_true", help="Show full plan")
    parser.add_argument("--status", action="store_true", help="Check implementation status")
    parser.add_argument("--build", type=int, help="Build specific feature")
    parser.add_argument("--build-all", action="store_true", help="Show build-all order")
    args = parser.parse_args()

    if args.plan:
        show_plan()
    elif args.status:
        check_status()
    elif args.build:
        build_feature(args.build)
    elif args.build_all:
        build_all()
    else:
        show_plan()
