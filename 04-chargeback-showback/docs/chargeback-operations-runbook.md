# Chargeback & Showback Operations Runbook

> **Version:** 1.0.0 | **Author:** Robert Myers, MBA | Stella Maris Governance

---

## 1. Purpose

Operational procedures for cost allocation, showback reporting, and chargeback governance. Every dollar is traceable to a team, project, and cost center. Zero leakage.

---

## 2. Monthly Allocation Cycle

| Day | Action | Owner |
|-----|--------|-------|
| 1st | Azure Cost Management exports previous month data | Automated |
| 2nd | `cost-allocation-engine.py` runs three-layer allocation | Automated |
| 3rd | `showback-report.py` generates per-CC reports | Automated |
| 3rd | Quarantine report generated for untagged costs | Automated |
| 5th | Reports distributed to cost center owners | Risk Owner |
| 10th | Variance review — any CC exceeding budget investigated | Risk Owner + Finance |
| 15th | Disputes resolved, adjustments applied if justified | Risk Owner |

---

## 3. Shared Cost Review

Quarterly review of shared cost allocation methods:

1. Are the allocation weights still accurate? (Resource counts, user counts, transaction volumes change.)
2. Has a new shared resource been introduced that needs a rule?
3. Have any teams disputed their allocation? If so, is the dispute valid?
4. Update `shared-cost-rules.json` if methods need adjustment.

---

## 4. Quarantine Management

Weekly:
1. Review quarantine report — which resources are untagged?
2. For each untagged resource: identify creator via Activity Log
3. Assign tags (Pack 01 enforcement) or escalate to engineering lead
4. Track quarantine balance — should decrease month-over-month

Goal: Quarantine = $0. Every dollar attributed.

---

## 5. Budget Management

Per cost center:
1. Budget set annually, reviewed quarterly
2. Monthly variance tracked in `budget-vs-actual.json`
3. Variance > 10% triggers investigation
4. Variance > 25% triggers escalation to Principal + Finance

Budget adjustments require:
- Documented justification (growth, new project, pricing change)
- Principal approval
- Updated in budget tracking

---

## 6. Dispute Resolution

When a team disputes their cost allocation:

1. **Review the allocation method** — is it correctly applied?
2. **Review the data** — are the proportional weights accurate?
3. **Review the rule rationale** — does the method still make sense?
4. If dispute is valid: adjust method, document change, retroactive credit if appropriate
5. If dispute is invalid: explain rationale, document decision

All disputes logged for quarterly shared cost review.

---

## 7. Chargeback Activation (When Ready)

Prerequisites before activating formal chargeback:
- Tag compliance > 99% (quarantine < 1% of total)
- Showback running for 3+ months (teams accustomed to visibility)
- Finance system (GL) selected and cost center mapping complete
- Principal and AO approval to activate

Activation:
1. Map cost center codes to GL accounts
2. Configure monthly export from allocation engine to GL format
3. First month: run parallel (showback + chargeback) to validate
4. Second month: chargeback live — costs appear on team budgets

---

*Stella Maris Governance — 2026*
