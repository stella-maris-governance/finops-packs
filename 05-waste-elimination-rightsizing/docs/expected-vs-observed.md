# The Law of Evidence: Expected vs. Observed

## Waste Elimination & Right-Sizing

> **Assessment Date:** 2026-02-12 [SAMPLE — replace with your assessment date]
> **Environment:** Stella Maris Lab — Azure Advisor + Custom Scanning [SAMPLE]
> **Assessor:** Robert Myers, MBA | SailPoint ISL, Security+, CCSK, CC
> **Pack Version:** 1.0.0
> **Status:** 8/10 controls confirmed | 1 partial | 1 fail

---

## Summary

| Status | Count | Percentage |
|--------|-------|------------|
| Pass | 8 | 80% |
| Partial | 1 | 10% |
| Fail | 1 | 10% |

---

## Assessment Detail

### 1 — Azure Advisor Right-Sizing Recommendations Reviewed

| Field | Detail |
|-------|--------|
| **Expected State** | Azure Advisor right-sizing and shutdown recommendations reviewed for all subscriptions. Every recommendation evaluated and dispositioned. |
| **Observed State** | Azure Advisor reviewed across 2 subscriptions. **9 recommendations identified:** **Right-sizing (4):** (1) VM D2s_v5 (Lab-Development): avg CPU 8%, max CPU 22%. Advisor recommends B2s. **Accepted — right-size.** Projected savings: $47/month. (2) VM D4s_v5 (Lab-Production): avg CPU 34%, max CPU 71%. Advisor recommends D2s_v5. **Deferred — production workload, need change window.** Projected savings: $89/month. (3) SQL Database S2 (Lab-Development): avg DTU 6%, max DTU 18%. Advisor recommends S0. **Accepted — right-size.** Projected savings: $62/month. (4) App Service Plan P1v3 (Lab-Development): avg CPU 4%, 0 requests on weekends. Advisor recommends B1. **Accepted — right-size.** Projected savings: $94/month. **Shutdown (2):** (5) VM B1s (Lab-Development): Tagged `ExpiryDate: 2026-01-31`. Past expiry. 0 network connections in 14 days. **Accepted — decommission.** Savings: $12/month. (6) VM A1_v2 (Lab-Development): Created 90+ days ago. avg CPU 0.4%, 0 connections 30 days. No project tag. **Accepted — decommission.** Savings: $28/month. **Other (3):** (7) Unattached managed disk (Lab-Development): 128GB Standard SSD, no VM. **Accepted — delete.** Savings: $10/month. (8) Unattached public IP (Lab-Production): No associated NIC. **Accepted — delete.** Savings: $3.65/month. (9) Storage account (Lab-Development): 0 transactions in 30 days. **Accepted — decommission after data review.** Savings: $8/month. **Total: 7 accepted, 1 deferred, 1 pending data review. Total projected savings: $353.65/month.** |
| **Evidence** | Screenshot #01, Azure Advisor recommendations |
| **FinOps Foundation** | Usage Optimization |
| **Status** | **Pass** |

---

### 2 — Idle Resource Detection Operational

| Field | Detail |
|-------|--------|
| **Expected State** | `waste-scanner.py` identifies resources with zero or near-zero utilization across VMs, App Services, SQL Databases, and Cosmos DB. Configurable thresholds (default: <5% utilization for 14+ days). |
| **Observed State** | `waste-scanner.py` **operational.** 30-day scan results across 127 resources: **Idle resources found: 4.** (1) **VM A1_v2** (Lab-Development): CPU avg 0.4% over 30 days. Zero network connections. No project tag. Owner tag: `dev-team`. Created: 2025-11-03. **Disposition: Decommission.** This VM has no purpose. Nobody is using it. Nobody knows why it exists. $28/month eliminated. (2) **VM B1s** (Lab-Development): CPU avg 1.2%. Past `ExpiryDate: 2026-01-31`. Tagged `Project: poc-auth-migration`. PoC completed December 2025. **Disposition: Decommission.** The PoC ended. The VM didn't. $12/month eliminated. (3) **App Service Plan P1v3** (Lab-Development): avg CPU 4%, 0 requests on weekends, minimal weekday traffic. Running premium tier for a development environment. **Disposition: Right-size to B1.** $94/month saved. (4) **Storage account** (Lab-Development): 0 blob transactions in 30 days. 2.1 GB data retained. No consuming application identified. **Disposition: Decommission after data review with owner.** $8/month pending. **Total idle cost: $142/month ($1,704/year).** On 127 resources in a lab environment. Scale to enterprise and idle waste is a line item. |
| **Evidence** | `waste-scanner.py` output, Screenshot #02 |
| **FinOps Foundation** | Usage Optimization |
| **Status** | **Pass** |

