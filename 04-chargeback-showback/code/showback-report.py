#!/usr/bin/env python3
"""
Showback Report Generator — Stella Maris Governance
FinOps Pack 04

Generates per-team, per-project, per-cost-center showback reports.
"""

import json
import argparse
from datetime import datetime


def generate_showback(allocation: dict, budgets: dict = None) -> str:
    """Generate Markdown showback report from allocation data."""
    lines = []
    alloc_date = allocation.get("allocation_date", "Unknown")
    fully_loaded = allocation.get("fully_loaded", {})
    cost_centers = fully_loaded.get("cost_centers", {})
    grand_total = fully_loaded.get("grand_total", 0)
    quarantine = fully_loaded.get("untagged_quarantine", 0)
    budgets = budgets or {}

    lines.append(f"# Monthly Showback Report")
    lines.append(f"")
    lines.append(f"> **Period:** {alloc_date}")
    lines.append(f"> **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"> **Total spend:** ${grand_total:,.2f}")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    # Summary table
    lines.append(f"## Cost Center Summary")
    lines.append(f"")
    lines.append(f"| Cost Center | Direct | Shared | Total | % of Spend | Budget | Variance |")
    lines.append(f"|-------------|--------|--------|-------|-----------|--------|----------|")

    for cc, data in sorted(cost_centers.items()):
        pct = (data["total"] / grand_total * 100) if grand_total > 0 else 0
        budget = budgets.get(cc, {}).get("monthly", 0)
        variance = budget - data["total"] if budget > 0 else 0
        var_str = f"${variance:,.2f}" if budget > 0 else "N/A"
        bud_str = f"${budget:,.2f}" if budget > 0 else "N/A"
        lines.append(f"| {cc} | ${data['direct']:,.2f} | ${data['shared']:,.2f} | "
                     f"${data['total']:,.2f} | {pct:.1f}% | {bud_str} | {var_str} |")

    if quarantine > 0:
        q_pct = (quarantine / grand_total * 100) if grand_total > 0 else 0
        lines.append(f"| **Untagged (quarantine)** | ${quarantine:,.2f} | — | "
                     f"${quarantine:,.2f} | {q_pct:.1f}% | — | — |")

    lines.append(f"| **TOTAL** | | | **${grand_total:,.2f}** | 100% | | |")
    lines.append(f"")

    # Shared cost detail
    shared_dist = allocation.get("shared_distributions", {})
    if shared_dist:
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## Shared Cost Distribution Detail")
        lines.append(f"")
        lines.append(f"| Shared Resource | Total | Method | Distribution |")
        lines.append(f"|----------------|-------|--------|-------------|")

        for name, dist in shared_dist.items():
            if "allocation" in dist:
                alloc_str = ", ".join(f"{cc}: ${amt:,.2f}" for cc, amt in dist["allocation"].items())
                lines.append(f"| {name} | ${dist['total_cost']:,.2f} | {dist['method']} | {alloc_str} |")

    lines.append(f"")

    # Environment breakdown
    by_env = allocation.get("direct", {}).get("by_environment", {})
    if by_env:
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## Environment Breakdown")
        lines.append(f"")
        lines.append(f"| Environment | Monthly Cost | % of Direct |")
        lines.append(f"|-------------|-------------|-------------|")
        direct_total = sum(by_env.values())
        for env, cost in sorted(by_env.items(), key=lambda x: -x[1]):
            pct = (cost / direct_total * 100) if direct_total > 0 else 0
            lines.append(f"| {env} | ${cost:,.2f} | {pct:.1f}% |")

    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"*Stella Maris Governance — The team that provisions the resource owns the bill.*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Stella Maris Showback Report")
    parser.add_argument("--allocation", "-a", required=True, help="Allocation output JSON")
    parser.add_argument("--budgets", "-b", default=None, help="Budget definitions JSON")
    parser.add_argument("--output", "-o", default=None, help="Output report (.md)")
    args = parser.parse_args()

    with open(args.allocation) as f:
        allocation = json.load(f)

    budgets = {}
    if args.budgets:
        with open(args.budgets) as f:
            budgets = json.load(f).get("budgets", {})

    report = generate_showback(allocation, budgets)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Showback report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
