# Reservation Operations Runbook

> **Version:** 1.0.0 | **Author:** Robert Myers, MBA | Stella Maris Governance

---

## 1. Purpose

Operational procedures for evaluating, purchasing, monitoring, and renewing cloud reservations and savings plans. Every commitment is backed by utilization data and break-even analysis. No rack rate on predictable workloads. No commitments on uncertain ones.

---

## 2. Quarterly Reservation Review Cycle

| Week | Action |
|------|--------|
| 1 | Pull Azure Advisor recommendations. Identify new candidates. |
| 2 | Run fitness scoring on candidates. Run break-even analysis. |
| 3 | Present recommendations to Principal + Finance. |
| 4 | Purchase approved commitments. Update register. |

---

## 3. Evaluation Workflow

### Step 1 — Identify Candidates

Sources: Azure Advisor recommendations, Pack 02 growth-disposition anomalies, manual review of on-demand resources running 24/7.

### Step 2 — Score Fitness
```bash
python3 reservation-fitness-score.py --workloads candidates.json --output scored.json
```

Review scores. Only candidates scoring >40 proceed to break-even.

### Step 3 — Break-Even Analysis
```bash
python3 break-even-calculator.py --candidates scored_candidates.json --output breakeven.json
```

Review risk scenarios. Ensure net-positive at realistic decommission horizons.

### Step 4 — Decision

| Score | Term | Approval |
|-------|------|----------|
| 70-100 | 1-year RI (conservative) or 3-year if 12+ months validated | Principal + Finance |
| 40-69 | Savings Plan | Principal |
| <40 | On-demand (no commitment) | Logged, no approval needed |

### Step 5 — Purchase and Register

Update `reservation-register.json` with purchase date, term, and monitoring configuration.

---

## 4. Monthly Monitoring

| Check | Tool | Action If Triggered |
|-------|------|-------------------|
| Utilization < 80% | Azure Cost Management | Investigate. Is workload still active? Right-size? Exchange? |
| Utilization < 60% | Azure Cost Management | Escalate. Evaluate exchange or cancellation options. |
| Expiry within 90 days | Register alert | Begin renewal evaluation. Re-score fitness. |
| Actual savings < projected | Savings tracker | Investigate variance. Utilization drop? Pricing change? |

---

## 5. Renewal Decision Process

90 days before expiry:

1. Re-run fitness score with current 30-day data
2. Re-run break-even analysis
3. Compare original projection to actual performance
4. Decision: renew same term, upgrade to 3-year, downsize, or let expire
5. Document decision in register

---

## 6. Exchange and Cancellation

Azure allows RI exchanges (same instance family, different size/region) and limited cancellations with early termination fee.

| Scenario | Action |
|----------|--------|
| Workload right-sized (smaller) | Exchange RI to match new size |
| Workload migrated to different region | Exchange RI to new region |
| Workload decommissioned | Evaluate cancellation vs riding out remaining term |
| Utilization consistently <60% | Exchange to smaller RI or cancel |

---

## 7. Savings Plan Management

Savings Plans commit to a spending level, not a specific resource. Monitor by:

| Metric | Healthy | Action If Unhealthy |
|--------|---------|-------------------|
| Coverage | >80% of commitment utilized | Below 80%: workload mix changed; re-evaluate |
| Savings rate | Within 5% of projected discount | Below: Azure may have changed pricing; investigate |

---

*Stella Maris Governance — 2026*
