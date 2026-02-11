#!/usr/bin/env python3
"""
Orphan Resource Detector — Stella Maris Governance
FinOps Pack 05

Finds resources that have lost their parent:
disks without VMs, IPs without NICs, NICs without VMs,
aged snapshots, empty resource groups.

Author: Robert Myers, MBA | Stella Maris Governance
"""

import json
import argparse
from datetime import datetime, date


def detect_orphans(resources: list) -> list:
    """Find orphaned resources across all types."""
    orphans = []
    today = date.today()

    for r in resources:
        rtype = r.get("type", "")
        is_orphan = False
        orphan_reason = ""

        if rtype == "Microsoft.Compute/disks":
            if not r.get("attached_vm"):
                is_orphan = True
                orphan_reason = "Managed disk not attached to any VM"

        elif rtype == "Microsoft.Network/publicIPAddresses":
            if not r.get("attached_nic"):
                is_orphan = True
                orphan_reason = "Public IP not associated with any NIC"

        elif rtype == "Microsoft.Network/networkInterfaces":
            if not r.get("attached_vm"):
                is_orphan = True
                orphan_reason = "NIC not attached to any VM"

        elif rtype == "Microsoft.Network/networkSecurityGroups":
            if r.get("attached_nic_count", 0) == 0 and r.get("attached_subnet_count", 0) == 0:
                is_orphan = True
                orphan_reason = "NSG not attached to any NIC or subnet"

        elif rtype == "Microsoft.Compute/snapshots":
            age_days = r.get("age_days", 0)
            if age_days > 90:
                is_orphan = True
                orphan_reason = f"Snapshot is {age_days} days old (threshold: 90)"

        elif rtype == "Microsoft.Resources/resourceGroups":
            if r.get("resource_count", 0) == 0:
                is_orphan = True
                orphan_reason = "Empty resource group — contains 0 resources"

        if is_orphan:
            orphans.append({
                "resource": r.get("name", "Unknown"),
                "resource_id": r.get("id", ""),
                "resource_type": rtype,
                "reason": orphan_reason,
                "monthly_cost": r.get("monthly_cost", 0),
                "created_date": r.get("created_date", "unknown"),
                "tags": r.get("tags", {}),
                "disposition": "decommission"
            })

    return orphans


def main():
    parser = argparse.ArgumentParser(
        description="Stella Maris Orphan Detector (FinOps Pack 05)"
    )
    parser.add_argument("--resources", "-r", required=True, help="Resources JSON")
    parser.add_argument("--output", "-o", default=None, help="Output JSON")
    args = parser.parse_args()

    with open(args.resources) as f:
        data = json.load(f)

    orphans = detect_orphans(data.get("resources", []))

    print(f"{'='*60}")
    print(f"  ORPHAN RESOURCE DETECTION")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Resources scanned: {len(data.get('resources', []))}")
    print(f"  Orphans found: {len(orphans)}")
    print(f"{'='*60}")
    print()

    total_cost = 0
    for o in orphans:
        print(f"  👻 {o['resource']} [{o['resource_type'].split('/')[-1]}]")
        print(f"     {o['reason']}")
        print(f"     Cost: ${o['monthly_cost']:.2f}/mo | Created: {o['created_date']}")
        print()
        total_cost += o["monthly_cost"]

    print(f"{'='*60}")
    print(f"  Total orphan cost: ${total_cost:.2f}/month (${total_cost*12:.2f}/year)")
    print(f"  Orphans accumulate when nobody looks.")
    print(f"{'='*60}")

    if args.output:
        with open(args.output, 'w') as f:
            json.dump({"orphans": orphans, "total_monthly_cost": total_cost}, f, indent=2)


if __name__ == "__main__":
    main()
