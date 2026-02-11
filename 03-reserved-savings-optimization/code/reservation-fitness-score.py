#!/usr/bin/env python3
"""
Reservation Fitness Score — Stella Maris Governance
FinOps Pack 03

Scores workloads on reservation fitness across 5 factors:
  - Utilization Stability (30%)
  - Runtime Hours (25%)
  - Workload Lifecycle (20%)
  - Environment (15%)
  - Criticality (10%)

Score > 70: Reserve (1-year or 3-year RI)
Score 40-69: Savings Plan
Score < 40: Remain on-demand

Author: Robert Myers, MBA | Stella Maris Governance
"""

import json
import sys
import argparse
from datetime import datetime, date
import statistics


# Factor weights
WEIGHTS = {
    "utilization_stability": 0.30,
    "runtime_hours": 0.25,
    "workload_lifecycle": 0.20,
    "environment": 0.15,
    "criticality": 0.10
}

# Environment scoring (from Pack 01 tags)
ENVIRONMENT_SCORES = {
    "production": 100,
    "staging": 60,
    "development": 30,
    "test": 20,
    "sandbox": 10
}

# Criticality scoring (from Pack 01 tags)
CRITICALITY_SCORES = {
    "critical": 100,
    "high": 80,
    "medium": 60,
    "low": 30
}


def score_utilization_stability(daily_utilization: list) -> dict:
    """Score based on consistency of utilization over 30 days.

    Low variance = high score. A resource that runs at 80% every day
    is a better reservation candidate than one that bounces 20-95%.
    """
    if not daily_utilization or len(daily_utilization) < 7:
        return {"score": 0, "reason": "Insufficient data (need 7+ days)"}

    avg = statistics.mean(daily_utilization)
    stdev = statistics.stdev(daily_utilization) if len(daily_utilization) > 1 else 0

    # Coefficient of variation — lower is more stable
    cv = (stdev / avg * 100) if avg > 0 else 100

    if cv < 10:
        raw = 100
    elif cv < 20:
        raw = 85
    elif cv < 30:
        raw = 70
    elif cv < 50:
        raw = 50
    else:
        raw = 25

    weighted = round(raw * WEIGHTS["utilization_stability"])

    return {
        "raw_score": raw,
        "weighted_score": weighted,
        "max_weighted": round(100 * WEIGHTS["utilization_stability"]),
        "avg_utilization": round(avg, 1),
        "stdev": round(stdev, 1),
        "cv_percent": round(cv, 1),
        "data_points": len(daily_utilization),
        "reason": f"CV={cv:.1f}% ({'stable' if cv < 20 else 'moderate' if cv < 40 else 'volatile'})"
    }


def score_runtime_hours(hours_per_month: float, total_hours: float = 730) -> dict:
    """Score based on percentage of hours resource runs per month.

    730 hours = full month. A resource running 24/7 scores 100.
    A resource running business hours only (8×22=176) scores ~24.
    """
    pct = min((hours_per_month / total_hours) * 100, 100)

    if pct >= 95:
        raw = 100
    elif pct >= 80:
        raw = 85
    elif pct >= 60:
        raw = 65
    elif pct >= 40:
        raw = 40
    else:
        raw = 20

    weighted = round(raw * WEIGHTS["runtime_hours"])

    return {
        "raw_score": raw,
        "weighted_score": weighted,
        "max_weighted": round(100 * WEIGHTS["runtime_hours"]),
        "hours_per_month": round(hours_per_month),
        "runtime_pct": round(pct, 1),
        "reason": f"{pct:.0f}% runtime ({'24/7' if pct >= 95 else 'business hours' if pct < 50 else 'extended hours'})"
    }


def score_workload_lifecycle(expiry_date: str = None, created_date: str = None,
                              review_date: str = None, term_months: int = 12) -> dict:
    """Score based on expected remaining workload lifetime.

    A workload expected to run beyond the RI term scores high.
    A workload with an expiry date before the RI term ends scores low.
    """
    today = date.today()

    if expiry_date:
        try:
            expiry = date.fromisoformat(expiry_date)
            remaining_months = (expiry.year - today.year) * 12 + (expiry.month - today.month)

            if remaining_months > term_months * 1.5:
                raw = 100
            elif remaining_months > term_months:
                raw = 80
            elif remaining_months > term_months * 0.75:
                raw = 50
            else:
                raw = 10  # Expiry before RI term ends — bad bet
        except ValueError:
            raw = 60  # Unparseable date
            remaining_months = "unknown"
    else:
        # No expiry = assumed long-lived (production default)
        raw = 90
        remaining_months = "none_set"

    weighted = round(raw * WEIGHTS["workload_lifecycle"])

    return {
        "raw_score": raw,
        "weighted_score": weighted,
        "max_weighted": round(100 * WEIGHTS["workload_lifecycle"]),
        "expiry_date": expiry_date or "not set",
        "remaining_months": remaining_months,
        "term_months": term_months,
        "reason": f"{'No expiry — assumed long-lived' if not expiry_date else f'{remaining_months} months remaining vs {term_months}-month term'}"
    }


