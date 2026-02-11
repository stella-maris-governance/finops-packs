# The Law of Evidence: Expected vs. Observed

## Anomaly Detection & Cost Alerting

> **Assessment Date:** 2026-02-12 [SAMPLE — replace with your assessment date]
> **Environment:** Stella Maris Lab — Azure Cost Management + Custom Detection [SAMPLE]
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

### 1 — Budget Alerts Configured for All Subscriptions

| Field | Detail |
|-------|--------|
| **Expected State** | Azure Cost Management budgets created for each subscription with threshold alerts at 50%, 75%, 90%, and 100% of monthly budget. Alert recipients configured (resource owner, engineering lead, finance). |
| **Observed State** | **2 budgets configured** across 2 subscriptions: **Lab-Production:** Monthly budget $3,200. Alert thresholds: 50% ($1,600) → informational, 75% ($2,400) → warning to engineering lead, 90% ($2,880) → high to engineering lead + finance, 100% ($3,200) → critical to engineering lead + finance + risk owner. **Lab-Development:** Monthly budget $1,800. Same threshold structure. Alert recipients: engineering lead, finance contact, risk owner (R. Myers). **30-day results:** Lab-Production reached 75% threshold on Feb 8 (day 22 of billing cycle). Alert fired. Investigation: on-pace spending, no anomaly — 22/28 days = 78.6% of month elapsed, 75% of budget consumed. **Expected pace.** Disposition: informational, logged. Lab-Development did not breach any threshold (59% of budget at day 22). |
| **Evidence** | Screenshot #01, Azure Cost Management budget configuration |
| **FinOps Foundation** | Anomaly Management |
| **Status** | **Pass** |

---

### 2 — Azure Cost Management Anomaly Detection Enabled

| Field | Detail |
|-------|--------|
| **Expected State** | Azure Cost Management built-in anomaly detection enabled. Anomalies surfaced in Cost Management dashboard. Anomaly alerts configured for notification. |
| **Observed State** | Azure Cost Management anomaly detection **enabled** on both subscriptions. **30-day results: 3 anomalies surfaced.** **Anomaly 1 (Jan 24):** Storage account cost spike $12.40 → $38.70 (212% increase). Root cause: blob storage tier changed from Cool to Hot during migration testing. Disposition: Expected — configuration was temporary, reverted Jan 26. Cost returned to baseline. **Anomaly 2 (Feb 3):** Compute cost spike $47.20 → $89.60 (90% increase). Root cause: auto-scale event on App Service during load test. Disposition: Expected — business event. Cost returned to baseline Feb 4. **Anomaly 3 (Feb 7):** Database cost increase $22.10 → $34.50 (56% increase). Root cause: Azure SQL DTU utilization exceeded threshold, auto-scaled to next tier. Disposition: Expected — growth. Feed to Pack 03 for reservation analysis. **All 3 anomalies investigated and dispositioned within SLA.** |
| **Evidence** | Azure Cost Management anomaly view, Screenshot #02 |
| **FinOps Foundation** | Anomaly Management |
| **Status** | **Pass** |

---

### 3 — Custom Statistical Anomaly Detection Operational

| Field | Detail |
|-------|--------|
| **Expected State** | `anomaly-detection.py` running daily with 4 detection methods: 7-day rolling average deviation, day-over-day spike, weekend/off-hours anomaly, and new resource cost detection. Configurable thresholds. |
| **Observed State** | `anomaly-detection.py` **deployed** with daily scheduled execution. Detection methods active: **7-day rolling average (30% threshold):** 2 detections in 30 days. Both correlated with Azure Cost Management anomalies (storage migration, load test). No unique findings beyond ACM — validates that ACM anomaly detection is catching the same events. **Day-over-day spike (50% threshold):** 1 detection. Feb 3 load test compute spike (same as ACM Anomaly 2). No unique findings. **Weekend anomaly:** **1 unique finding.** Feb 1-2 (Saturday-Sunday): development environment VMs accrued $34.80 in compute cost. Normal weekday average: $8.20/day. These VMs should be deallocated on weekends. Owner notified. **Disposition: Unexpected — waste.** Fed to Pack 05. **New resource cost:** 1 detection. New premium storage account created Feb 6, accruing $8.40/day. Investigated: legitimate new project resource, properly tagged. Disposition: Expected — growth. Thresholds stable after 30-day tuning: 7-day rolling at 30% and day-over-day at 50% produce actionable alerts without excessive noise. Weekend detection is the highest-value custom method — catches what ACM doesn't flag. |
| **Evidence** | `anomaly-detection.py` output log |
| **NIST 800-53** | AU-6 |
| **Status** | **Pass** |

