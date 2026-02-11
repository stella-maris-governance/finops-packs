#!/usr/bin/env python3
"""
Tag Compliance Report — Stella Maris Governance
Generate tag compliance metrics from Azure Resource Graph data.
"""

import json
import sys
import argparse
from datetime import datetime
from collections import defaultdict


REQUIRED_TAGS = ["Owner", "Environment", "CostCenter", "Project"]
RECOMMENDED_TAGS = ["Criticality", "DataClassification", "CreatedDate", "ReviewDate", "ExpiryDate", "ManagedBy"]


def analyze_compliance(resources: list) -> dict:
    """Analyze tag compliance across resource inventory."""
    total = len(resources)
    if total == 0:
        return {"error": "No resources found"}

    required_compliance = {}
    recommended_compliance = {}

    for tag in REQUIRED_TAGS:
        tagged = sum(1 for r in resources if r.get("tags", {}).get(tag))
        required_compliance[tag] = {
            "tagged": tagged,
            "total": total,
            "percent": round(tagged / total * 100, 1)
        }

    for tag in RECOMMENDED_TAGS:
        tagged = sum(1 for r in resources if r.get("tags", {}).get(tag))
        recommended_compliance[tag] = {
            "tagged": tagged,
            "total": total,
            "percent": round(tagged / total * 100, 1)
        }

    req_total_slots = total * len(REQUIRED_TAGS)
    req_filled = sum(v["tagged"] for v in required_compliance.values())
    rec_total_slots = total * len(RECOMMENDED_TAGS)
    rec_filled = sum(v["tagged"] for v in recommended_compliance.values())

    return {
        "total_resources": total,
        "required": {
            "aggregate_percent": round(req_filled / req_total_slots * 100, 1),
            "per_tag": required_compliance
        },
        "recommended": {
            "aggregate_percent": round(rec_filled / rec_total_slots * 100, 1),
            "per_tag": recommended_compliance
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Stella Maris Tag Compliance Report")
    parser.add_argument("--resources", required=True, help="Path to resource inventory JSON")
    parser.add_argument("--output", default=None, help="Output report JSON")
    args = parser.parse_args()

    with open(args.resources) as f:
        resources = json.load(f)

    if isinstance(resources, dict):
        resources = resources.get("resources", [])

    report = analyze_compliance(resources)

    print(f"{'='*60}")
    print(f"  TAG COMPLIANCE REPORT")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Resources: {report['total_resources']}")
    print(f"{'='*60}")
    print()

    print(f"  REQUIRED TAGS — Aggregate: {report['required']['aggregate_percent']}%")
    for tag, data in report["required"]["per_tag"].items():
        bar = "█" * int(data["percent"] / 5) + "░" * (20 - int(data["percent"] / 5))
        print(f"    {tag:.<25} {data['percent']:>5.1f}%  {bar}  ({data['tagged']}/{data['total']})")
    print()

    print(f"  RECOMMENDED TAGS — Aggregate: {report['recommended']['aggregate_percent']}%")
    for tag, data in report["recommended"]["per_tag"].items():
        bar = "█" * int(data["percent"] / 5) + "░" * (20 - int(data["percent"] / 5))
        print(f"    {tag:.<25} {data['percent']:>5.1f}%  {bar}  ({data['tagged']}/{data['total']})")
    print()

    print(f"{'='*60}")
    print(f"  You cannot govern what you cannot see.")
    print(f"{'='*60}")

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n  Report written to {args.output}")


if __name__ == "__main__":
    main()
