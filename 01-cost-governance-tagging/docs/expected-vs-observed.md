# The Law of Evidence: Expected vs. Observed

## Cost Governance & Tagging Policy

> **Assessment Date:** 2026-02-12 [SAMPLE — replace with your assessment date]
> **Environment:** Stella Maris Lab — Azure Subscriptions + Azure Policy [SAMPLE]
> **Assessor:** Robert Myers, MBA | SailPoint ISL, Security+, CCSK, CC
> **Pack Version:** 1.0.0
> **Status:** 8/10 controls confirmed | 2 partial | 0 failed

---

## Summary

| Status | Count | Percentage |
|--------|-------|------------|
| Pass | 8 | 80% |
| Partial | 2 | 20% |
| Fail | 0 | 0% |

---

## Assessment Detail

### 1 — Tag Taxonomy Defined and Approved

| Field | Detail |
|-------|--------|
| **Expected State** | Standard tag taxonomy documented with required tags (enforced via deny) and recommended tags (enforced via audit). Naming conventions, allowed values, and format rules defined. Approved by engineering and finance stakeholders. |
| **Observed State** | Tag taxonomy **defined and approved.** **4 required tags:** `Owner` (individual or team), `Environment` (5 allowed values: production, staging, development, sandbox, test), `CostCenter` (CC-XXXX format), `Project` (workload name). **6 recommended tags:** `Criticality`, `DataClassification`, `CreatedDate`, `ReviewDate`, `ExpiryDate`, `ManagedBy`. Naming convention: camelCase keys, no spaces, ISO 8601 dates, lowercase environment values. Taxonomy reviewed with engineering (tag feasibility), finance (cost center mapping), and security (data classification alignment). |
| **Evidence** | Taxonomy document v1.0 |
| **FinOps Foundation** | Cost Allocation: Metadata and Hierarchy |
| **Status** | **Pass** |

---

### 2 — Azure Policies Deployed for Tag Enforcement

| Field | Detail |
|-------|--------|
| **Expected State** | 4 Azure Policies deployed: (1) Deny resource creation without required tags, (2) Audit resources missing recommended tags, (3) Inherit tags from resource group to child resources, (4) Restrict Environment tag to allowed values. |
| **Observed State** | **4 Azure Policies deployed** across 2 subscriptions (Lab-Production, Lab-Development): **Policy 1 — Require Tags (Deny):** Active. Denies creation of any resource missing `Owner`, `Environment`, `CostCenter`, or `Project`. Exclusions: Microsoft-managed resource groups (NetworkWatcherRG, AzureBackupRG, cloud-shell-storage). 14 deny events in first 7 days — all from engineers who hadn't read the announcement. All resolved within same day after tagging. **Policy 2 — Audit Recommended Tags:** Active. 47 resources flagged for missing recommended tags. Most common missing: `ReviewDate` (38 resources), `ExpiryDate` (35 resources). `Criticality` and `DataClassification` more commonly present (22 and 19 resources respectively). **Policy 3 — Tag Inheritance (Modify):** Active. Tested: created resource group with all 4 required tags, then created child resource without tags — inheritance applied correctly. Child resource received all 4 tags from parent within 15 minutes (Azure Policy evaluation cycle). **Policy 4 — Allowed Environment Values (Deny):** Active. Tested: attempted to create resource with `Environment: prod` — denied. Corrected to `Environment: production` — accepted. |
| **Evidence** | Screenshot #01, Azure Policy assignment list |
| **NIST 800-53** | CM-8 |
| **Status** | **Pass** |

---

### 3 — Tag Compliance Baseline Measured