---

### 4 — Tag-Based Cost Alerts Configured

| Field | Detail |
|-------|--------|
| **Expected State** | Alerts configured by Pack 01 tag categories: Environment (sandbox/test cost thresholds), Owner (individual spike), Project (budget deviation), CostCenter (trend deviation). |
| **Observed State** | **4 tag-category alert rules** configured: **Environment: sandbox > $50/day:** 0 alerts in 30 days. Sandbox costs averaging $14.60/day. Within threshold. **Environment: test > 20% of production:** 0 alerts. Test: $187/month vs Production: $2,847/month (6.6%). Well within threshold. **Owner spike > 40% week-over-week:** 1 alert. `dev-team` costs increased 47% week 2 → week 3. Investigated: new project resources provisioned (legitimate). Disposition: Expected — growth. **Project > 25% above allocated budget:** 0 alerts. All projects within allocation. **Finding:** Tag-based alerting depends entirely on Pack 01 tag compliance. The 91.7% required tag compliance means 8.3% of costs are not attributable to tag-based alerts. Untagged costs are monitored by subscription-level alerts but miss tag-category granularity. As tag compliance approaches 99%, tag-based alerting coverage improves proportionally. |
| **Evidence** | Alert rule configuration, alert log |
| **FinOps Foundation** | Anomaly Management, Cost Allocation |
| **Status** | **Pass** |

---

### 5 — Resource-Level Spike Detection Operational

| Field | Detail |
|-------|--------|
| **Expected State** | `resource-spike-scan.py` runs daily. Identifies individual resources where daily cost exceeds 2× 7-day average or new resources exceeding $25/day. |
| **Observed State** | `resource-spike-scan.py` **operational.** Daily execution, 30-day results: **4 resource-level spikes detected:** (1) **Storage account** (Jan 24): Cool → Hot tier. $12.40 → $38.70. Correlated with ACM Anomaly 1. Resolved. (2) **App Service** (Feb 3): Auto-scale during load test. $47.20 → $89.60. Correlated with ACM Anomaly 2. Resolved. (3) **Development VM** (Feb 1-2 weekend): $8.20 → $34.80. Weekend anomaly. Fed to Pack 05. (4) **Premium storage account** (Feb 6): New resource, $8.40/day. Legitimate, properly tagged. **Resource attribution:** All 4 resources had `Owner` tags. All investigated within SLA. Resource-level detection overlaps with ACM anomaly detection for major spikes but catches granular items (weekend VM, moderate new resource cost) that ACM may not flag as anomalies. |
| **Evidence** | `resource-spike-scan.py` output |
| **FinOps Foundation** | Anomaly Management |
| **Status** | **Pass** |

---

### 6 — Forecast Alerting Configured

| Field | Detail |
|-------|--------|
| **Expected State** | Azure Cost Management forecasted spend alerts configured. Alert when projected monthly spend exceeds budget by 10%. Enables proactive budget management before month-end. |
| **Observed State** | Forecast alerts **configured** on both subscriptions: **Lab-Production:** Forecast alert at 110% of $3,200 budget ($3,520). Current forecast: $3,050 (95.3% of budget). No alert triggered. **Lab-Development:** Forecast alert at 110% of $1,800 budget ($1,980). Current forecast: $1,640 (91.1% of budget). No alert triggered. **Finding:** Azure Cost Management forecasting has a known limitation: forecasts in the first 10 days of a billing cycle are less accurate due to limited data. Forecasts become reliable after day 10-14. Alert was configured from day 1 but meaningful forecasting begins mid-cycle. No forecast alerts triggered in 30 days — both subscriptions are tracking within budget. |
| **Evidence** | Azure Cost Management forecast view |
| **FinOps Foundation** | Forecasting |
| **Status** | **Pass** |

