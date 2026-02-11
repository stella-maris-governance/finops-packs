# Anomaly Detection & Cost Alerting — Operations Runbook

> **Version:** 1.0.0 | **Author:** Robert Myers, MBA | Stella Maris Governance

---

## 1. Purpose and Scope

Operational procedures for detecting, triaging, and dispositioning cloud cost anomalies. The invoice is an autopsy. This runbook governs the vital sign monitor.

**Scope:** All Azure subscriptions under organizational management. Budget alerts, anomaly detection, tag-based alerts, and resource-level spike detection.

---

## 2. Prerequisites

| Requirement | Detail |
|-------------|--------|
| Pack 01 operational | Tag compliance > 90% for effective tag-based alerting |
| Azure Cost Management | Budgets configured with threshold alerts |
| Cost Management Reader | Role on subscriptions |
| Alert recipients configured | Engineering lead, finance, risk owner distribution lists |
| Daily scheduled tasks | `anomaly-detection.py` and `resource-spike-scan.py` |

---

## 3. Daily Operations

### 3.1 Automated Daily Scans

Two scripts run daily (scheduled task or cron):
```bash
# Anomaly detection: 7-day rolling, day-over-day, weekend, new resource
python3 anomaly-detection.py --subscriptions all --output daily-anomaly-report.json

# Resource-level spike detection
python3 resource-spike-scan.py --subscriptions all --output daily-spike-report.json
```

Both scripts output findings to JSON. Findings above configured severity threshold trigger email notification.

### 3.2 Alert Review

| Time | Action |
|------|--------|
| Morning | Review overnight alerts. Weekend detection findings require immediate attention on Monday. |
| Midday | Check for same-day budget threshold alerts (billing data updates with delay). |
| Weekly | Review all informational alerts. Update alert register. Run trend analysis. |

---

## 4. Alert Triage Process

When an alert fires:

### Step 1 — Acknowledge (within SLA)

| Severity | SLA | Action |
|----------|-----|--------|
| Critical | 4 hours | Acknowledge alert. Begin investigation immediately. |
| High | 24 hours | Acknowledge alert. Schedule investigation. |
| Warning | 48 hours | Acknowledge alert. Investigate during business hours. |
| Informational | Weekly | Log. Review in weekly cadence. |

### Step 2 — Investigate Root Cause

1. **Identify the resource(s)** causing the cost change
2. **Check tags:** Who owns it? What project? What environment?
3. **Check activity logs:** What changed? Who changed it? When?
4. **Correlate with known events:** Was there a deployment? Migration? Load test? Launch?
5. **Ask the owner:** Is this expected?

### Step 3 — Disposition

Assign one disposition:

| Disposition | Criteria | Follow-Up |
|------------|----------|-----------|
| Expected — Business Event | Planned activity explains cost | Log. Verify return to baseline. |
| Expected — Growth | Organic workload growth | Log. Update forecast. Feed Pack 03. |
| Unexpected — Configuration | Misconfiguration caused cost | Remediate. Feed Pack 05. |
| Unexpected — Waste | Resource running without justification | Stop/deallocate/delete. Feed Pack 05. |
| Unexpected — Pricing Change | Vendor pricing changed | Log. Evaluate alternatives. |
| Under Investigation | Root cause not yet determined | Assign owner. Set SLA. |

### Step 4 — Register Entry

Log in `alert-register.json`:
- Alert ID, date, type, severity
- Resource(s) affected
- Root cause
- Disposition
- Remediation taken (if applicable)
- Owner who investigated

---

## 5. Budget Management

### 5.1 Setting Budgets

For each subscription:

1. Review 3-month cost history (or projected cost for new subscriptions)
2. Set monthly budget at 110% of average monthly spend (10% growth buffer)
3. Configure 4 threshold alerts: 50%, 75%, 90%, 100%
4. Configure forecast alert at 110% of budget

### 5.2 Budget Adjustments

Budgets are reviewed monthly:

