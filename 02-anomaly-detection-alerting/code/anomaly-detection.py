#!/usr/bin/env python3
"""
Cost Anomaly Detection — Stella Maris Governance
Statistical anomaly detection: 7-day rolling, day-over-day, weekend, new resource.
"""

import json
import sys
import argparse
from datetime import datetime, date, timedelta
from collections import defaultdict


def detect_rolling_average(daily_costs: list, threshold_pct: float = 30.0) -> list:
    """Detect days where cost exceeds 7-day rolling average by threshold."""
    findings = []
    if len(daily_costs) < 8:
        return findings

    for i in range(7, len(daily_costs)):
        window = daily_costs[i-7:i]
        avg = sum(d["cost"] for d in window) / 7
        current = daily_costs[i]

        if avg > 0 and current["cost"] > avg * (1 + threshold_pct / 100):
            deviation = ((current["cost"] - avg) / avg) * 100
            findings.append({
                "type": "ROLLING_AVERAGE_DEVIATION",
                "date": current["date"],
                "resource": current.get("resource", "Subscription"),
                "cost": round(current["cost"], 2),
                "seven_day_avg": round(avg, 2),
                "deviation_pct": round(deviation, 1),
                "threshold_pct": threshold_pct,
                "severity": "HIGH" if deviation > 100 else "WARNING"
            })
    return findings


def detect_day_over_day(daily_costs: list, threshold_pct: float = 50.0) -> list:
    """Detect day-over-day spikes exceeding threshold."""
    findings = []
    for i in range(1, len(daily_costs)):
        prev = daily_costs[i-1]["cost"]
        curr = daily_costs[i]["cost"]

        if prev > 0 and curr > prev * (1 + threshold_pct / 100):
            spike = ((curr - prev) / prev) * 100
            findings.append({
                "type": "DAY_OVER_DAY_SPIKE",
                "date": daily_costs[i]["date"],
                "resource": daily_costs[i].get("resource", "Subscription"),
                "cost": round(curr, 2),
                "previous_day": round(prev, 2),
                "spike_pct": round(spike, 1),
                "severity": "HIGH" if spike > 100 else "WARNING"
            })
    return findings


def detect_weekend(daily_costs: list, weekday_avg_threshold: float = 2.0) -> list:
    """Detect significant weekend cost on non-production resources."""
    findings = []
    weekday_costs = [d for d in daily_costs if date.fromisoformat(d["date"]).weekday() < 5]
    weekend_costs = [d for d in daily_costs if date.fromisoformat(d["date"]).weekday() >= 5]

    if not weekday_costs or not weekend_costs:
        return findings

    weekday_avg = sum(d["cost"] for d in weekday_costs) / len(weekday_costs)

    for d in weekend_costs:
        if weekday_avg > 0 and d["cost"] > weekday_avg * weekday_avg_threshold:
            findings.append({
                "type": "WEEKEND_ANOMALY",
                "date": d["date"],
                "resource": d.get("resource", "Subscription"),
                "weekend_cost": round(d["cost"], 2),
                "weekday_avg": round(weekday_avg, 2),
                "multiplier": round(d["cost"] / weekday_avg, 1),
                "severity": "WARNING"
            })
    return findings


def detect_new_resource(daily_costs: list, threshold_daily: float = 25.0, lookback_days: int = 7) -> list:
    """Detect new resources exceeding daily cost threshold."""
    findings = []
    today = date.today()
    cutoff = today - timedelta(days=lookback_days)

    for d in daily_costs:
        created = d.get("created_date", "")
        if created and date.fromisoformat(created) >= cutoff and d["cost"] > threshold_daily:
            findings.append({
                "type": "NEW_RESOURCE_COST",
                "date": d["date"],
                "resource": d.get("resource", "Unknown"),
                "daily_cost": round(d["cost"], 2),
                "created_date": created,
                "threshold": threshold_daily,
                "severity": "WARNING"
            })
    return findings


def main():
    parser = argparse.ArgumentParser(description="Stella Maris Cost Anomaly Detection")
    parser.add_argument("--costs", required=True, help="Path to daily cost data JSON")
    parser.add_argument("--rolling-threshold", type=float, default=30.0, help="7-day rolling deviation %")
    parser.add_argument("--dod-threshold", type=float, default=50.0, help="Day-over-day spike %")
    parser.add_argument("--output", default=None, help="Output findings JSON")
    args = parser.parse_args()

    with open(args.costs) as f:
        data = json.load(f)
    daily_costs = data.get("daily_costs", [])

    print(f"{'='*60}")
    print(f"  COST ANOMALY DETECTION")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Data points: {len(daily_costs)}")
    print(f"  Thresholds: rolling={args.rolling_threshold}%, DoD={args.dod_threshold}%")
    print(f"{'='*60}")
    print()

    all_findings = []

    scans = [
        ("7-Day Rolling Average", detect_rolling_average(daily_costs, args.rolling_threshold)),
        ("Day-over-Day Spike", detect_day_over_day(daily_costs, args.dod_threshold)),
        ("Weekend Anomaly", detect_weekend(daily_costs)),
        ("New Resource Cost", detect_new_resource(daily_costs))
    ]

    for scan_name, findings in scans:
        print(f"  ─── {scan_name} ───")
        if findings:
            for f_item in findings:
                icon = "🔴" if f_item["severity"] == "HIGH" else "🟡"
                print(f"  {icon} [{f_item['type']}] {f_item.get('resource', 'N/A')} — {f_item['date']}")
                for k, v in f_item.items():
                    if k not in ("type", "severity", "resource", "date"):
                        print(f"      {k}: {v}")
            all_findings.extend(findings)
        else:
            print(f"  ✓ No anomalies detected")
        print()

    print(f"{'='*60}")
    print(f"  Total findings: {len(all_findings)}")
    print(f"  The invoice is an autopsy. This is the vital sign monitor.")
    print(f"{'='*60}")

    if args.output:
        with open(args.output, 'w') as f:
            json.dump({"findings": all_findings, "scan_date": str(date.today())}, f, indent=2)


if __name__ == "__main__":
    main()