| Field | Detail |
|-------|--------|
| **Expected State** | Initial tag compliance baseline measured across all subscriptions. Required tag compliance and recommended tag compliance reported as percentages. |
| **Observed State** | `tag-compliance-report.py` **executed.** Baseline measured across 2 subscriptions, **127 taggable resources.** **Required tag compliance:** `Owner`: 119/127 (93.7%). `Environment`: 124/127 (97.6%). `CostCenter`: 108/127 (85.0%). `Project`: 115/127 (90.6%). **Aggregate required tag compliance: 91.7%** (466 of 508 tag slots filled). 8 resources missing `Owner` — all in Lab-Development, provisioned before policy deployment. 19 resources missing `CostCenter` — engineering team requested finance provide updated cost center mapping, resolved 12 within first week. **Recommended tag compliance:** `Criticality`: 72/127 (56.7%). `DataClassification`: 65/127 (51.2%). `CreatedDate`: 89/127 (70.1%). `ReviewDate`: 42/127 (33.1%). `ExpiryDate`: 38/127 (29.9%). `ManagedBy`: 91/127 (71.7%). **Aggregate recommended tag compliance: 52.1%.** |
| **Evidence** | `tag-compliance-report.py` output, Screenshot #02 |
| **FinOps Foundation** | Data Analysis: Reporting and Analytics |
| **Status** | **Pass** |

---

### 4 — Deny Policy Preventing Non-Compliant Resource Creation

| Field | Detail |
|-------|--------|
| **Expected State** | Azure Policy deny effect actively prevents creation of resources without required tags. Every blocked creation logged. Zero non-compliant new resources after policy activation. |
| **Observed State** | Deny policy **active and enforced.** 30-day results: **14 deny events** in first 7 days (engineers learning new process). **2 deny events** in days 8-14. **0 deny events** in days 15-30. All denials resolved same day — engineers added tags and re-submitted. **Zero new non-compliant resources** created after day 14. The deny policy is working as designed: it creates a gate that forces compliance at point of creation. The 14 denials in week 1 were the learning curve. The zero denials in weeks 3-4 prove adoption. |
| **Evidence** | Screenshot #03, Azure Activity Log filtered to policy deny events |
| **NIST 800-53** | CM-8 |
| **Status** | **Pass** |

---

### 5 — Tag Inheritance Operational

| Field | Detail |
|-------|--------|
| **Expected State** | Azure Policy modify effect inherits required tags from resource group to child resources. Child resources created without tags automatically receive parent resource group tags. |
| **Observed State** | Tag inheritance **operational.** Policy evaluation cycle: approximately 15 minutes (standard Azure Policy compliance scan). Tested with 3 scenarios: (1) **New resource in tagged resource group:** Child resource created without tags → all 4 required tags inherited from RG within 15 minutes. Verified. (2) **Resource group tag updated:** RG `Owner` changed from `robert.myers` to `platform-team` → child resources updated on next evaluation cycle. Verified. (3) **Child resource has own tag:** Child resource created with `Owner: dev-team` in RG with `Owner: platform-team` → child resource retains its own tag (no overwrite). Correct behavior — explicit tags are not overridden. **Finding:** Inheritance only applies to required tags configured in the policy. Recommended tags are not inherited. This is by design — recommended tags are resource-specific (e.g., `ExpiryDate` varies per resource). |
| **Evidence** | Tag inheritance test log |
| **NIST 800-53** | CM-8 |
| **Status** | **Pass** |

---

### 6 — Cost Management Group-by-Tag Validated

| Field | Detail |
|-------|--------|
| **Expected State** | Azure Cost Management can group and filter costs by required tags: Owner, Environment, CostCenter, Project. Cost breakdown by tag produces actionable financial data. |
| **Observed State** | Cost Management group-by-tag **validated** for all 4 required tags: **By Environment:** Production: $2,847/month (62%). Development: $1,124/month (24%). Sandbox: $438/month (10%). Test: $187/month (4%). Untagged: $0 (0% — deny policy effective). **By CostCenter:** CC-1001 (Platform): $2,156/month. CC-2050 (Security): $1,412/month. CC-3010 (Data): $890/month. Unallocated: $138/month (resources with missing CostCenter from pre-policy). **By Owner (top 5):** robert.myers: $1,847. platform-team: $1,234. security-team: $892. data-team: $467. dev-team: $156. **By Project:** stella-maris: $1,456. customer-portal: $1,123. data-pipeline: $890. identity-lab: $467. untagged-backfill: $138 (tagged for tracking but awaiting project assignment). Cost data is **actionable.** Finance can see exactly where money goes. Engineering can see their team's spend. Anomalies by tag category will feed Pack 02. |
| **Evidence** | Screenshot #04, Cost Management export |
| **FinOps Foundation** | Cost Allocation, Data Analysis |
| **Status** | **Pass** |

