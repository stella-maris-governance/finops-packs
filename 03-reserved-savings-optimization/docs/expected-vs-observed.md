# The Law of Evidence: Expected vs. Observed

## Reserved Instance & Savings Plan Optimization

> **Assessment Date:** 2026-02-12 [SAMPLE — replace with your assessment date]
> **Environment:** Stella Maris Lab — Azure Cost Management + Azure Advisor [SAMPLE]
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

### 1 — Azure Advisor Reservation Recommendations Reviewed

| Field | Detail |
|-------|--------|
| **Expected State** | Azure Advisor reservation recommendations reviewed for all subscriptions. Recommendations captured, evaluated, and dispositioned (accept, defer, reject with justification). |
| **Observed State** | Azure Advisor reviewed across 2 subscriptions. **7 recommendations identified:** (1) **SQL Database** (Lab-Production): 1-year RI recommended. Estimated savings $126/month (38%). Current on-demand: $331/month. Running 24/7 for 90+ days. **Accepted — candidate for scoring.** (2) **App Service Plan** (Lab-Production): 1-year RI recommended. Estimated savings $89/month (33%). Current on-demand: $270/month. Running 24/7 for 60+ days. **Accepted — candidate for scoring.** (3) **Virtual Machine D4s_v5** (Lab-Production): 1-year RI recommended. Estimated savings $64/month (36%). Running 24/7 for 120+ days. **Accepted — candidate for scoring.** (4) **Virtual Machine B2s** (Lab-Development): 1-year RI recommended. Estimated savings $18/month (31%). Running weekdays only. **Deferred — runtime hours too low for RI.** (5) **Storage Account** (Lab-Production): Reserved capacity recommended. Estimated savings $12/month (20%). **Deferred — savings below threshold.** (6) **Virtual Machine B1s** (Lab-Development): Savings Plan recommended. Estimated savings $8/month (28%). **Rejected — sandbox resource, expected decommission within 6 months.** (7) **Cosmos DB** (Lab-Production): Reserved capacity recommended. Estimated savings $34/month (25%). **Accepted — candidate for scoring.** **4 accepted, 2 deferred, 1 rejected. Every recommendation dispositioned with justification.** |
| **Evidence** | Screenshot #01, Azure Advisor reservation recommendations |
| **FinOps Foundation** | Rate Optimization |
| **Status** | **Pass** |

---

### 2 — Reservation Fitness Scoring Operational

| Field | Detail |
|-------|--------|
| **Expected State** | `reservation-fitness-score.py` evaluates all candidate workloads across 5 factors: utilization stability (30%), runtime hours (25%), workload lifecycle (20%), environment (15%), criticality (10%). Score determines recommendation: >70 = reserve, 40-70 = savings plan, <40 = on-demand. |
| **Observed State** | `reservation-fitness-score.py` **operational.** Scored 4 accepted candidates from Advisor: **SQL Database:** Utilization stability 92% (score: 28/30). Runtime 100% (score: 25/25). Lifecycle: no expiry tag, production (score: 18/20). Environment: production (score: 15/15). Criticality: high (score: 8/10). **Total: 94/100 → RESERVE.** **App Service Plan:** Utilization stability 87% (score: 26/30). Runtime 100% (score: 25/25). Lifecycle: no expiry (score: 18/20). Environment: production (score: 15/15). Criticality: high (score: 8/10). **Total: 92/100 → RESERVE.** **VM D4s_v5:** Utilization stability 85% (score: 26/30). Runtime 100% (score: 25/25). Lifecycle: no expiry (score: 18/20). Environment: production (score: 15/15). Criticality: medium (score: 6/10). **Total: 90/100 → RESERVE.** **Cosmos DB:** Utilization stability 68% (score: 20/30). Runtime 100% (score: 25/25). Lifecycle: no expiry (score: 18/20). Environment: production (score: 15/15). Criticality: medium (score: 6/10). **Total: 84/100 → RESERVE.** All 4 candidates scored above 70. All recommended for 1-year RI. No candidates in the savings plan or on-demand band. This is expected for a production-heavy lab environment. |
| **Evidence** | `reservation-fitness-score.py` output |
| **FinOps Foundation** | Rate Optimization |
| **Status** | **Pass** |

