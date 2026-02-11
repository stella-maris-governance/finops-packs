# Cost Governance & Tagging Policy — Operations Runbook

> **Version:** 1.0.0 | **Author:** Robert Myers, MBA | Stella Maris Governance

---

## 1. Purpose and Scope

Operational procedures for maintaining tag governance across all Azure subscriptions. Tags are the foundation of cloud financial visibility. This runbook governs how they're enforced, monitored, and maintained.

**Scope:** All Azure subscriptions under organizational management. All taggable resources.

---

## 2. Prerequisites

| Requirement | Detail |
|-------------|--------|
| Azure Policy Contributor | Role on all subscriptions for policy deployment |
| Cost Management Reader | Role on billing account or subscriptions |
| Resource Graph Reader | Role for compliance queries |
| Tag taxonomy approved | Documented and stakeholder-approved |
| Finance cost center mapping | Current CC-XXXX list from finance team |

---

## 3. Tag Enforcement Deployment

### 3.1 Initial Deployment (New Subscription)

1. **Deploy Policy 1 (Deny Required Tags) in audit mode first**
```bash
   python3 deploy-tag-policies.ps1 -Mode AuditOnly -Subscription "Sub-Name"
```
2. **Wait 30 days.** Collect compliance data. Identify non-compliant resources.
3. **Run tag compliance report** to establish baseline
4. **Communicate to engineering:** tag taxonomy, naming conventions, 30-day grace period
5. **Remediate existing resources** (backfill campaign)
6. **Switch to deny mode** when compliance exceeds 90%
```bash
   python3 deploy-tag-policies.ps1 -Mode Enforce -Subscription "Sub-Name"
```
7. **Deploy remaining policies** (audit recommended, inheritance, allowed values)

### 3.2 Adding to Existing Subscription

Same process. The audit-first approach prevents disruption.

> **Watchstander Note:** Never deploy deny policies without the audit period. The audit period is your data collection phase. It tells you how bad the problem is, who the top non-compliant teams are, and how many resources need backfill. The data builds the case for enforcement. Enforcement without data creates resistance.

---

## 4. Tag Compliance Monitoring

### 4.1 Weekly Compliance Report
```bash
python3 tag-compliance-report.py --subscriptions all --output weekly-report.json
```

Report includes:
- Required tag compliance % (per tag and aggregate)
- Recommended tag compliance % (per tag and aggregate)
- Week-over-week trend
- Deny events count
- Top 10 non-compliant resources with owners
- New resources created (all should be 100% compliant)

### 4.2 Compliance Targets

| Metric | 30-Day Target | 90-Day Target | Steady State |
|--------|--------------|--------------|-------------|
| Required tag compliance | 95% | 99% | 99%+ |
| Recommended tag compliance | 60% | 80% | 80%+ |
| New resource compliance | 100% | 100% | 100% |
| Deny events (weekly) | < 5 | 0 | 0 |

### 4.3 Escalation for Non-Compliance

| Compliance Level | Action |
|-----------------|--------|
| > 95% required | Normal operations. Weekly report. |
| 90-95% required | Targeted outreach to owners of non-compliant resources |
| 80-90% required | Engineering lead engaged. Remediation sprint. |
| < 80% required | Escalate to management. Investigate root cause (tooling issue? process gap? resistance?) |

---

## 5. Tag Hygiene Scan

### 5.1 Quarterly Scan
```bash
python3 tag-hygiene-scan.py --subscriptions all --directory entra-export.json --projects active-projects.json --costcenters cc-list.json
```

Scan checks:
- **Owner validation:** Does the `Owner` tag value exist in Entra ID? If not, the person may have left.
- **Project validation:** Does the `Project` tag value exist in the active project list? If not, the project may be defunct.
- **CostCenter validation:** Does the `CostCenter` value exist in the finance cost center list? If not, the code may be retired.
- **ReviewDate validation:** Is the `ReviewDate` past? If so, the resource is overdue for review.
- **ExpiryDate validation:** Is the `ExpiryDate` past? If so, the resource should be decommissioned.
- **CreatedDate age analysis:** Resources older than 12 months without a recent ReviewDate are flagged.