---

### 7 — Alert Register Active and Logging

| Field | Detail |
|-------|--------|
| **Expected State** | Every cost alert logged in centralized register: alert ID, type, severity, resource/category, root cause, disposition, remediation (if applicable), owner. |
| **Observed State** | `alert-register.json` **active** with **8 entries** from 30 days: |
| | (1) Lab-Production 75% budget threshold — Expected pace, informational |
| | (2) Storage Hot tier spike — Expected, temporary migration config |
| | (3) App Service auto-scale spike — Expected, load test business event |
| | (4) SQL DTU tier increase — Expected, growth, feed Pack 03 |
| | (5) Weekend dev VM cost — **Unexpected waste**, feed Pack 05 |
| | (6) Dev-team owner spike — Expected, new project resources |
| | (7) New premium storage — Expected, growth, properly tagged |
| | (8) Lab-Production 75% threshold re-check — Confirmed on-pace |
| | **Disposition summary:** Expected — business event: 3. Expected — growth: 2. Expected — on-pace: 2. **Unexpected — waste: 1** (weekend VM). **100% of alerts dispositioned.** The 1 waste finding proves the model: anomaly → investigation → waste identified → Pack 05 feed. |
| **Evidence** | `alert-register.json`, Screenshot #05 |
| **NIST 800-53** | AU-6 |
| **Status** | **Pass** |

---

### 8 — Alert Triage Workflow Documented and Tested

| Field | Detail |
|-------|--------|
| **Expected State** | Documented triage workflow: alert received → investigation → root cause → disposition → remediation (if needed) → register entry. Response SLAs by severity enforced. |
| **Observed State** | Triage workflow **documented** in runbook and **tested** through 8 real alerts in 30 days. Response SLA performance: **Critical (4-hour SLA):** 0 critical alerts. Not tested. **High (24-hour SLA):** 1 alert (Lab-Production 90% would have triggered but was not reached). Forecast alerts not triggered. Effectively untested at high severity. **Warning (48-hour SLA):** 3 alerts. All investigated within 24 hours (faster than SLA). **Informational (weekly review):** 4 alerts. All reviewed in weekly cadence. **Finding:** No critical or high-severity alerts fired in 30 days. The triage process is validated for warning and informational severity but untested at critical/high. This is partially good news (no serious anomalies) but means the urgent response path is unexercised. |
| **Evidence** | Triage log with timestamps |
| **FinOps Foundation** | Anomaly Management |
| **Status** | **Partial** — triage process validated for warning/informational; critical/high severity response untested |

---

### 9 — Alert Threshold Tuning Completed

| Field | Detail |
|-------|--------|
| **Expected State** | After 30-day observation period, alert thresholds tuned for signal-to-noise ratio. False positive rate below 20%. Every alert that fires is worth investigating. |
| **Observed State** | **30-day tuning results:** Total alerts: 8. Alerts requiring investigation: 8 (all investigated). Alerts with actionable findings: 1 (weekend VM waste). Alerts confirming expected behavior: 7. **False positives: 0** (all alerts corresponded to real cost events). However, 7 of 8 were confirmations of expected behavior rather than problems discovered. The weekend VM finding is the one true "catch." **Threshold assessment:** 7-day rolling average (30%): appropriate — catches real spikes without noise. Day-over-day (50%): appropriate — only fires on significant single-day events. Weekend detection: **highest value** — caught waste that no other method flagged. Sandbox $50/day threshold: not triggered (sandbox costs well below). May lower to $30/day for tighter governance. **Recommendation:** Lower sandbox daily threshold from $50 to $30. Add after-hours detection for production resources (alert if production compute drops — may indicate outage, not cost issue but operationally relevant). |
| **Evidence** | Threshold tuning analysis document |
| **FinOps Foundation** | Anomaly Management |
| **Status** | **Pass** |

---

### 10 — Cross-Pillar Cost Correlation Active

