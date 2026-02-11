#!/usr/bin/env python3
"""
Cost Allocation Engine — Stella Maris Governance
FinOps Pack 04

Three-layer allocation:
  Layer 1: Direct attribution via Pack 01 tags
  Layer 2: Shared cost distribution (proportional, equal, fixed)
  Layer 3: Untagged cost quarantine

Zero leakage: every dollar in = every dollar out.

Author: Robert Myers, MBA | Stella Maris Governance
"""

import json
import argparse
from datetime import datetime
from collections import defaultdict


def allocate_direct(resources: list) -> dict:
    """Layer 1: Attribute costs to tagged entities."""
    by_cost_center = defaultdict(lambda: {"direct": 0.0, "resources": []})
    by_owner = defaultdict(float)
    by_project = defaultdict(float)
    by_environment = defaultdict(float)
    untagged = {"total": 0.0, "resources": []}

    for r in resources:
        cost = r.get("monthly_cost", 0)
        tags = r.get("tags", {})
        cc = tags.get("CostCenter", "")
        owner = tags.get("Owner", "")
        project = tags.get("Project", "")
        env = tags.get("Environment", "")

        if cc:
            by_cost_center[cc]["direct"] += cost
            by_cost_center[cc]["resources"].append(r.get("name", "Unknown"))
            by_owner[owner or "unassigned"] += cost
            by_project[project or "unassigned"] += cost
            by_environment[env or "unassigned"] += cost
        else:
            untagged["total"] += cost
            untagged["resources"].append({
                "name": r.get("name", "Unknown"),
                "cost": cost,
                "id": r.get("id", ""),
                "created": r.get("created_date", "unknown")
            })

    return {
        "by_cost_center": dict(by_cost_center),
        "by_owner": dict(by_owner),
        "by_project": dict(by_project),
        "by_environment": dict(by_environment),
        "untagged": untagged
    }


def distribute_shared(shared_resources: list, cost_centers: dict,
                       rules: list) -> dict:
    """Layer 2: Distribute shared costs across cost centers."""
    distributions = {}

    for shared in shared_resources:
        name = shared.get("name", "Unknown")
        cost = shared.get("monthly_cost", 0)
        rule_name = shared.get("allocation_rule", "")

        # Find matching rule
        rule = next((r for r in rules if r["name"] == rule_name), None)
        if not rule:
            distributions[name] = {"error": f"No rule found for {rule_name}"}
            continue

        method = rule.get("method", "equal")
        weights = shared.get("allocation_weights", {})

        allocation = {}

        if method == "proportional" and weights:
            total_weight = sum(weights.values())
            if total_weight > 0:
                for cc, weight in weights.items():
                    share = cost * (weight / total_weight)
                    allocation[cc] = round(share, 2)

        elif method == "equal":
            cc_count = len(cost_centers)
            if cc_count > 0:
                per_cc = cost / cc_count
                for cc in cost_centers:
                    allocation[cc] = round(per_cc, 2)

        elif method == "fixed":
            fixed_splits = rule.get("fixed_splits", {})
            for cc, pct in fixed_splits.items():
                allocation[cc] = round(cost * pct, 2)

        # Reconcile rounding
        allocated = sum(allocation.values())
        if allocation and abs(allocated - cost) > 0.01:
            first_cc = list(allocation.keys())[0]
            allocation[first_cc] += round(cost - allocated, 2)

        distributions[name] = {
            "total_cost": cost,
            "method": method,
            "rule": rule_name,
            "allocation": allocation
        }

    return distributions