---

### 3 — Right-Sizing Analysis Completed

| Field | Detail |
|-------|--------|
| **Expected State** | `rightsizing-analyzer.py` compares actual CPU, memory, and IOPS utilization against provisioned capacity. Recommends target SKU based on P95 utilization (size for sustained peak, not average). |
| **Observed State** | `rightsizing-analyzer.py` **operational.** Analyzed all non-idle resources: **Right-sizing candidates: 3.** (1) **VM D2s_v5 → B2s** (Lab-Development): P95 CPU: 22%. P95 memory: 41%. Current: 2 vCPU, 8 GB. Recommended: 2 vCPU, 4 GB (B2s burstable). Savings: $47/month (54% reduction). Risk: B-series is burstable, not sustained. Acceptable for development workload with burst credit management. **Disposition: Right-size.** (2) **SQL S2 → S0** (Lab-Development): P95 DTU: 18%. Current: 50 DTU. Recommended: 10 DTU (S0). Savings: $62/month (76% reduction). Risk: DTU throttling during peak queries. Acceptable for development — queries are intermittent. **Disposition: Right-size.** (3) **VM D4s_v5 → D2s_v5** (Lab-Production): P95 CPU: 71%. P95 memory: 58%. Current: 4 vCPU, 16 GB. Recommended: 2 vCPU, 8 GB (D2s_v5). Savings: $89/month (50% reduction). Risk: Production workload. P95 at 71% on 4 vCPU means sustained load. On 2 vCPU that becomes P95 at ~142% — exceeds capacity. **Disposition: Deferred.** Need to analyze workload pattern further. May need D2s_v5 with auto-scale rather than fixed right-size. **Methodology note:** P95 sizing, not average. Average CPU of 34% hides the fact that this VM hits 71% at peak. Right-sizing to average would cause production impact. P95 is the conservative approach — size for what actually happens, not the optimistic middle. **Total right-sizing savings (accepted): $109/month. Deferred: $89/month.** |
| **Evidence** | `rightsizing-analyzer.py` output, Screenshot #04 |
| **NIST 800-53** | CM-8, SA-4 |
| **Status** | **Pass** |

---

### 4 — Orphan Resource Detection Operational

| Field | Detail |
|-------|--------|
| **Expected State** | `orphan-detector.py` identifies resources that have lost their parent: disks without VMs, public IPs without NICs, NICs without VMs, NSGs without attachments, snapshots older than 90 days, empty resource groups. |
| **Observed State** | `orphan-detector.py` **operational.** Full scan results: **Orphans found: 5.** (1) **Managed disk** (128GB Standard SSD): No attached VM. Created: 2025-12-15. Owner tag: `dev-team`. VM was deleted but disk retained (default Azure behavior — disks persist after VM deletion). **Disposition: Delete.** Savings: $10/month. (2) **Public IP**: No associated NIC. Created: 2025-10-22. No tags (legacy resource). Likely remnant of a deleted load balancer or VM. **Disposition: Delete.** Savings: $3.65/month. (3) **Snapshot** (64GB): Created: 2025-09-10. 155 days old. Tagged `Project: migration-q3`. Migration completed Q3 2025. **Disposition: Delete.** Savings: $3.20/month. (4) **NIC**: No attached VM. Created: 2025-11-03. Same date as the idle VM A1_v2. Likely created together, VM was this NIC's parent. **Disposition: Delete with VM decommission.** $0 direct savings but clutter removed. (5) **Empty resource group** (rg-poc-auth): Contains 0 resources. Created: 2025-12-01. Named after the completed PoC. **Disposition: Delete.** $0 but governance hygiene. **Total orphan cost: $16.85/month.** Small individually. The governance value is in the detection — orphans accumulate when nobody looks. The scanner makes looking automatic. |
| **Evidence** | `orphan-detector.py` output, Screenshot #03 |
| **FinOps Foundation** | Usage Optimization |
| **Status** | **Pass** |

