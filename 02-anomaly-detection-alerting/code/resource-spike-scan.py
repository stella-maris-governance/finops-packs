#!/usr/bin/env python3
"""
Resource-Level Spike Scanner — Stella Maris Governance
Identifies individual resources with abnormal daily cost increases.
"""

import json
import argparse
from datetime import datetime


def scan_spikes(resources: list, multiplier: float = 2.0) -> list:
    """Find resources where today's cost exceeds multiplier × 7-day average."""
    findings = []
    for r in resources:
        avg = r.get("seven_day_avg", 0)
        today = r.get("today_cost", 0)

        if avg > 0 and today > avg * multiplier:
            findings.append({
                "resource": r["name"],
                "resource_id": r.get("id", ""),
                "today_cost": round(today, 2),
                "seven_day_avg": round(avg, 2),
                "multiplier": round(today / avg, 1),
                "owner": r.get("tags", {}).get("Owner", "UNTAGGED"),
                "environment": r.get("tags", {}).get("Environment", "UNTAGGED"),
                "severity": "HIGH" if today > avg * 3 else "WARNING"
            })
    return sorted(findings, key=lambda x: x["today_cost"], reverse=True)


def main():
    parser = argparse.ArgumentParser(description="Stella Maris Resource Spike Scanner")
    parser.add_argument("--resources", required=True, help="Resource cost data JSON")
    parser.add_argument("--multiplier", type=float, default=2.0, help="Spike threshold multiplier")
    args = parser.parse_args()

    with open(args.resources) as f:
        data = json.load(f)
    resources = data.get("resources", [])

    findings = scan_spikes(resources, args.multiplier)

    print(f"{'='*60}")
    print(f"  RESOURCE SPIKE SCAN")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Resources scanned: {len(resources)}")
    print(f"  Threshold: {args.multiplier}× 7-day average")
    print(f"{'='*60}")
    print()

    if findings:
        for f_item in findings:
            icon = "🔴" if f_item["severity"] == "HIGH" else "🟡"
            print(f"  {icon} {f_item['resource']} [{f_item['owner']}]")
            print(f"      Today: ${f_item['today_cost']} | 7-day avg: ${f_item['seven_day_avg']} | {f_item['multiplier']}×")
            print()
    else:
        print(f"  ✓ No resource spikes detected")
        print()

    print(f"{'='*60}")
    print(f"  Spikes found: {len(findings)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