### 5.2 Responding to Findings

| Finding | Action | Timeline |
|---------|--------|----------|
| Owner departed | Reassign to team lead or manager. If no one claims it, candidate for decommission. | 7 days |
| Defunct project | Contact last known project lead. If project confirmed ended, resources are decommission candidates. | 14 days |
| Retired cost center | Contact finance for updated mapping. Retag or decommission. | 14 days |
| Overdue review | Notify owner. Owner must confirm resource is still needed. | 7 days |
| Past expiry | Notify owner. Default action: decommission unless owner extends with justification. | 3 days |

---

## 6. Tag Backfill Process

For pre-policy resources missing required tags:

1. **Export non-compliant resource list** from Azure Policy compliance
2. **Group by resource group** (often a resource group can be tagged, and inheritance handles children)
3. **Identify owners** through:
   - Azure Activity Log (who created or last modified the resource?)
   - Resource group naming convention (if any)
   - Ask engineering team leads
4. **Bulk tag application:**
```bash
   # Tag all resources in a resource group
   az tag update --resource-id /subscriptions/{sub}/resourceGroups/{rg} --operation merge --tags Owner=robert.myers Environment=development CostCenter=CC-1001 Project=stella-maris
```
5. **Verify inheritance** applies tags to child resources
6. **Re-run compliance report** to confirm improvement

### Unattributable Resources

If a resource has no identifiable owner after investigation:
1. Tag with `Owner: unattributed` and `ReviewDate: [today + 30 days]`
2. Monitor for 30 days — is anyone using it? (check metrics, access logs)
3. If zero usage in 30 days: decommission candidate. Notify engineering lead.
4. If in use: identify consumer through activity logs. Assign owner.

---

## 7. Exception Management

### Requesting an Exception

1. Submit exception request with: resource ID, reason tags cannot be applied, proposed duration
2. Risk Owner reviews within 3 business days
3. If approved: exception logged with expiry date (max 90 days)
4. At expiry: exception reviewed. Renew (with justification) or remediate.

### Permanent Exceptions

Only for Microsoft-managed resource groups that cannot be tagged by users. These are documented and excluded from compliance calculations.

---

## 8. New Tag Addition Process

When a new tag needs to be added to the taxonomy:

1. **Propose** with: tag key, description, required or recommended, allowed values (if restricted)
2. **Review** with engineering (feasibility), finance (if cost-related), security (if sensitivity-related)
3. **Approve** and add to taxonomy document
4. **Deploy** Azure Policy update (audit mode for 30 days, then enforce if required)
5. **Communicate** to all teams
6. **Backfill** existing resources if needed

---

## 9. Review Cadence

| Review | Frequency | Owner |
|--------|-----------|-------|
| Tag compliance report | Weekly | Risk Owner |
| Tag hygiene scan | Quarterly | Risk Owner |
| Tag taxonomy review | Semi-annual | Risk Owner + Engineering + Finance |
| Policy exception review | At expiry (max 90-day cycle) | Risk Owner |
| Cost center mapping refresh | Quarterly (sync with finance) | Finance + Risk Owner |
| Full tag governance review | Annual | Risk Owner + Stakeholders |

---

## 10. Troubleshooting

**Engineers complaining about deny policy:** Share the compliance trend data. Show that deny events dropped to zero within 2-3 weeks for every team that adopted tagging. Offer to help with tagging automation (Terraform/Bicep modules with required tags pre-configured).

**Tag inheritance not applying:** Azure Policy evaluation cycle is approximately 15 minutes. Wait one cycle. If still not applied, check policy assignment scope and exclusions. Verify the resource type supports the `modify` effect.

**Cost Management not showing tag breakdown:** Cost Management may take 24-48 hours to reflect new tags in cost analysis. Tags applied mid-billing-cycle will appear in the next billing period's data.

**Finance cost center list doesn't match tags:** Schedule quarterly sync between finance and engineering. Maintain a mapping document. When finance retires a cost center, the hygiene scan catches orphaned tags.

---

*Stella Maris Governance — 2026*
