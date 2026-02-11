# Stella Maris Governance — FinOps Packs

> **The Duty of Fiscal Stewardship:** Every dollar spent on cloud infrastructure is a dollar entrusted. Governance is not just security — it is the discipline of ensuring that what you spend, you can justify, trace, and optimize. Waste is a governance failure.

[![Pillar](https://img.shields.io/badge/pillar-FinOps-8957e5?style=flat-square)]()
[![Packs](https://img.shields.io/badge/packs-5-ff6b35?style=flat-square)]()
[![Controls](https://img.shields.io/badge/Expected_vs_Observed-50_controls-36b37e?style=flat-square)]()

---

## Pillar Overview

The FinOps pillar governs cloud financial operations — the intersection of cost management, resource optimization, and organizational accountability. In the same way the Identity pillar governs who has access and the Supply Chain pillar governs who you trust, the FinOps pillar governs what you spend and whether that spending is justified.

This is not a cost-cutting exercise. This is a governance exercise. Cost optimization without governance is a one-time project. Cost governance is a continuous discipline — the same Expected vs. Observed rigor applied to dollars as to controls.

---

## The Three Duties

| Duty | What It Means | How This Pillar Delivers |
|------|--------------|-------------------------|
| **Duty of Trustworthiness** | Every claim about cloud spend is backed by evidence | Tagging policy enforces traceability. Anomaly detection proves monitoring. |
| **Duty of Fiscal Stewardship** | Every dollar is justified, traceable, and optimized | Chargeback proves accountability. Waste elimination proves discipline. |
| **Duty of Operational Readiness** | Cloud financial governance survives personnel changes | Tagging, automation, and dashboards ensure continuity. |

---

## Pack Index

| # | Pack | Controls | Status |
|---|------|----------|--------|
| 01 | [Cost Governance & Tagging Policy](01-cost-governance-tagging/) | 10 | 🔧 Building |
| 02 | [Anomaly Detection & Cost Alerting](02-anomaly-detection-alerting/) | 10 | Planned |
| 03 | [Reserved Instance & Savings Plan Optimization](03-reserved-savings-optimization/) | 10 | Planned |
| 04 | [Chargeback & Showback](04-chargeback-showback/) | 10 | Planned |
| 05 | [Waste Elimination & Right-Sizing](05-waste-elimination-rightsizing/) | 10 | Planned |

---

## How the Packs Connect
```
Pack 01 (Tagging) ──────► Foundation: every resource tagged = every cost traceable
        │
        ├──► Pack 02 (Anomaly Detection): tagged costs enable category-level alerting
        │
        ├──► Pack 03 (Reservations): tagged workloads inform commitment decisions
        │
        ├──► Pack 04 (Chargeback): tags assign costs to teams/projects/owners
        │
        └──► Pack 05 (Waste): tagged orphans are identifiable and attributable
```

Pack 01 is the foundation. Without tagging, you cannot trace costs, detect anomalies by category, allocate charges, or attribute waste. Every pack depends on the tagging discipline established in Pack 01.

---

## Cross-Pillar Integration

| Pillar | Integration Point |
|--------|------------------|
| **Identity** | Service principal cost attribution. CIEM over-permissioned resources may indicate over-provisioned (wasteful) resources. |
| **Supply Chain** | Vendor cost tracking. Pack 01 burn rate analysis feeds FinOps anomaly detection. SLA credits tracked. |
| **Cloud Security** | Security tool licensing costs. Defender for Cloud tier optimization. Key Vault transaction costs. |

---

## Prerequisites

| Requirement | Detail |
|-------------|--------|
| Azure subscription(s) | At least one Azure subscription with Cost Management enabled |
| Cost Management + Billing access | Reader role on billing account or Cost Management Reader on subscriptions |
| Azure Policy | Contributor on subscriptions for tag enforcement policies |
| Azure Advisor | Access for right-sizing and reservation recommendations |

---

<div align="center">

**© 2026 Stella Maris Governance LLC**

*The work speaks for itself. Stella Maris — the one light that does not drift.*

</div>
