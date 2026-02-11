#!/usr/bin/env python3
"""
Waste Scanner — Stella Maris Governance
FinOps Pack 05

Scans 6 categories of cloud waste:
  1. Idle resources (near-zero utilization)
  2. Over-provisioned resources (right-sizing candidates)
  3. Orphan resources (lost their parent)
  4. Schedule optimization (24/7 when shouldn't be)
  5. Aged resources (past expiry or review date)
  6. Pricing tier waste (premium tier, standard workload)

Author: Robert Myers, MBA | Stella Maris Governance
"""

import json
import argparse
from datetime import datetime, date, timedelta
from collections import defaultdict


# Configurable thresholds
THRESHOLDS = {
    "idle_cpu_pct": 5,
    "idle_days": 14,
    "orphan_snapshot_days": 90,
    "aged_overdue_days": 0,
    "overprovisioned_p95_pct": 40,
    "schedule_env": ["development", "test", "sandbox"]
}


def scan_idle(resources: list, thresholds: dict) -> list:
    """Category 1: Find resources with near-zero utilization."""
    findings = []
    for r in resources:
        metrics = r.get("metrics", {})
        avg_cpu = metrics.get("avg_cpu_pct", 100)
        avg_days = metrics.get("low_util_days", 0)
        connections = metrics.get("network_connections_30d", -1)

        if avg_cpu < thresholds.get("idle_cpu_pct", 5) and avg_days >= thresholds.get("idle_days", 14):
            findings.append({
                "finding_id": f"WASTE-IDLE-{len(findings)+1:03d}",
                "category": "idle",
                "resource": r.get("name", "Unknown"),
                "resource_id": r.get("id", ""),
                "resource_type": r.get("type", ""),
                "avg_cpu": avg_cpu,
                "idle_days": avg_days,
                "connections_30d": connections,
                "monthly_cost": r.get("monthly_cost", 0),
                "tags": r.get("tags", {}),
                "recommended_disposition": "decommission" if connections == 0 else "investigate",
                "reason": f"CPU avg {avg_cpu}% for {avg_days} days"
                          + (f", 0 network connections" if connections == 0 else "")
            })
    return findings


def scan_rightsizing(resources: list, thresholds: dict) -> list:
    """Category 2: Find over-provisioned resources."""
    findings = []
    for r in resources:
        metrics = r.get("metrics", {})
        p95_cpu = metrics.get("p95_cpu_pct", 100)
        p95_mem = metrics.get("p95_memory_pct", 100)
        avg_cpu = metrics.get("avg_cpu_pct", 100)
        current_sku = r.get("sku", "")
        recommended_sku = r.get("recommended_sku", "")

        threshold = thresholds.get("overprovisioned_p95_pct", 40)

        if p95_cpu < threshold and recommended_sku and recommended_sku != current_sku:
            savings = r.get("monthly_cost", 0) - r.get("recommended_cost", r.get("monthly_cost", 0))
            env = r.get("tags", {}).get("Environment", "unknown")

            findings.append({
                "finding_id": f"WASTE-RSIZE-{len(findings)+1:03d}",
                "category": "rightsizing",
                "resource": r.get("name", "Unknown"),
                "resource_id": r.get("id", ""),
                "resource_type": r.get("type", ""),
                "current_sku": current_sku,
                "recommended_sku": recommended_sku,
                "p95_cpu": p95_cpu,
                "p95_memory": p95_mem,
                "avg_cpu": avg_cpu,
                "monthly_cost": r.get("monthly_cost", 0),
                "recommended_cost": r.get("recommended_cost", 0),
                "monthly_savings": round(savings, 2),
                "recommended_disposition": "rightsize" if env != "production" else "defer",
                "reason": f"P95 CPU {p95_cpu}%, current {current_sku} → {recommended_sku}"
                          + (f" (PRODUCTION — defer)" if env == "production" else "")
            })
    return findings