---

### 5 — Schedule Optimization Assessed

| Field | Detail |
|-------|--------|
| **Expected State** | Non-production resources assessed for auto-shutdown schedules. Development, test, and sandbox resources should not run 24/7. Schedule recommendations generated based on Environment tag. |
| **Observed State** | Schedule analysis **completed** using Pack 01 Environment tags: **Development environment (8 resources, $1,200/month):** Currently running 24/7 (730 hours/month). Recommended: business hours (8am-6pm weekdays = 220 hours/month). Potential savings: 70% of compute = **$840/month** on compute-hours if fully scheduled. Realistic savings (some resources need extended hours): estimated **$480/month.** **Specific findings:** The weekend VM anomaly (Pack 02, $34.80/weekend) is a schedule optimization finding. If all dev VMs follow auto-shutdown schedule, weekend waste goes to zero. **Staging environment (3 resources, $284/month):** Recommended: business hours + deployment windows. Potential savings: 50% = $142/month. Realistic: $85/month. **Sandbox (1 resource, $14.60/month avg):** Already low utilization. Auto-shutdown would save minimal. Recommend decommission review instead. **Total schedule optimization savings: estimated $565/month realistic ($982/month theoretical max).** **Implementation:** Auto-shutdown policies configured in `schedule-recommendations.json`. Requires Azure Automation account or DevTest Labs auto-shutdown. |
| **Evidence** | Schedule analysis, `schedule-recommendations.json` |
| **FinOps Foundation** | Workload Management |
| **Status** | **Pass** |

---

### 6 — Aged Resource Review Completed

| Field | Detail |
|-------|--------|
| **Expected State** | Resources with expired `ExpiryDate`, overdue `ReviewDate`, or `CreatedDate` > 12 months reviewed. Every aged resource receives a disposition: extend with justification, decommission, or tag with lifecycle dates. |
| **Observed State** | Aged resource scan **completed** using Pack 01 tags: **ExpiryDate expired: 2 resources.** (1) VM B1s: `ExpiryDate: 2026-01-31`. 12 days past expiry. Already flagged as idle (Control 2). **Disposition: Decommission.** (2) Sandbox storage: `ExpiryDate: 2026-01-15`. 28 days past expiry. Contains 340 MB test data. **Disposition: Decommission after data backup confirmation.** **ReviewDate overdue: 3 resources.** (3-5) Three production resources with `ReviewDate: 2025-12-31`. 43 days overdue. Pack 01 hygiene scan also flagged these. All three are active production resources. **Disposition: Reviewed now. ReviewDate updated to 2026-06-30.** **CreatedDate > 12 months, no lifecycle tags: 1 resource.** (6) The idle VM A1_v2 (created 2025-11-03). No ExpiryDate, no ReviewDate. Created 100+ days ago. Already flagged as idle (Control 2). **Disposition: Decommission.** **Finding:** Pack 01 lifecycle tags (CreatedDate, ExpiryDate, ReviewDate) enable proactive waste detection. Without those tags, aged resources are invisible. The 2 expired resources should have been caught at expiry — the fact that they ran 12 and 28 days past expiry means the expiry monitoring needs automation. Currently manual review. |
| **Evidence** | Aged resource scan output |
| **NIST 800-53** | CM-8 |
| **Status** | **Pass** |

---

### 7 — Waste Register Active and Logging

| Field | Detail |
|-------|--------|
| **Expected State** | Every waste finding logged in central register: finding ID, category, resource, cost impact, disposition, owner, remediation timeline. |
| **Observed State** | `waste-register.json` **active** with **12 findings** from comprehensive scan: **By category:** Idle resources: 4 findings ($142/month). Right-sizing: 3 findings ($198/month, $109 accepted). Orphans: 5 findings ($16.85/month). Schedule: 1 systemic finding ($565/month estimated). Aged: 3 findings (overlap with idle — 2 resources, plus 3 overdue reviews). **By disposition:** Decommission: 5 resources ($61.85/month confirmed savings). Right-size: 2 resources ($109/month confirmed savings). Schedule: pending implementation ($565/month estimated). Defer: 1 resource ($89/month pending production analysis). Justify: 0 (no findings justified — all actionable). Review updated: 3 resources ($0 savings but governance compliance). **Total confirmed savings: $170.85/month ($2,050/year).** Total estimated with schedule: $735.85/month ($8,830/year). **100% of findings dispositioned. Every finding has an owner.** |
| **Evidence** | `waste-register.json`, Screenshot #05 |
| **FinOps Foundation** | Usage Optimization |
| **Status** | **Pass** |

