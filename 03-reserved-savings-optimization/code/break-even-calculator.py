#!/usr/bin/env python3
"""
Break-Even Calculator — Stella Maris Governance
FinOps Pack 03

Calculates when a reservation pays for itself and models
the risk if a workload is decommissioned early.

Author: Robert Myers, MBA | Stella Maris Governance
"""

import json
import argparse
from datetime import datetime


def calculate_breakeven(candidate: dict) -> dict:
    """Calculate break-even for 1-year and 3-year RI terms."""
    name = candidate.get("name", "Unknown")
    on_demand_monthly = candidate.get("on_demand_monthly", 0)

    results = {"resource": name, "on_demand_monthly": on_demand_monthly, "terms": []}

    for term in candidate.get("terms", []):
        term_months = term.get("months", 12)
        ri_monthly = term.get("ri_monthly", 0)
        upfront = term.get("upfront", 0)
        discount_pct = term.get("discount_pct", 0)

        monthly_savings = on_demand_monthly - ri_monthly
        total_commitment = (ri_monthly * term_months) + upfront
        total_on_demand = on_demand_monthly * term_months
        total_savings = total_on_demand - total_commitment

        # Break-even month (when cumulative savings exceed upfront cost)
        if upfront > 0 and monthly_savings > 0:
            breakeven_month = -(-upfront // monthly_savings)  # Ceiling division
        elif monthly_savings > 0:
            breakeven_month = 1  # No upfront = immediate savings
        else:
            breakeven_month = None  # No savings — bad deal

        # Risk analysis: if decommissioned at month N
        risk_scenarios = []
        checkpoints = [3, 6, 9, 12] if term_months == 12 else [6, 12, 18, 24, 30, 36]
        for month_n in checkpoints:
            if month_n > term_months:
                continue
            savings_at_n = (monthly_savings * month_n) - upfront
            remaining_commitment = ri_monthly * (term_months - month_n)
            wasted_if_decommissioned = remaining_commitment
            net = savings_at_n - wasted_if_decommissioned

            risk_scenarios.append({
                "decommission_month": month_n,
                "savings_to_date": round(savings_at_n, 2),
                "wasted_commitment": round(wasted_if_decommissioned, 2),
                "net_position": round(net, 2),
                "verdict": "NET POSITIVE" if net > 0 else "NET NEGATIVE"
            })

        results["terms"].append({
            "term_months": term_months,
            "ri_monthly": ri_monthly,
            "upfront": upfront,
            "discount_pct": discount_pct,
            "monthly_savings": round(monthly_savings, 2),
            "total_savings": round(total_savings, 2),
            "breakeven_month": breakeven_month,
            "risk_scenarios": risk_scenarios
        })

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Stella Maris Break-Even Calculator (FinOps Pack 03)"
    )
    parser.add_argument("--candidates", "-c", required=True, help="Candidates JSON")
    parser.add_argument("--output", "-o", default=None, help="Output JSON")
    args = parser.parse_args()

    with open(args.candidates) as f:
        data = json.load(f)
    candidates = data.get("candidates", [])

    print(f"{'='*60}")
    print(f"  BREAK-EVEN ANALYSIS")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")
    print()

    all_results = []
    total_annual_savings = 0

    for c in candidates:
        result = calculate_breakeven(c)
        all_results.append(result)

        print(f"  ─── {result['resource']} ───")
        print(f"  On-demand: ${result['on_demand_monthly']}/month")
        print()

        for t in result["terms"]:
            label = f"{t['term_months']}-month RI"
            print(f"    {label}: ${t['ri_monthly']}/month ({t['discount_pct']}% discount)")
            print(f"    Monthly savings: ${t['monthly_savings']}")
            print(f"    Break-even: Month {t['breakeven_month']}")
            print(f"    Total savings over term: ${t['total_savings']}")

            if t["term_months"] == 12:
                total_annual_savings += t["total_savings"]

            print(f"    Risk scenarios:")
            for rs in t["risk_scenarios"]:
                icon = "✅" if rs["verdict"] == "NET POSITIVE" else "❌"
                print(f"      {icon} Decommission month {rs['decommission_month']}: "
                      f"net ${rs['net_position']} ({rs['verdict']})")
            print()

    print(f"{'='*60}")
    print(f"  Total projected annual savings (1-year terms): ${round(total_annual_savings, 2)}")
    print(f"  On-demand is rack rate. Reservations are the negotiation.")
    print(f"{'='*60}")

    if args.output:
        with open(args.output, 'w') as f:
            json.dump({"results": all_results}, f, indent=2)


if __name__ == "__main__":
    main()