| Field | Detail |
|-------|--------|
| **Expected State** | Cost anomalies correlated with events from other pillars: Supply Chain vendor cost changes, Identity service principal cost attribution, Cloud Security tool licensing costs. Anomaly in one pillar investigated for cost impact in FinOps. |
| **Observed State** | Cross-pillar correlation **designed but not yet producing findings.** **Supply Chain correlation:** Pack 04 vendor scorecard financial signals (SEC filings, funding, burn rate) are tracked but have not generated a cost anomaly in the FinOps environment. Designed to detect: vendor price increase → your cost increase. Not triggered in 30 days. **Identity correlation:** Service principal cost attribution designed — when a vendor service principal provisions resources, the cost should be tagged to the vendor relationship. Not triggered (no vendor-provisioned resources in 30 days). **Cloud Security correlation:** Defender for Cloud licensing costs tracked as a line item. No anomaly detected. Stable at $312/month. **Finding:** The cross-pillar feeds are designed and the correlation logic is documented, but 30 days of stable operations have not produced a cross-pillar cost event. The correlation will prove its value when a vendor raises prices, a misconfigured service principal provisions expensive resources, or a security tool license tier changes unexpectedly. |
| **Status** | **Fail** — cross-pillar correlation designed but not validated with a real cross-pillar finding |

---

## Remediation Tracker

| # | Control | Finding | Owner | Remediation | Target Date | Status |
|---|---------|---------|-------|-------------|-------------|--------|
| 3 | Weekend detection | Dev VMs running on weekends costing $34.80 | R. Myers | Implement auto-shutdown schedule for dev VMs (Pack 05) | 2026-02-28 | Open |
| 8 | Alert triage | Critical/high severity response untested | R. Myers | Time-based — will validate on first critical/high alert or simulate | 2026-Q2 | Open |
| 9 | Threshold tuning | Sandbox threshold may be too generous at $50/day | R. Myers | Lower to $30/day, observe for 30 days | 2026-03-15 | Open |
| 10 | Cross-pillar | Correlation designed but unvalidated | R. Myers | Time-based — first cross-pillar event will validate | When triggered | Open |

---

## Watchstander Notes

1. **The weekend VM is the $34.80 proof of concept.** One finding. One resource. $34.80 on a weekend when it should have cost zero. Extrapolated: that's $140/month, $1,680/year — on one VM in one environment. Multiply by every development VM across a real enterprise and the waste is material. The weekend anomaly detection method caught what budget alerts, Azure Cost Management anomaly detection, and resource-level spike detection did not. Custom detection fills the gaps that native tools leave. This one finding justifies the pack.

2. **7 of 8 alerts confirmed expected behavior. That's not waste — that's confidence.** An alert that fires and confirms expected behavior isn't a false positive. It's a verification. You now have documented evidence that the storage tier change was intentional, the load test was planned, the database growth is organic, and the budget is tracking to pace. When finance asks "what happened in February?" you have 8 documented answers with root causes and dispositions. That's governance.

3. **The honest fail on cross-pillar correlation is patience, not failure.** The feeds are designed. The logic is documented. A vendor hasn't raised prices. A service principal hasn't provisioned unexpected resources. A security tool hasn't changed licensing tiers. These events will happen — just not in the first 30 days of a new lab environment. When they do, the correlation is ready. Marking it as a fail ensures we don't claim a capability we haven't proven.

4. **Tune for signal, not noise.** Zero false positives in 30 days means the thresholds are appropriately set — but it also means we might be missing subtle anomalies. The recommendation to lower the sandbox threshold from $50 to $30 is an example of progressive tightening. Start conservative (avoid alert fatigue), observe, then tighten. Alert fatigue is the biggest threat to anomaly detection. An engineer who ignores cost alerts because they're always noise is an engineer who will ignore the one alert that matters.

5. **The invoice is an autopsy. This pack is the vital sign monitor.** The monthly invoice tells you what you spent. This pack tells you why, when, and whether you meant to. The difference is the difference between a finance meeting that says "we're over budget" and one that says "we're over budget because of these 3 events, 2 of which are justified growth and 1 of which is waste we've already remediated." That's the Duty of Fiscal Stewardship in practice.

---

*Assessment conducted by Robert Myers, MBA | SailPoint ISL, Security+, CCSK, CC*
*Stella Maris Governance — 2026*