def score_environment(env: str) -> dict:
    """Score based on environment tag. Production = high fitness."""
    env_lower = env.lower() if env else "unknown"
    raw = ENVIRONMENT_SCORES.get(env_lower, 40)
    weighted = round(raw * WEIGHTS["environment"])

    return {
        "raw_score": raw,
        "weighted_score": weighted,
        "max_weighted": round(100 * WEIGHTS["environment"]),
        "environment": env_lower,
        "reason": f"{'Production — commitment justified' if env_lower == 'production' else f'{env_lower} — reduced commitment fitness'}"
    }


def score_criticality(crit: str) -> dict:
    """Score based on criticality tag. Critical = justified commitment."""
    crit_lower = crit.lower() if crit else "medium"
    raw = CRITICALITY_SCORES.get(crit_lower, 50)
    weighted = round(raw * WEIGHTS["criticality"])

    return {
        "raw_score": raw,
        "weighted_score": weighted,
        "max_weighted": round(100 * WEIGHTS["criticality"]),
        "criticality": crit_lower,
        "reason": f"{crit_lower} criticality"
    }


def calculate_fitness(workload: dict) -> dict:
    """Calculate composite reservation fitness score."""
    tags = workload.get("tags", {})

    factors = {
        "utilization_stability": score_utilization_stability(
            workload.get("daily_utilization", [])
        ),
        "runtime_hours": score_runtime_hours(
            workload.get("hours_per_month", 730)
        ),
        "workload_lifecycle": score_workload_lifecycle(
            expiry_date=tags.get("ExpiryDate"),
            created_date=tags.get("CreatedDate"),
            term_months=workload.get("term_months", 12)
        ),
        "environment": score_environment(
            tags.get("Environment", "unknown")
        ),
        "criticality": score_criticality(
            tags.get("Criticality", "medium")
        )
    }

    total = sum(f["weighted_score"] for f in factors.values())
    max_possible = sum(f["max_weighted"] for f in factors.values())

    # Recommendation
    if total >= 70:
        recommendation = "RESERVE"
        rec_detail = "1-year Reserved Instance recommended. Proceed to break-even analysis."
    elif total >= 40:
        recommendation = "SAVINGS_PLAN"
        rec_detail = "Savings Plan recommended. Workload stability insufficient for RI lock-in."
    else:
        recommendation = "ON_DEMAND"
        rec_detail = "Remain on-demand. Commitment risk exceeds discount benefit."

    return {
        "resource": workload.get("name", "Unknown"),
        "resource_id": workload.get("id", ""),
        "resource_type": workload.get("type", ""),
        "tags": tags,
        "factors": factors,
        "fitness_score": total,
        "max_score": max_possible,
        "recommendation": recommendation,
        "recommendation_detail": rec_detail,
        "assessed_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    }


def main():
    parser = argparse.ArgumentParser(
        description="Stella Maris Reservation Fitness Score (FinOps Pack 03)"
    )
    parser.add_argument("--workloads", "-w", required=True, help="Workloads JSON file")
    parser.add_argument("--output", "-o", default=None, help="Output results JSON")
    args = parser.parse_args()

    with open(args.workloads) as f:
        data = json.load(f)
    workloads = data.get("workloads", [])

    print(f"{'='*60}")
    print(f"  RESERVATION FITNESS SCORING")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Candidates: {len(workloads)}")
    print(f"{'='*60}")
    print()

    results = []
    for wl in workloads:
        result = calculate_fitness(wl)
        results.append(result)

        icon = "🟢" if result["recommendation"] == "RESERVE" else "🟡" if result["recommendation"] == "SAVINGS_PLAN" else "🔴"
        print(f"  {icon} {result['resource']} [{result['resource_type']}]")
        print(f"      Fitness Score: {result['fitness_score']}/{result['max_score']}")
        print(f"      Recommendation: {result['recommendation']}")

        for fname, fdata in result["factors"].items():
            label = fname.replace("_", " ").title()
            print(f"        {label}: {fdata['weighted_score']}/{fdata['max_weighted']} — {fdata['reason']}")
        print()

    # Summary
    reserves = [r for r in results if r["recommendation"] == "RESERVE"]
    savings = [r for r in results if r["recommendation"] == "SAVINGS_PLAN"]
    ondemand = [r for r in results if r["recommendation"] == "ON_DEMAND"]

    print(f"{'='*60}")
    print(f"  Reserve: {len(reserves)} | Savings Plan: {len(savings)} | On-Demand: {len(ondemand)}")
    print(f"  Don't pay rack rate on predictable workloads.")
    print(f"{'='*60}")

    if args.output:
        with open(args.output, 'w') as f:
            json.dump({"results": results, "scan_date": str(date.today())}, f, indent=2)
        print(f"\n  Results written to {args.output}")


if __name__ == "__main__":
    main()