| Condition | Action |
|-----------|--------|
| Actual spend consistently 80-90% of budget | Budget is well-calibrated. No change. |
| Actual spend consistently < 70% of budget | Budget may be too generous. Tighten by 10%. |
| Actual spend approaches or exceeds 100% | Investigate. If growth is legitimate, increase budget. If waste, remediate. |
| New project or workload added | Increase budget proportionally. |

---

## 6. Threshold Tuning

### Tuning Cadence

| Period | Action |
|--------|--------|
| First 30 days | Observe. Record all alerts. Note false positives and missed anomalies. |
| Day 30 | Adjust thresholds based on findings. |
| Quarterly | Re-evaluate all thresholds against 90-day data. |

### Tuning Principles

- **Too many alerts:** Raise threshold. If 30% deviation fires daily, try 40%.
- **Missing real anomalies:** Lower threshold. If a $200/day spike wasn't caught, lower from 50% to 30%.
- **Weekend detection:** This method is binary — any significant weekend cost on a non-production resource is a finding. Keep threshold low.
- **Tag-category alerts:** Tune per category. Sandbox resources should have tight thresholds. Production may need wider bands.

> **Watchstander Note:** The goal is not zero alerts. The goal is every alert matters. If you're getting 3-5 alerts per week and each one gets investigated and dispositioned, the system is healthy. If you're getting 20 alerts per week and ignoring most of them, the thresholds need tuning.

---

## 7. Trend Analysis

Monthly, analyze the alert register for patterns:

- **Recurring anomalies:** Same resource or category spiking repeatedly? May indicate a systemic configuration issue.
- **Growing baselines:** If the 7-day rolling average keeps climbing, "normal" is getting more expensive. Feed to budget adjustment.
- **Alert distribution:** Are most alerts from one subscription, team, or project? May indicate a team that needs FinOps training.
- **Disposition distribution:** Mostly "expected"? Thresholds may need tightening. Mostly "waste"? Pack 05 needs attention.

---

## 8. Escalation

| Condition | Escalate To | Action |
|-----------|------------|--------|
| Single anomaly > $500/day unexplained | Engineering Lead + Finance | Joint investigation. Resource freeze if needed. |
| Budget exceeded with no explanation | Engineering Lead + Finance + Risk Owner | Spending review. Identify and resolve top cost driver. |
| Recurring waste pattern | Engineering Lead | Systemic remediation. Policy change or automation needed. |
| Vendor pricing change > 10% impact | Finance + Procurement | Vendor engagement. Contract review. Alternative evaluation. |

---

## 9. Review Cadence

| Review | Frequency | Owner |
|--------|-----------|-------|
| Alert check | Daily (automated + manual review) | Risk Owner |
| Alert register update | As alerts occur | Risk Owner |
| Budget vs actual | Weekly | Risk Owner + Finance |
| Threshold tuning review | Monthly (first 90 days), then quarterly | Risk Owner |
| Trend analysis | Monthly | Risk Owner |
| Full anomaly detection review | Quarterly | Risk Owner + Engineering + Finance |

---

## 10. Troubleshooting

**Azure Cost Management data is delayed:** Cost data can be 24-48 hours delayed. Budget alerts and anomaly detection operate on this delayed data. Custom detection scripts run on the most recent available data. Do not expect real-time cost alerting.

**Too many informational alerts:** Raise the 50% budget threshold to 60%, or switch to weekly digest instead of per-event notification. Informational alerts should inform, not interrupt.

**Alert fired but resource has no Owner tag:** Resource is part of the 8.3% untagged (Pack 01 backfill in progress). Investigate using Azure Activity Log to determine creator. Tag immediately. This is why Pack 01 is the foundation.

**Weekend detection flagging legitimate 24/7 workloads:** Add exception list for resources tagged `Environment: production` or `Criticality: critical`. Weekend detection should only flag non-production resources.

**Cross-pillar correlation producing no results:** Normal in first 90 days. Vendor pricing changes, service principal provisioning events, and security tool tier changes are low-frequency events. The correlation will activate when the event occurs.

---

*Stella Maris Governance — 2026*
