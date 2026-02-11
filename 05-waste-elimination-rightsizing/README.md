# Waste Elimination & Right-Sizing Pack

> Every idle resource is a silent invoice. A VM running at 3% CPU is not "available." It's burning money while doing nothing. A storage account with no consumers isn't "retained for safety." It's a forgotten liability. This pack finds every dollar that isn't earning its keep and forces a decision: justify it, shrink it, or kill it.

[![Controls](https://img.shields.io/badge/Expected_vs_Observed-10_controls-8957e5?style=flat-square)]()
[![Framework](https://img.shields.io/badge/framework-FinOps_Foundation_·_Azure_Cost_Management-ff6b35?style=flat-square)]()

---

## Start Here

| You Are | Read This First |
|---------|----------------|
| **Hiring Manager** | This README then [`expected-vs-observed.md`](docs/expected-vs-observed.md) — proves cost optimization is continuous, not a one-time exercise |
| **Consulting Client** | [`expected-vs-observed.md`](docs/expected-vs-observed.md) — how much are you spending on resources nobody uses? |
| **Auditor / GRC** | [`expected-vs-observed.md`](docs/expected-vs-observed.md) then [`control-mapping.md`](docs/control-mapping.md) — FinOps Foundation, NIST alignment |
| **CFO / Finance** | This README — proves every resource is justified or eliminated |
| **Engineer** | [`/code/`](code/) for waste scanner and [`waste-operations-runbook.md`](docs/waste-operations-runbook.md) |

---

## The Problem

Cloud waste is not a budgeting failure. It's an accumulation failure. Nobody provisions a VM intending to waste money. They provision it for a demo, a test, a migration, a proof of concept. The demo ends. The test passes. The migration completes. The proof of concept is approved. But the resource keeps running. The meter keeps ticking.

Over time, these forgotten resources accumulate like sediment. Each one is small — $30 here, $80 there — but collectively they represent 20-35% of cloud spend in a typical enterprise. That's not an estimate; that's the industry consensus from FinOps Foundation, Gartner, and every cloud cost optimization vendor.

The problem is compounded by over-provisioning. Engineers provision for peak, not average. A VM sized for a traffic spike that happens once a month runs at 3% CPU the other 29 days. The insurance premium against a rare spike costs 10× what right-sizing would cost.

This pack systematically identifies waste across 6 categories, forces a disposition on every finding, and tracks remediation to completion. Every idle resource gets a decision: justify, right-size, schedule, or decommission.

---

## What This Pack Delivers

| Capability | What It Does | How |
|-----------|-------------|-----|
| **Idle resource detection** | Find resources with zero or near-zero utilization | Azure Advisor + custom utilization scanning |
| **Right-sizing recommendations** | Identify over-provisioned resources that can be downsized | CPU, memory, IOPS analysis against actual usage |
| **Orphan resource detection** | Find resources with no parent or consumer | Disks without VMs, IPs without NICs, NICs without VMs |
| **Schedule optimization** | Identify resources running 24/7 that should run business hours | Environment tags + utilization patterns |
| **Aged resource review** | Find resources past their review or expiry date | Pack 01 tags: ReviewDate, ExpiryDate, CreatedDate |
| **Waste register and tracking** | Log every finding, disposition, and remediation | Central register with owner accountability |

---

## Six Categories of Cloud Waste

### Category 1 — Idle Resources

Resources running with zero or near-zero utilization for 14+ days.

| Resource Type | Idle Signal | Threshold |
|--------------|-------------|-----------|
| Virtual Machine | CPU avg < 5% for 14 days | Deallocate or right-size |
| App Service | Request count = 0 for 14 days | Scale to Free or decommission |
| SQL Database | DTU avg < 5% for 14 days | Scale down or decommission |
| Cosmos DB | RU consumption < 5% of provisioned for 14 days | Scale down or switch to serverless |

### Category 2 — Over-Provisioned Resources

Resources sized significantly above actual utilization.

| Resource Type | Signal | Recommendation |
|--------------|--------|---------------|
| VM: D4s_v5 running at 15% CPU | Provisioned for peak, running at base | Right-size to D2s_v5 (50% cost reduction) |
| SQL: S3 (100 DTU) using 12 DTU avg | Premium tier for standard workload | Downgrade to S1 (75% cost reduction) |
| Storage: Premium using < 500 IOPS | Premium for standard workload | Move to Standard (60% cost reduction) |

### Category 3 — Orphan Resources

Resources that have lost their parent or consumer.

| Orphan Type | How It Happens | Cost Impact |
|-------------|---------------|-------------|
| Managed disk without VM | VM deleted, disk retained | $5-100/month per disk |
| Public IP without NIC | NIC deleted, IP retained | $3.65/month per IP |
| NIC without VM | VM deleted, NIC retained | Minimal but governance gap |
| Network Security Group without NIC | Attachment removed | Minimal but governance gap |
| Snapshot older than 90 days | Created for migration, never cleaned | $1-50/month per snapshot |
| Empty resource group | Resources deleted, group remains | $0 but clutter and governance gap |

### Category 4 — Schedule Optimization

Resources running 24/7 that should follow a schedule.

| Environment | Expected Schedule | Waste If 24/7 |
|------------|------------------|---------------|
| Development | Business hours (8×5 = 40 hrs/week) | 76% of hours wasted |
| Test | Business hours or on-demand | 76% of hours wasted |
| Sandbox | On-demand only | Up to 100% wasted if idle |
| Staging | Business hours + deployment windows | 60-70% of hours wasted |

> **Watchstander Note:** Pack 02 already caught this. The weekend VM anomaly ($34.80) is a schedule optimization finding. This pack closes the loop: detect → decide → automate shutdown.

### Category 5 — Aged Resources

Resources past their intended lifecycle.

| Tag | Signal | Action |
|-----|--------|--------|
| `ExpiryDate` in the past | Resource should have been decommissioned | Decommission or extend with justification |
| `ReviewDate` in the past | Resource hasn't been reviewed on schedule | Review now or flag as unreviewed |
| `CreatedDate` > 12 months, no other lifecycle tags | Long-running resource with no governance | Add lifecycle tags or justify |

### Category 6 — Pricing Tier Waste

Resources on premium tiers without premium requirements.

| Signal | Example | Savings |
|--------|---------|---------|
| Premium storage with < 500 IOPS | Provisioned for expected load, actual load is standard | 60% |
| Premium App Service with < 1 instance | Premium for SSL, could use Standard with cert | 40-60% |
| Premium SQL with DTU headroom > 80% | Provisioned for spike that never came | 50-75% |

---

## Waste Disposition Framework

Every finding requires a disposition:

| Disposition | Meaning | Action | Timeline |
|------------|---------|--------|----------|
| **Decommission** | Resource has no business justification | Delete/deallocate | 7 days |
| **Right-size** | Resource is justified but over-provisioned | Resize to match actual utilization | 14 days |
| **Schedule** | Resource is justified but doesn't need 24/7 | Implement auto-shutdown schedule | 14 days |
| **Justify** | Resource appears wasteful but has valid reason | Document justification, set review date | 7 days |
| **Defer** | Cannot act now (dependency, change window) | Document reason, set action date | 30 days max |

> **Watchstander Note:** "Justify" is a legitimate disposition — not every low-utilization resource is waste. A disaster recovery VM running at 0% CPU is not idle. It's waiting. But the justification must be documented. If the answer to "why is this running?" is "I don't know" — that's decommission, not justify.

---

## Compliance Mapping

| Framework | Control ID | Control Name | Implementation |
|-----------|-----------|--------------|----------------|
| FinOps Foundation | Capability: Usage Optimization | Maximize value of every resource | 6 waste categories, disposition framework |
| FinOps Foundation | Capability: Workload Management | Right-size and schedule resources | Right-sizing, schedule optimization |
| NIST 800-53 | CM-8 | Information System Component Inventory | Resource inventory with justification |
| NIST 800-53 | SA-4 | Acquisition Process | Cost-justified resource procurement |

> Full mapping: [`docs/control-mapping.md`](docs/control-mapping.md)

---

## What's Included

### `code/`

| File | Description |
|------|-------------|
| `waste-scanner.py` | Python: scan all 6 waste categories with configurable thresholds |
| `rightsizing-analyzer.py` | Python: CPU/memory/IOPS analysis with SKU recommendations |
| `orphan-detector.py` | Python: find disks, IPs, NICs, NSGs without parents |
| `waste-register.json` | Central register: every finding, disposition, remediation |
| `schedule-recommendations.json` | Auto-shutdown schedules by environment |
| `deploy-waste-scanning.ps1` | PowerShell: deploy waste scanning configuration |

### `docs/`

| File | Description |
|------|-------------|
| [`expected-vs-observed.md`](docs/expected-vs-observed.md) | The Law of Evidence — 10 controls |
| [`waste-operations-runbook.md`](docs/waste-operations-runbook.md) | Full waste management SOP |
| [`control-mapping.md`](docs/control-mapping.md) | FinOps Foundation / NIST alignment |

### `screenshots/`

| # | What It Shows |
|---|--------------|
| 01 | Azure Advisor right-sizing recommendations |
| 02 | Waste scanner: idle resource detection output |
| 03 | Orphan detector: unattached disks and IPs |
| 04 | Right-sizing analysis: CPU utilization vs provisioned |
| 05 | Waste register: findings with dispositions |

---

## Related Packs

| Pack | Relationship |
|------|-------------|
| [Cost Governance & Tagging](../01-cost-governance-tagging/) | Tags (CreatedDate, ExpiryDate, ReviewDate, Environment) enable aged resource and schedule detection |
| [Anomaly Detection](../02-anomaly-detection-alerting/) | Waste-disposition anomalies feed this pack directly |
| [Reserved Instance Optimization](../03-reserved-savings-optimization/) | Under-utilized reservations feed waste analysis |
| [Chargeback & Showback](../04-chargeback-showback/) | Waste costs attributed to responsible owner for remediation |
| [Supply Chain Pack 07](../../supply-chain-scrm-packs/07-sla-governance/) | Vendor tool licensing waste (overpaid tiers) |

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-02-12 | Initial release |

---

<div align="center">

**© 2026 Stella Maris Governance LLC**

*The work speaks for itself. Stella Maris — the one light that does not drift.*

</div>