---

### 3 — Break-Even Analysis Completed for All Candidates

| Field | Detail |
|-------|--------|
| **Expected State** | `break-even-calculator.py` runs for every RI candidate. Break-even point calculated for 1-year and 3-year terms. Risk analysis: "if decommissioned at month N, did we still save?" |
| **Observed State** | Break-even analysis **completed** for 4 candidates: **SQL Database:** 1-year RI: $205/month (vs $331 on-demand). Savings $126/month. Break-even: month 1 (no upfront). 3-year RI: $149/month (55% discount). Break-even: month 1. Total 3-year savings: $6,552. Risk: if decommissioned at month 18, net savings still $2,304. **Recommendation: 1-year RI** (conservative — re-evaluate at renewal). **App Service Plan:** 1-year RI: $181/month (vs $270). Savings $89/month. Break-even: month 1. 3-year: $124/month. Total 3-year savings: $5,256. **Recommendation: 1-year RI.** **VM D4s_v5:** 1-year RI: $114/month (vs $178). Savings $64/month. Break-even: month 1. 3-year: $80/month. Total 3-year savings: $3,528. **Recommendation: 1-year RI.** **Cosmos DB:** 1-year reserved capacity: $103/month (vs $137). Savings $34/month. Break-even: month 1 (no upfront). **Recommendation: 1-year reserved capacity.** **Aggregate: $313/month projected savings across 4 commitments. $3,756/year.** All break-even at month 1 due to no-upfront payment structure. Conservative approach: all 1-year to preserve flexibility. |
| **Evidence** | `break-even-calculator.py` output, Screenshot #03 |
| **NIST 800-53** | SA-4 |
| **Status** | **Pass** |

---

### 4 — Reservation Purchase Decisions Documented

| Field | Detail |
|-------|--------|
| **Expected State** | Every reservation purchase decision documented with: candidate, fitness score, break-even analysis, term selected, approver, and rationale. AO approval for commitments above defined threshold. |
| **Observed State** | **Reservation register created** with 4 entries. Each entry includes: resource, fitness score, break-even data, term (all 1-year), monthly commitment, and projected savings. **Purchase decisions documented but not yet executed.** Lab environment uses pay-as-you-go subscriptions where reservation purchases require billing account owner authorization. All 4 candidates are documented and ready for purchase upon authorization. **Finding:** The decision documentation is complete. The actual purchase is pending billing authorization. In a client environment, this would be the handoff to procurement/finance. The governance artifact (fitness score + break-even + documented approval) is the deliverable. The purchase is the execution. |
| **Evidence** | `reservation-register.json` |
| **FinOps Foundation** | Rate Optimization |
| **Status** | **Pass** |

---

### 5 — Savings Plan Evaluation Completed

| Field | Detail |
|-------|--------|
| **Expected State** | Azure Savings Plans evaluated as an alternative to RIs for workloads with moderate fitness scores (40-69) or mixed instance families. Savings Plan vs RI comparison documented. |
| **Observed State** | Savings Plan evaluation **completed.** **Finding:** No candidates scored in the 40-69 range (savings plan band). All 4 candidates scored 84-94 (RI band). 2 deferred candidates (Dev B2s, storage) did not meet minimum threshold for any commitment. **Savings Plan evaluated for aggregate coverage:** Total on-demand compute: $779/month across both subscriptions. Savings Plan at $500/month commitment would cover 64% of compute at approximately 20% discount. Savings: ~$100/month. However, with 4 specific RIs already identified at $313/month savings, the targeted RI approach yields higher savings than a broad Savings Plan. **Recommendation: RIs for the 4 identified candidates. Re-evaluate Savings Plan when workload mix diversifies.** |
| **Evidence** | Savings Plan analysis documentation |
| **FinOps Foundation** | Rate Optimization |
| **Status** | **Pass** |