---

### 8 — Cross-Pack Traceability Validated End-to-End

| Field | Detail |
|-------|--------|
| **Expected State** | The development VM (weekend anomaly) traced through all 5 FinOps packs: Pack 01 (tagged) → Pack 02 (anomaly detected) → Pack 03 (fitness scored) → Pack 04 (cost attributed) → Pack 05 (waste dispositioned). Full lifecycle cost governance. |
| **Observed State** | **End-to-end trace completed for the development VM (weekend anomaly):** **Pack 01:** Tagged `Owner: dev-team`, `Environment: development`, `CostCenter: CC-1001`, `Project: customer-portal`. Tags enabled everything downstream. ✅ **Pack 02:** Weekend anomaly detected — $34.80 on Saturday-Sunday. Dispositioned: Unexpected — waste. Fed to Pack 05. ✅ **Pack 03:** Fitness score 38/100 (development, weekday-only runtime, medium criticality). Recommendation: on-demand. Correct — don't commit to a reservation for a resource that should be auto-shutdown. ✅ **Pack 04:** Cost allocated to CC-1001, dev-team, customer-portal. Visible in showback report. Team sees the cost. ✅ **Pack 05:** Schedule optimization finding. Auto-shutdown recommended. Weekend cost goes to zero with implementation. Disposition: Schedule. ✅ **All 5 packs traced.** The chain is complete: tag → detect → evaluate → attribute → remediate. The $34.80 weekend anomaly that Pack 02 found becomes a $0 weekend cost after Pack 05 auto-shutdown. That's the FinOps lifecycle working end-to-end. **Also traced: the expired PoC VM (B1s).** Pack 01: ExpiryDate set. Pack 05: Expired, idle, decommission. The tag created the accountability. The scanner enforced it. |
| **Evidence** | Cross-pack trace documentation |
| **FinOps Foundation** | All capabilities (end-to-end) |
| **Status** | **Pass** |

---

### 9 — Remediation Execution Tracked

| Field | Detail |
|-------|--------|
| **Expected State** | Waste findings remediated within disposition timelines: decommission (7 days), right-size (14 days), schedule (14 days). Remediation status tracked in register. Savings verified post-remediation. |
| **Observed State** | Remediation tracking **operational.** Status of 12 findings: **Completed (4):** Orphan disk deleted. Orphan public IP deleted. Orphan snapshot deleted. Orphan NIC deleted. Combined savings confirmed: $16.85/month. **In progress (5):** VM B1s decommission: pending final data check (2 days remaining). VM A1_v2 decommission: pending owner confirmation (3 days remaining). Dev VM D2s_v5 right-size to B2s: change window scheduled. SQL S2 right-size to S0: change window scheduled. Storage account decommission: pending data review. **Deferred (1):** Production VM D4s_v5 right-size: needs workload analysis before production change. **Systemic (1):** Auto-shutdown schedule: Azure Automation account setup in progress. **Not started (1):** Aged sandbox storage decommission: owner notification sent. **Finding:** 4 of 12 findings remediated within SLA (all orphans — lowest risk, fastest action). 5 in progress within SLA. 1 deferred with justification. Remediation velocity is appropriate — orphans first (no dependency), then idle (low risk), then right-size (requires change window), then schedule (requires automation setup). |
| **Status** | **Partial** — 4 completed, 5 in progress, 1 deferred, 2 pending; remediation ongoing |

---

### 10 — Automated Waste Scanning Scheduled

| Field | Detail |
|-------|--------|
| **Expected State** | `waste-scanner.py`, `rightsizing-analyzer.py`, and `orphan-detector.py` scheduled to run weekly. New findings automatically added to register. Trend tracking: is total waste increasing or decreasing month-over-month? |
| **Observed State** | **Scanning scheduled but automation incomplete.** Scripts run successfully when manually executed. Weekly scheduled execution requires Azure Automation account or cron job on a management VM. **Azure Automation account setup is in progress** (same dependency as schedule optimization). Until Automation is configured, scanning runs on manual trigger. Manual scanning was executed 4 times during the 30-day assessment (weekly cadence maintained manually). **Finding:** The scripts work. The scheduling mechanism doesn't yet exist. This is an infrastructure dependency, not a code gap. Once Azure Automation is configured (for both auto-shutdown and waste scanning), weekly automated scans will produce findings without manual intervention. |
| **Status** | **Fail** — scripts operational but automated scheduling not yet implemented |