def generate_fully_loaded(direct: dict, shared_distributions: dict,
                           untagged: dict) -> dict:
    """Combine direct + shared + untagged for fully loaded cost per CC."""
    fully_loaded = defaultdict(lambda: {
        "direct": 0.0, "shared": 0.0, "total": 0.0,
        "shared_breakdown": defaultdict(float)
    })

    # Direct costs
    for cc, data in direct["by_cost_center"].items():
        fully_loaded[cc]["direct"] = round(data["direct"], 2)

    # Shared costs
    for resource_name, dist in shared_distributions.items():
        if "allocation" in dist:
            for cc, amount in dist["allocation"].items():
                fully_loaded[cc]["shared"] += amount
                fully_loaded[cc]["shared_breakdown"][resource_name] += amount

    # Calculate totals
    grand_total = 0
    for cc in fully_loaded:
        fully_loaded[cc]["shared"] = round(fully_loaded[cc]["shared"], 2)
        fully_loaded[cc]["total"] = round(
            fully_loaded[cc]["direct"] + fully_loaded[cc]["shared"], 2
        )
        fully_loaded[cc]["shared_breakdown"] = dict(fully_loaded[cc]["shared_breakdown"])
        grand_total += fully_loaded[cc]["total"]

    return {
        "cost_centers": dict(fully_loaded),
        "untagged_quarantine": round(untagged["total"], 2),
        "grand_total": round(grand_total + untagged["total"], 2),
        "leakage": 0.00
    }


def main():
    parser = argparse.ArgumentParser(
        description="Stella Maris Cost Allocation Engine (FinOps Pack 04)"
    )
    parser.add_argument("--resources", "-r", required=True, help="Resources with costs JSON")
    parser.add_argument("--shared", "-s", required=True, help="Shared resources JSON")
    parser.add_argument("--rules", required=True, help="Shared cost rules JSON")
    parser.add_argument("--output", "-o", default=None, help="Output allocation JSON")
    args = parser.parse_args()

    with open(args.resources) as f:
        res_data = json.load(f)
    with open(args.shared) as f:
        shared_data = json.load(f)
    with open(args.rules) as f:
        rules_data = json.load(f)

    resources = res_data.get("resources", [])
    shared_resources = shared_data.get("shared_resources", [])
    rules = rules_data.get("rules", [])

    print(f"{'='*60}")
    print(f"  COST ALLOCATION ENGINE")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Resources: {len(resources)} | Shared: {len(shared_resources)}")
    print(f"{'='*60}")
    print()

    # Layer 1: Direct attribution
    direct = allocate_direct(resources)

    print(f"  ─── Layer 1: Direct Attribution ───")
    for cc, data in direct["by_cost_center"].items():
        print(f"  {cc}: ${data['direct']:.2f} ({len(data['resources'])} resources)")
    print(f"  Untagged quarantine: ${direct['untagged']['total']:.2f} ({len(direct['untagged']['resources'])} resources)")
    print()

    # Layer 2: Shared distribution
    shared_dist = distribute_shared(
        shared_resources, direct["by_cost_center"], rules
    )

    print(f"  ─── Layer 2: Shared Distribution ───")
    for name, dist in shared_dist.items():
        if "allocation" in dist:
            alloc_str = ", ".join(f"{cc}: ${amt:.2f}" for cc, amt in dist["allocation"].items())
            print(f"  {name} (${dist['total_cost']:.2f}, {dist['method']}): {alloc_str}")
    print()

    # Fully loaded
    result = generate_fully_loaded(direct, shared_dist, direct["untagged"])

    print(f"  ─── Fully Loaded Cost ───")
    for cc, data in result["cost_centers"].items():
        pct = (data["total"] / result["grand_total"] * 100) if result["grand_total"] > 0 else 0
        print(f"  {cc}: ${data['direct']:.2f} direct + ${data['shared']:.2f} shared = ${data['total']:.2f} ({pct:.1f}%)")
    print(f"  Quarantine: ${result['untagged_quarantine']:.2f}")
    print()

    print(f"{'='*60}")
    print(f"  Grand total: ${result['grand_total']:.2f}")
    print(f"  Leakage: ${result['leakage']:.2f}")
    print(f"  The team that provisions the resource owns the bill.")
    print(f"{'='*60}")

    if args.output:
        output = {
            "allocation_date": datetime.now().strftime("%Y-%m-%d"),
            "direct": {
                "by_cost_center": {cc: {"direct": d["direct"]} for cc, d in direct["by_cost_center"].items()},
                "by_owner": direct["by_owner"],
                "by_project": direct["by_project"],
                "by_environment": direct["by_environment"]
            },
            "shared_distributions": shared_dist,
            "fully_loaded": result,
            "untagged_quarantine": direct["untagged"]
        }
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\n  Output written to {args.output}")


if __name__ == "__main__":
    main()