---

### 7 — Tag Hygiene Scan Executed

| Field | Detail |
|-------|--------|
| **Expected State** | Quarterly tag hygiene scan identifies orphan tags: invalid owners (people who left), defunct projects, invalid cost centers, stale review dates. |
| **Observed State** | `tag-hygiene-scan.py` **executed.** Scan results across 127 resources: **Owner validation:** 119 tagged resources checked against Entra ID directory. 2 resources owned by `sarah.chen` — user left organization Jan 2026. **Orphan owner finding.** Resources reassigned to `platform-team` within 24 hours of finding. **Project validation:** 115 tagged resources checked against active project list. All projects valid. No defunct projects found (environment is new — this will become more relevant over time). **CostCenter validation:** 108 tagged resources checked against finance cost center list. All cost centers valid. **ReviewDate validation:** 42 resources with ReviewDate tag. 3 resources past review date (review overdue by 15-30 days). Owners notified. **ExpiryDate validation:** 38 resources with ExpiryDate tag. 1 resource past expiry date — sandbox VM expired Feb 1, still running. Owner notified for decommission. |
| **Evidence** | `tag-hygiene-scan.py` output, Screenshot #05 |
| **FinOps Foundation** | Cost Allocation |
| **Status** | **Pass** |

---

### 8 — Weekly Compliance Report Configured

| Field | Detail |
|-------|--------|
| **Expected State** | Automated weekly report showing tag compliance trends: required compliance %, recommended compliance %, deny events, new findings. Report distributed to engineering and finance stakeholders. |
| **Observed State** | Weekly report **configured** and first 4 reports generated. **Week 1:** Required 87.2%, Recommended 41.3%, Deny events: 14. **Week 2:** Required 89.5%, Recommended 45.8%, Deny events: 2. **Week 3:** Required 91.0%, Recommended 49.2%, Deny events: 0. **Week 4:** Required 91.7%, Recommended 52.1%, Deny events: 0. **Trend: improving.** Required compliance approaching 95% target. Recommended compliance growing at ~3% per week as engineers adopt additional tags. Deny events dropped to zero by week 3 — engineers have adopted the tagging workflow. Report distributed to: Engineering Lead, Finance, Risk Owner (R. Myers). |
| **Evidence** | Weekly report archive |
| **FinOps Foundation** | Data Analysis: Reporting and Analytics |
| **Status** | **Pass** |

---

### 9 — Pre-Policy Resource Backfill In Progress

| Field | Detail |
|-------|--------|
| **Expected State** | Resources created before policy deployment are tagged retroactively. Backfill campaign targets 99% required tag compliance within 90 days. |
| **Observed State** | Backfill campaign **in progress.** 127 resources total. Pre-policy resources without required tags: `Owner` missing: 8 resources → 6 backfilled, 2 remaining (investigating ownership). `CostCenter` missing: 19 resources → 12 backfilled after finance mapping, 7 remaining (cost center assignment pending finance). `Project` missing: 12 resources → 9 backfilled, 3 remaining (no clear project — candidates for decommission). **Current required compliance: 91.7%.** Target: 95% within 30 days, 99% within 90 days. Backfill rate: 27 of 39 gaps remediated (69%) in 30 days. Remaining 12 gaps are the harder ones — ownership unclear, cost center unmapped, or possibly orphaned resources. |
| **Finding** | 3 resources with no clear project assignment are candidates for decommission. They may be remnants of a completed POC. Investigation underway. If decommissioned, that's cost savings from the tagging exercise itself. |
| **Status** | **Partial** — 91.7% required compliance vs 95% 30-day target; backfill ongoing |