---

### 6 — Reservation Utilization Monitoring Configured

| Field | Detail |
|-------|--------|
| **Expected State** | Reservation utilization monitoring configured in Azure Cost Management. Alert when utilization drops below 80%. Dashboard showing utilization by reservation. |
| **Observed State** | **Monitoring configured** in Azure Cost Management: Utilization threshold alert: **80%** (warning), **60%** (high — investigate). Alert recipients: resource owner, engineering lead, finance. Dashboard: reservation utilization view configured showing per-reservation utilization percentage. **Current state:** No active reservations yet (purchases pending authorization), so monitoring is configured but not producing data. Validated configuration by reviewing Azure Cost Management reservation utilization interface — fields, filters, and export options confirmed operational. **Finding:** Monitoring is ready. It will begin producing data when the first reservation is purchased. This is configuration-complete but observation-pending. |
| **Evidence** | Azure Cost Management reservation monitoring configuration |
| **FinOps Foundation** | Usage Optimization |
| **Status** | **Pass** |

---

### 7 — Monthly Savings Tracking Established

| Field | Detail |
|-------|--------|
| **Expected State** | Monthly savings tracked: actual reserved cost vs on-demand counterfactual (what we would have paid). Cumulative savings visible. Savings attributed to cost centers and projects via Pack 01 tags. |
| **Observed State** | `savings-tracker.json` **created** with projected savings model: **Projected monthly savings (when reservations active):** SQL Database: $126/month. App Service: $89/month. VM D4s_v5: $64/month. Cosmos DB: $34/month. **Total: $313/month projected.** Savings attribution by Pack 01 tags: CostCenter CC-1001 (Engineering): $253/month (SQL + App Service + VM). CostCenter CC-1002 (Data): $34/month (Cosmos DB). Project customer-portal: $215/month. Project data-pipeline: $34/month. **Finding:** Savings tracking is configured with projected data. Actual vs projected tracking will begin once reservations are purchased. The framework for attribution exists because Pack 01 tags are already on these resources. |
| **Evidence** | `savings-tracker.json` |
| **FinOps Foundation** | Rate Optimization |
| **Status** | **Pass** |

---

### 8 — Deferred and Rejected Candidates Documented

| Field | Detail |
|-------|--------|
| **Expected State** | Every Advisor recommendation that was deferred or rejected includes documented justification. Deferred candidates scheduled for re-evaluation. |
| **Observed State** | **3 non-accepted recommendations documented:** (1) **Dev B2s VM — Deferred.** Justification: Runs weekday business hours only (~40% of month). Runtime too low for RI. Weekend anomaly finding (Pack 02) suggests this VM should be auto-shutdown, further reducing runtime. Re-evaluate after auto-shutdown implementation. Next review: 2026-Q2. (2) **Storage Account — Deferred.** Justification: Savings of $12/month below minimum threshold for commitment management overhead. At current growth rate, re-evaluate when storage exceeds $100/month. Next review: 2026-Q3. (3) **Sandbox B1s VM — Rejected.** Justification: Tagged `ExpiryDate: 2026-06-30`. Resource expected to be decommissioned within 6 months. 1-year commitment would outlive the resource. On-demand is correct for temporary workloads. **All 3 documented. Deferred candidates have re-evaluation dates. Rejected candidate has explicit lifecycle justification.** |
| **Evidence** | Reservation register deferred/rejected section |
| **FinOps Foundation** | Rate Optimization |
| **Status** | **Pass** |

---

### 9 — Expiration Management Process Documented

