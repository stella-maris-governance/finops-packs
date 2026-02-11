#!/usr/bin/env python3
"""
Reservation Coverage Report — Stella Maris Governance
FinOps Pack 03

Reports current reservation coverage, utilization, and savings.
"""

import json
from datetime import datetime, date


def generate_report(register: dict) -> str:
    """Generate coverage report from reservation register."""
    reservations = register.get("reservations", [])
    lines = []

    lines.append(f"{'='*60}")
    lines.append(f"  RESERVATION COVERAGE REPORT")
    lines.append(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"  Active reservations: {len(reservations)}")
    lines.append(f"{'='*60}")
    lines.append("")

    total_monthly_commitment = 0
    total_monthly_savings = 0
    total_on_demand_equivalent = 0

    for r in reservations:
        status_icon = "🟢" if r.get("utilization_pct", 0) >= 80 else "🟡" if r.get("utilization_pct", 0) >= 60 else "🔴"
        lines.append(f"  {status_icon} {r['name']} [{r.get('type', 'Unknown')}]")
        lines.append(f"      Term: {r.get('term_months', 12)} months | "
                     f"Purchased: {r.get('purchase_date', 'N/A')} | "
                     f"Expires: {r.get('expiry_date', 'N/A')}")
        lines.append(f"      Monthly cost: ${r.get('monthly_cost', 0)} | "
                     f"On-demand equivalent: ${r.get('on_demand_equivalent', 0)}")
        lines.append(f"      Utilization: {r.get('utilization_pct', 0)}% | "
                     f"Monthly savings: ${r.get('monthly_savings', 0)}")

        # Expiry warning
        if r.get("expiry_date"):
            try:
                expiry = date.fromisoformat(r["expiry_date"])
                days_remaining = (expiry - date.today()).days
                if days_remaining <= 90:
                    lines.append(f"      ⚠️  EXPIRING IN {days_remaining} DAYS — renewal decision required")
            except ValueError:
                pass

        lines.append("")

        total_monthly_commitment += r.get("monthly_cost", 0)
        total_monthly_savings += r.get("monthly_savings", 0)
        total_on_demand_equivalent += r.get("on_demand_equivalent", 0)

    # Summary
    coverage_pct = round((total_monthly_commitment / total_on_demand_equivalent * 100), 1) if total_on_demand_equivalent > 0 else 0

    lines.append(f"{'='*60}")
    lines.append(f"  SUMMARY")
    lines.append(f"  Total monthly commitment: ${total_monthly_commitment}")
    lines.append(f"  On-demand equivalent:     ${total_on_demand_equivalent}")
    lines.append(f"  Monthly savings:          ${total_monthly_savings}")
    lines.append(f"  Annual projected savings: ${total_monthly_savings * 12}")
    lines.append(f"  Coverage:                 {coverage_pct}%")
    lines.append(f"{'='*60}")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            register = json.load(f)
        print(generate_report(register))
    else:
        print("Usage: python3 reservation-coverage-report.py <register.json>")