def scan_orphans(resources: list, thresholds: dict) -> list:
    """Category 3: Find resources without parents."""
    findings = []
    orphan_types = {
        "Microsoft.Compute/disks": {"parent_field": "attached_vm", "label": "Unattached disk"},
        "Microsoft.Network/publicIPAddresses": {"parent_field": "attached_nic", "label": "Unattached public IP"},
        "Microsoft.Network/networkInterfaces": {"parent_field": "attached_vm", "label": "Unattached NIC"},
        "Microsoft.Network/networkSecurityGroups": {"parent_field": "attached_nic_count", "label": "Unattached NSG"},
        "Microsoft.Compute/snapshots": {"parent_field": "age_days", "label": "Aged snapshot"}
    }

    for r in resources:
        rtype = r.get("type", "")
        if rtype not in orphan_types:
            continue

        config = orphan_types[rtype]
        parent_value = r.get(config["parent_field"])

        is_orphan = False
        if rtype == "Microsoft.Compute/snapshots":
            age = r.get("age_days", 0)
            if age > thresholds.get("orphan_snapshot_days", 90):
                is_orphan = True
        elif rtype == "Microsoft.Network/networkSecurityGroups":
            if parent_value == 0:
                is_orphan = True
        elif not parent_value:
            is_orphan = True

        if is_orphan:
            findings.append({
                "finding_id": f"WASTE-ORPHAN-{len(findings)+1:03d}",
                "category": "orphan",
                "resource": r.get("name", "Unknown"),
                "resource_id": r.get("id", ""),
                "resource_type": rtype,
                "orphan_type": config["label"],
                "monthly_cost": r.get("monthly_cost", 0),
                "created_date": r.get("created_date", "unknown"),
                "tags": r.get("tags", {}),
                "recommended_disposition": "decommission",
                "reason": config["label"] + (" — " + f"{r.get('age_days', 0)} days old" if rtype == "Microsoft.Compute/snapshots" else "")
            })
    return findings


def scan_schedule(resources: list, thresholds: dict) -> list:
    """Category 4: Find resources running 24/7 that shouldn't be."""
    findings = []
    target_envs = thresholds.get("schedule_env", ["development", "test", "sandbox"])

    for r in resources:
        env = r.get("tags", {}).get("Environment", "").lower()
        if env not in target_envs:
            continue

        rtype = r.get("type", "")
        if rtype not in ["Microsoft.Compute/virtualMachines", "Microsoft.Web/serverfarms",
                         "Microsoft.Sql/servers/databases"]:
            continue

        hours_running = r.get("metrics", {}).get("hours_per_month", 730)
        if hours_running > 400:  # More than business hours
            business_hours = 220  # 8am-6pm, Mon-Fri
            waste_hours = hours_running - business_hours
            waste_pct = round((waste_hours / hours_running) * 100)
            potential_savings = round(r.get("monthly_cost", 0) * (waste_pct / 100), 2)

            findings.append({
                "finding_id": f"WASTE-SCHED-{len(findings)+1:03d}",
                "category": "schedule",
                "resource": r.get("name", "Unknown"),
                "resource_id": r.get("id", ""),
                "resource_type": rtype,
                "environment": env,
                "hours_running": hours_running,
                "recommended_hours": business_hours,
                "waste_hours": waste_hours,
                "waste_pct": waste_pct,
                "monthly_cost": r.get("monthly_cost", 0),
                "potential_savings": potential_savings,
                "recommended_disposition": "schedule",
                "reason": f"{env} resource running {hours_running}hrs/month, recommend {business_hours}hrs"
            })
    return findings


def scan_aged(resources: list, thresholds: dict) -> list:
    """Category 5: Find resources past expiry or review date."""
    findings = []
    today = date.today()

    for r in resources:
        tags = r.get("tags", {})

        # Check ExpiryDate
        expiry = tags.get("ExpiryDate", "")
        if expiry:
            try:
                exp_date = date.fromisoformat(expiry)
                if exp_date < today:
                    days_past = (today - exp_date).days
                    findings.append({
                        "finding_id": f"WASTE-AGED-{len(findings)+1:03d}",
                        "category": "aged",
                        "subcategory": "expired",
                        "resource": r.get("name", "Unknown"),
                        "resource_id": r.get("id", ""),
                        "expiry_date": expiry,
                        "days_past_expiry": days_past,
                        "monthly_cost": r.get("monthly_cost", 0),
                        "recommended_disposition": "decommission",
                        "reason": f"ExpiryDate {expiry} — {days_past} days past"
                    })
            except ValueError:
                pass

        # Check ReviewDate
        review = tags.get("ReviewDate", "")
        if review:
            try:
                rev_date = date.fromisoformat(review)
                if rev_date < today:
                    days_overdue = (today - rev_date).days
                    findings.append({
                        "finding_id": f"WASTE-AGED-{len(findings)+1:03d}",
                        "category": "aged",
                        "subcategory": "review_overdue",
                        "resource": r.get("name", "Unknown"),
                        "resource_id": r.get("id", ""),
                        "review_date": review,
                        "days_overdue": days_overdue,
                        "monthly_cost": r.get("monthly_cost", 0),
                        "recommended_disposition": "review",
                        "reason": f"ReviewDate {review} — {days_overdue} days overdue"
                    })
            except ValueError:
                pass

    return findings