| Field | Detail |
|-------|--------|
| **Expected State** | Reservation expiration tracked. 90-day, 60-day, and 30-day alerts before expiry. Renewal decision process: re-score fitness, re-run break-even, decide renew/modify/let-expire. |
| **Observed State** | Expiration management **documented in runbook.** Alert schedule: 90/60/30 days before expiry. Renewal decision workflow mirrors initial assessment: re-score fitness → re-run break-even → present to Principal + Finance → decide. **Current state:** No active reservations, so no expirations to track. Process is documented but untested with a real expiration. **Finding:** This is the same pattern as Pack 02 critical/high severity triage — the process exists but the triggering event hasn't occurred. It will activate when the first reservation approaches expiry (12 months from purchase). |
| **Evidence** | Runbook expiration management section |
| **FinOps Foundation** | Rate Optimization |
| **Status** | **Partial** — process documented but not tested with real expiration event |

---

### 10 — Actual Savings Validated Against Projections

| Field | Detail |
|-------|--------|
| **Expected State** | After 30 days of active reservations, actual savings compared to projected savings. Variance analysis performed. Utilization confirmed above 80%. |
| **Observed State** | **Cannot validate.** Reservations not yet purchased (pending billing authorization). No actual savings data exists to compare against projections. **This is the honest gap.** The analysis is complete. The fitness scores are calculated. The break-even is modeled. The projections are documented. But until money is actually committed and 30 days of utilization data is collected, the savings are theoretical. The model says $313/month. Reality will say something different. This control validates when the first reservation has 30 days of utilization history. |
| **Status** | **Fail** — no actual savings data; projections only |

---

## Remediation Tracker

| # | Control | Finding | Owner | Remediation | Target Date | Status |
|---|---------|---------|-------|-------------|-------------|--------|
| 4 | Purchase decisions | Reservations documented but not purchased | R. Myers | Purchase upon billing authorization | 2026-03-15 | Open |
| 9 | Expiration mgmt | Process untested with real expiration | R. Myers | Time-based — activates at first expiry | 12 months post-purchase | Open |
| 10 | Actual savings | No actual data — projections only | R. Myers | Validate 30 days post-purchase | 2026-04-15 | Open |

---

## Watchstander Notes

1. **$313/month is $3,756/year on a lab environment.** Scale that to an enterprise with 500 VMs, 50 databases, and 20 app services — the savings are six figures. The methodology doesn't change. The fitness score works the same at 4 candidates or 400. What matters is that every commitment is justified by data, not by gut feel. The fitness score IS the justification. The break-even IS the risk analysis. Together, they are the evidence a CFO needs to approve the commitment.

2. **All 1-year recommendations — that's deliberate conservatism.** 3-year RIs save more (55% vs 35%), but they lock you in for 36 months. In a governance program that's 3 months old, locking into 3-year commitments is premature optimization. Start with 1-year. Prove the model. Validate utilization. At renewal, you'll have 12 months of data to decide whether 3-year is appropriate. Conservative first commitments build trust with finance.

3. **The sandbox VM rejection is the fitness score doing its job.** Azure Advisor recommended a reservation. The fitness score rejected it because the `ExpiryDate` tag (Pack 01) indicated decommission within 6 months. A reservation would have outlived the resource. This is the cross-pillar integration working: Pack 01 tags feed Pack 03 scoring. The tag prevented a bad commitment. That's governance.

4. **The honest fail on Control 10 is the same pattern we've seen across packs.** You can model, project, and document — but until real money is committed and real utilization is measured, the savings are theoretical. The fail ensures we don't claim cost savings we haven't actually realized. When the reservations are purchased and 30 days pass, this control either validates the model or reveals where the projections were wrong. Both outcomes are valuable.

5. **Deferred is not ignored.** The Dev B2s and storage account were deferred with re-evaluation dates. They'll cycle back through the fitness score at the scheduled review. The governance value is in the tracking — these resources don't fall through the cracks because someone forgot about them. They're in the register with a next-review date. That's the difference between a one-time analysis and a continuous optimization program.

---

*Assessment conducted by Robert Myers, MBA | SailPoint ISL, Security+, CCSK, CC*
*Stella Maris Governance — 2026*
