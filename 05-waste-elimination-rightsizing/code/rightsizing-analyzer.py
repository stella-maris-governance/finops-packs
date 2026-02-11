#!/usr/bin/env python3
"""
Right-Sizing Analyzer — Stella Maris Governance
FinOps Pack 05

Compares actual utilization (P95) against provisioned capacity
and recommends target SKU. Sizes for sustained peak, not average.

Author: Robert Myers, MBA | Stella Maris Governance
"""

import json
import argparse
from datetime import datetime


# Azure VM SKU reference (simplified)
VM_SKUS = {
    "B1s":    {"vcpu": 1, "memory_gb": 1, "monthly": 7.59},
    "B2s":    {"vcpu": 2, "memory_gb": 4, "monthly": 30.37},
    "B2ms":   {"vcpu": 2, "memory_gb": 8, "monthly": 60.74},
    "D2s_v5": {"vcpu": 2, "memory_gb": 8, "monthly": 89.00},
    "D4s_v5": {"vcpu": 4, "memory_gb": 16, "monthly": 178.00},
    "D8s_v5": {"vcpu": 8, "memory_gb": 32, "monthly": 356.00},
    "D2as_v5": {"vcpu": 2, "memory_gb": 8, "monthly": 79.00},
    "D4as_v5": {"vcpu": 4, "memory_gb": 16, "monthly": 158.00}
}


def analyze_vm(resource: dict) -> dict:
    """Analyze VM right-sizing based on P95 utilization."""
    metrics = resource.get("metrics", {})
    current_sku = resource.get("sku", "")
    current_info = VM_SKUS.get(current_sku, {})
    env = resource.get("tags", {}).get("Environment", "unknown")

    p95_cpu = metrics.get("p95_cpu_pct", 100)
    p95_mem = metrics.get("p95_memory_pct", 100)
    avg_cpu = metrics.get("avg_cpu_pct", 100)

    if not current_info:
        return {"resource": resource.get("name"), "status": "unknown_sku", "sku": current_sku}

    # Calculate required capacity at P95
    required_vcpu = current_info["vcpu"] * (p95_cpu / 100)
    required_mem = current_info["memory_gb"] * (p95_mem / 100)

    # Find smallest SKU that fits P95 with 20% headroom
    target_vcpu = required_vcpu * 1.2
    target_mem = required_mem * 1.2

    candidates = []
    for sku_name, sku_info in sorted(VM_SKUS.items(), key=lambda x: x[1]["monthly"]):
        if sku_info["vcpu"] >= target_vcpu and sku_info["memory_gb"] >= target_mem:
            candidates.append(sku_name)

    recommended = candidates[0] if candidates else current_sku
    rec_info = VM_SKUS.get(recommended, current_info)

    savings = current_info["monthly"] - rec_info["monthly"]

    return {
        "resource": resource.get("name", "Unknown"),
        "resource_id": resource.get("id", ""),
        "environment": env,
        "current_sku": current_sku,
        "current_cost": current_info["monthly"],
        "current_vcpu": current_info["vcpu"],
        "current_memory_gb": current_info["memory_gb"],
        "p95_cpu_pct": p95_cpu,
        "p95_memory_pct": p95_mem,
        "avg_cpu_pct": avg_cpu,
        "required_vcpu": round(required_vcpu, 1),
        "required_memory_gb": round(required_mem, 1),
        "recommended_sku": recommended,
        "recommended_cost": rec_info["monthly"],
        "monthly_savings": round(savings, 2),
        "annual_savings": round(savings * 12, 2),
        "recommendation": "rightsize" if recommended != current_sku else "no_change",
        "risk": "low" if env != "production" else "high",
        "notes": f"{'Production — requires change window and rollback plan' if env == 'production' else 'Non-production — safe to resize'}"
    }


def main():
    parser = argparse.ArgumentParser(
        description="Stella Maris Right-Sizing Analyzer (FinOps Pack 05)"
    )
    parser.add_argument("--resources", "-r", required=True, help="VM resources JSON")
    parser.add_argument("--output", "-o", default=None, help="Output JSON")
    args = parser.parse_args()

    with open(args.resources) as f:
        data = json.load(f)

    vms = [r for r in data.get("resources", [])
           if r.get("type") == "Microsoft.Compute/virtualMachines"]

    print(f"{'='*60}")
    print(f"  RIGHT-SIZING ANALYSIS (P95 Method)")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  VMs analyzed: {len(vms)}")
    print(f"{'='*60}")
    print()

    results = []
    total_savings = 0

    for vm in vms:
        result = analyze_vm(vm)
        results.append(result)

        if result["recommendation"] == "rightsize":
            icon = "📐"
            print(f"  {icon} {result['resource']} [{result['environment']}]")
            print(f"      Current: {result['current_sku']} ({result['current_vcpu']} vCPU, "
                  f"{result['current_memory_gb']} GB) — ${result['current_cost']}/mo")
            print(f"      P95: CPU {result['p95_cpu_pct']}%, Memory {result['p95_memory_pct']}%")
            print(f"      Recommended: {result['recommended_sku']} — ${result['recommended_cost']}/mo")
            print(f"      Savings: ${result['monthly_savings']}/mo (${result['annual_savings']}/yr)")
            print(f"      Risk: {result['risk']} — {result['notes']}")
            print()
            total_savings += result["monthly_savings"]
        else:
            print(f"  ✅ {result['resource']}: properly sized ({result['current_sku']}, "
                  f"P95 CPU {result['p95_cpu_pct']}%)")

    print()
    print(f"{'='*60}")
    print(f"  Right-sizing candidates: {sum(1 for r in results if r['recommendation'] == 'rightsize')}")
    print(f"  Monthly savings: ${total_savings:.2f}")
    print(f"  Size for P95, not average. Average hides peaks.")
    print(f"{'='*60}")

    if args.output:
        with open(args.output, 'w') as f:
            json.dump({"results": results}, f, indent=2)


if __name__ == "__main__":
    main()