---

## Remediation Tracker

| # | Control | Finding | Owner | Remediation | Target Date | Status |
|---|---------|---------|-------|-------------|-------------|--------|
| 3 | Right-sizing | Production VM deferred — needs workload analysis | R. Myers | Analyze workload pattern, evaluate auto-scale | 2026-03-15 | Open |
| 6 | Aged resources | ExpiryDate monitoring needs automation | R. Myers | Automate expiry alerting via Azure Automation | 2026-03-01 | Open |
| 9 | Remediation | 8 findings still in progress or pending | R. Myers | Complete within disposition SLAs | Rolling | Open |
| 10 | Automation | Azure Automation account for scheduled scanning | R. Myers | Configure Automation + schedule all 3 scripts | 2026-03-01 | Open |

---

## Waste Elimination Summary

| Category | Findings | Confirmed Savings | Estimated Savings | Status |
|----------|----------|------------------|-------------------|--------|
| Idle Resources | 4 | $52/month | $142/month | 2 decommissioned, 2 in progress |
| Right-Sizing | 3 | $0 (pending) | $198/month | 2 accepted, 1 deferred |
| Orphan Resources | 5 | $16.85/month | $16.85/month | All completed |
| Schedule Optimization | 1 | $0 (pending) | $565/month | Automation pending |
| Aged Resources | 3 | $0 (overlap) | Included above | 2 decommission, 3 review updated |
| **TOTAL** | **12** | **$68.85/month** | **$921.85/month** | |

**Projected annual savings at full remediation: $11,062/year — on a lab with 127 resources.**

---

## Watchstander Notes

1. **$921.85/month in waste on 127 resources is 18.4% of total spend.** Total monthly spend: $5,000. Identified waste: $921.85 (confirmed + estimated). That's within the industry range of 20-35% waste. On a $5,000 lab environment, the absolute number is modest. On a $500,000/month enterprise environment, the same percentage is $92,000/month — over $1M/year. The methodology scales. The percentage is the constant. The six categories of waste exist in every cloud environment. The only variable is whether someone is looking.

2. **The end-to-end trace proves the FinOps pillar works as a system.** Pack 01 tags the resource. Pack 02 detects the anomaly. Pack 03 evaluates it for commitment. Pack 04 attributes the cost. Pack 05 dispositions the waste. Five packs, one resource, one lifecycle. That $34.80 weekend VM anomaly was detected on February 1, attributed to CC-1001 by February 5, and schedule-optimized by February 12. Twelve days from detection to remediation plan. That's governance velocity.

3. **Orphans are the fastest win.** Four orphan resources found and deleted in the first scan. Total effort: 30 minutes. Total savings: $16.85/month ($202/year). The ROI is immediate and the risk is zero — an orphan disk without a VM is not serving any workload. It's pure waste. Every cloud environment has orphans. They accumulate silently because Azure doesn't delete child resources when parent resources are deleted. The orphan detector makes the invisible visible.

4. **P95 sizing saved a production outage.** The D4s_v5 production VM has an average CPU of 34%. Right-sizing to average (D2s_v5) would put P95 utilization at ~142% of capacity — a guaranteed performance failure under peak load. By sizing to P95 instead of average, we identified that this workload NEEDS 4 vCPU and deferred the right-size. The right answer was "don't touch it." The analyzer's P95 methodology prevented a bad decision. That's the value of data over intuition.

5. **The honest fail on automation is the right sequencing gap.** The scripts work. The automation doesn't exist yet. Azure Automation account is the infrastructure dependency that blocks both auto-shutdown (schedule optimization, $565/month) and automated waste scanning (Control 10). One Automation account unblocks both. It's a $20/month service that enables $565/month in savings. The ROI is obvious. The gap is honest.

---

*Assessment conducted by Robert Myers, MBA | SailPoint ISL, Security+, CCSK, CC*
*Stella Maris Governance — 2026*
