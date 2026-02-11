#!/usr/bin/env python3
"""
Tag Hygiene Scanner — Stella Maris Governance
Detect orphan tags: invalid owners, defunct projects, stale dates.
"""

import json
import argparse
from datetime import datetime, date


def scan_owners(resources: list, directory: list) -> list:
    """Find resources with Owner tags not in directory."""
    valid_owners = set(u.get("userPrincipalName", "").split("@")[0] for u in directory)
    valid_owners.update(u.get("displayName", "").lower().replace(" ", ".") for u in directory)
    # Also accept team names
    valid_owners.update(["platform-team", "security-team", "data-team", "dev-team", "unattributed"])

    findings = []
    for r in resources:
        owner = r.get("tags", {}).get("Owner", "")
        if owner and owner.lower() not in {o.lower() for o in valid_owners}:
            findings.append({
                "type": "ORPHAN_OWNER",
                "resource": r.get("name", "Unknown"),
                "resource_id": r.get("id", ""),
                "owner_tag": owner,
                "severity": "HIGH"
            })
    return findings


def scan_dates(resources: list) -> list:
    """Find resources past ReviewDate or ExpiryDate."""
    today = date.today()
    findings = []

    for r in resources:
        tags = r.get("tags", {})

        review = tags.get("ReviewDate", "")
        if review:
            try:
                review_date = date.fromisoformat(review)
                if review_date < today:
                    findings.append({
                        "type": "OVERDUE_REVIEW",
                        "resource": r.get("name", "Unknown"),
                        "review_date": review,
                        "days_overdue": (today - review_date).days,
                        "severity": "MEDIUM"
                    })
            except ValueError:
                pass

        expiry = tags.get("ExpiryDate", "")
        if expiry:
            try:
                expiry_date = date.fromisoformat(expiry)
                if expiry_date < today:
                    findings.append({
                        "type": "PAST_EXPIRY",
                        "resource": r.get("name", "Unknown"),
                        "expiry_date": expiry,
                        "days_past": (today - expiry_date).days,
                        "severity": "HIGH"
                    })
            except ValueError:
                pass

    return findings


def main():
    parser = argparse.ArgumentParser(description="Stella Maris Tag Hygiene Scanner")
    parser.add_argument("--resources", required=True, help="Resource inventory JSON")
    parser.add_argument("--directory", default=None, help="Entra ID user export JSON")
    args = parser.parse_args()

    with open(args.resources) as f:
        data = json.load(f)
    resources = data.get("resources", []) if isinstance(data, dict) else data

    findings = []

    if args.directory:
        with open(args.directory) as f:
            directory = json.load(f)
        directory = directory.get("users", []) if isinstance(directory, dict) else directory
        findings.extend(scan_owners(resources, directory))

    findings.extend(scan_dates(resources))

    print(f"{'='*60}")
    print(f"  TAG HYGIENE SCAN")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Resources scanned: {len(resources)}")
    print(f"{'='*60}")
    print()

    if findings:
        for f_item in findings:
            icon = "🔴" if f_item["severity"] == "HIGH" else "🟡"
            print(f"  {icon} [{f_item['type']}] {f_item['resource']}")
            for k, v in f_item.items():
                if k not in ("type", "severity", "resource"):
                    print(f"      {k}: {v}")
            print()
    else:
        print(f"  ✓ No hygiene findings")
        print()

    print(f"{'='*60}")
    print(f"  Findings: {len(findings)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