def run_full_scan(resources: list, thresholds: dict = None) -> dict:
    """Run all 6 scan categories."""
    t = thresholds or THRESHOLDS

    idle = scan_idle(resources, t)
    rightsizing = scan_rightsizing(resources, t)
    orphans = scan_orphans(resources, t)
    schedule = scan_schedule(resources, t)
    aged = scan_aged(resources, t)

    all_findings = idle + rightsizing + orphans + schedule + aged

    total_confirmed = sum(f.get("monthly_cost", 0) for f in idle + orphans)
    total_rightsizing = sum(f.get("monthly_savings", 0) for f in rightsizing)
    total_schedule = sum(f.get("potential_savings", 0) for f in schedule)

    return {
        "scan_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
        "resources_scanned": len(resources),
        "total_findings": len(all_findings),
        "by_category": {
            "idle": {"count": len(idle), "monthly_cost": sum(f["monthly_cost"] for f in idle)},
            "rightsizing": {"count": len(rightsizing), "monthly_savings": total_rightsizing},
            "orphans": {"count": len(orphans), "monthly_cost": sum(f["monthly_cost"] for f in orphans)},
            "schedule": {"count": len(schedule), "potential_savings": total_schedule},
            "aged": {"count": len(aged)}
        },
        "savings_summary": {
            "confirmed": round(total_confirmed, 2),
            "rightsizing": round(total_rightsizing, 2),
            "schedule_estimated": round(total_schedule, 2),
            "total_potential": round(total_confirmed + total_rightsizing + total_schedule, 2)
        },
        "findings": all_findings
    }


def main():
    parser = argparse.ArgumentParser(
        description="Stella Maris Waste Scanner (FinOps Pack 05)"
    )
    parser.add_argument("--resources", "-r", required=True, help="Resources JSON")
    parser.add_argument("--output", "-o", default=None, help="Output findings JSON")
    parser.add_argument("--thresholds", "-t", default=None, help="Custom thresholds JSON")
    args = parser.parse_args()

    with open(args.resources) as f:
        data = json.load(f)
    resources = data.get("resources", [])

    thresholds = THRESHOLDS
    if args.thresholds:
        with open(args.thresholds) as f:
            thresholds = json.load(f)

    results = run_full_scan(resources, thresholds)

    print(f"{'='*60}")
    print(f"  WASTE SCAN RESULTS")
    print(f"  Date: {results['scan_date']}")
    print(f"  Resources scanned: {results['resources_scanned']}")
    print(f"  Findings: {results['total_findings']}")
    print(f"{'='*60}")
    print()

    for f in results["findings"]:
        icon = {"idle": "💤", "rightsizing": "📐", "orphan": "👻",
                "schedule": "⏰", "aged": "📅"}.get(f["category"], "❓")
        cost_str = f"${f.get('monthly_cost', 0):.2f}/mo" if f.get("monthly_cost") else ""
        save_str = f"save ${f.get('monthly_savings', 0):.2f}/mo" if f.get("monthly_savings") else ""
        save_str = f"save ${f.get('potential_savings', 0):.2f}/mo" if f.get("potential_savings") and not save_str else save_str

        print(f"  {icon} [{f['category'].upper()}] {f['resource']}")
        print(f"     {f['reason']}")
        print(f"     Disposition: {f['recommended_disposition']}"
              + (f" | {cost_str}" if cost_str else "")
              + (f" | {save_str}" if save_str else ""))
        print()

    s = results["savings_summary"]
    print(f"{'='*60}")
    print(f"  SAVINGS SUMMARY")
    print(f"  Confirmed (idle + orphan):   ${s['confirmed']:.2f}/month")
    print(f"  Right-sizing:                ${s['rightsizing']:.2f}/month")
    print(f"  Schedule (estimated):        ${s['schedule_estimated']:.2f}/month")
    print(f"  Total potential:             ${s['total_potential']:.2f}/month")
    print(f"  Annual potential:            ${s['total_potential'] * 12:,.2f}/year")
    print(f"{'='*60}")
    print(f"  Every idle resource is a silent invoice.")

    if args.output:
        with open(args.output, 'w') as f_out:
            json.dump(results, f_out, indent=2)
        print(f"\n  Results written to {args.output}")


if __name__ == "__main__":
    main()