---

### 10 — Tagging Policy Exception Process Documented

| Field | Detail |
|-------|--------|
| **Expected State** | Documented exception process for resources that cannot be tagged (Microsoft-managed resource groups, third-party limitations). Exceptions are justified, time-limited, and tracked. |
| **Observed State** | Exception process **documented.** Current exceptions: **3 Microsoft-managed resource groups** excluded from deny policy: NetworkWatcherRG, AzureBackupRG, cloud-shell-storage-westus. These are managed by Azure and cannot be tagged by users. Exclusion is permanent and justified. **2 third-party resources** identified that don't support all tag keys (tag key length limitation on one legacy resource type). Workaround documented: shortened tag key applied, cross-reference maintained in tag registry. **Exception process flow:** Request → justification → Risk Owner approval → time-limited (90 days max) → review at expiry → renew or remediate. **No user-requested exceptions** to date. The deny policy has not created a need for exceptions beyond infrastructure limitations. |
| **Finding** | Exception process exists but has not been tested with a user-requested exception. Will be validated when first exception request is received. |
| **Status** | **Partial** — process documented but not exercised with a user-requested exception |

---

## Remediation Tracker

| # | Control | Finding | Owner | Remediation | Target Date | Status |
|---|---------|---------|-------|-------------|-------------|--------|
| 7 | Tag hygiene | 2 resources owned by departed employee found, 1 expired sandbox still running | R. Myers | Reassign orphaned resources, decommission expired sandbox | 2026-02-28 | In Progress |
| 9 | Backfill | 12 resources still missing required tags (ownership unclear, cost center unmapped) | R. Myers | Complete backfill or decommission unattributable resources | 2026-03-15 | Open |
| 10 | Exceptions | Exception process untested with user-requested exception | R. Myers | Time-based — will validate on first request | When triggered | Open |

---

## Watchstander Notes

1. **The deny policy is the most important control in this pack.** It creates a gate at the point of resource creation. Every resource that enters the environment after the policy is deployed has required tags. No exceptions. No "I'll tag it later." The 14 denials in week 1 were the growing pains. The zero denials in weeks 3-4 prove that engineers adopted the discipline. The policy changed behavior because it was enforced, not suggested.

2. **91.7% required compliance in 30 days is good. It's not done.** The remaining 8.3% is the hardest part — resources with no clear owner, no cost center mapping, no project justification. These are the resources most likely to be waste. The tagging exercise doesn't just create visibility. It surfaces the questions that should have been asked when the resources were created: who owns this? Why does it exist? Should it still be running? Three resources with no project are candidates for decommission. If they're decommissioned, the tagging policy just paid for itself.

3. **The departed employee finding proves tag hygiene value.** Sarah Chen left in January. Two resources still tagged to her. Without the hygiene scan, those resources would have drifted — no owner, no accountability, no one to ask "should this still exist?" The scan found them in the first run. This will only become more valuable over time as team composition changes.

4. **Cost Management group-by-tag is the bridge between engineering and finance.** Finance asks "what are we spending on the customer portal?" Cost Management answers: $1,123/month. Finance asks "what's our development environment costing us?" Answer: $1,124/month — almost as much as production. That's a conversation starter. That's Pack 05 waste elimination's first lead. None of this is possible without tags. Tags are not an engineering exercise. They are a financial governance exercise that engineers implement.

5. **This pack is the foundation. Every other FinOps pack depends on it.** Anomaly detection (Pack 02) needs tags to know which category spiked. Reservations (Pack 03) need tags to know which workloads are committed. Chargeback (Pack 04) needs tags to allocate costs. Waste elimination (Pack 05) needs tags to attribute orphans. Without this pack, the FinOps pillar is blind. With it, every dollar is traceable.

---

*Assessment conducted by Robert Myers, MBA | SailPoint ISL, Security+, CCSK, CC*
*Stella Maris Governance — 2026*
