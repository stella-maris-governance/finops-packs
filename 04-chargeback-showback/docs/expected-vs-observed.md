# The Law of Evidence: Expected vs. Observed

## Chargeback & Showback

> **Assessment Date:** 2026-02-12 [SAMPLE — replace with your assessment date]
> **Environment:** Stella Maris Lab — Azure Cost Management + Custom Allocation [SAMPLE]
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

### 1 — Cost Allocation Model Documented and Approved

| Field | Detail |
|-------|--------|
| **Expected State** | Three-layer allocation model documented: (1) direct attribution via Pack 01 tags, (2) shared cost distribution with defined allocation methods, (3) untagged cost handling policy. Model reviewed and approved by Principal and Finance. |
| **Observed State** | Allocation model **documented** in `chargeback-model.json` with three layers: **Layer 1 — Direct attribution:** 91.7% of costs directly attributable via Pack 01 required tags (Owner, CostCenter, Project, Environment). Validated by querying Azure Cost Management grouped by each tag — results match Pack 01 compliance report. **Layer 2 — Shared cost distribution:** 6 shared resource categories identified with allocation methods: VNet/VPN (proportional by connected resource cost), Entra ID licensing (equal per user), Defender for Cloud (proportional by protected resource count), Key Vault (proportional by transactions), Log Analytics (proportional by ingestion volume), shared storage (proportional by data volume). Each method documented with rationale in `shared-cost-rules.json`. **Layer 3 — Untagged handling:** 8.3% untagged costs default to subscription-level cost center. Quarantine bucket configured to report untagged costs separately. Weekly escalation to engineering lead. **Model reviewed by Principal (Robert Myers). Finance stakeholder role not yet filled — lab environment has no independent finance function.** |
| **Evidence** | `chargeback-model.json`, `shared-cost-rules.json` |
| **FinOps Foundation** | Cost Allocation |
| **Status** | **Pass** |

---

### 2 — Direct Cost Attribution Operational

| Field | Detail |
|-------|--------|
| **Expected State** | Azure Cost Management group-by-tag producing accurate cost breakdowns for Owner, CostCenter, Project, and Environment. Results reconcile to subscription-level total. |
| **Observed State** | Cost Management group-by-tag **validated** across all 4 required tags: **By CostCenter:** CC-1001 (Engineering): $2,847/month (56.9%). CC-1002 (Data): $412/month (8.2%). CC-1003 (Operations): $287/month (5.7%). Untagged: $416/month (8.3%). Shared/platform: $1,038/month (20.8%). **Total: $5,000/month.** **By Project:** customer-portal: $1,823/month (36.5%). data-pipeline: $412/month (8.2%). internal-tools: $287/month (5.7%). infrastructure (shared): $1,038/month (20.8%). Untagged: $416/month (8.3%). Cross-project (reservations): $1,024/month (20.5%). **By Owner:** dev-team: $2,412/month (48.2%). data-team: $412/month (8.2%). ops-team: $287/month (5.7%). platform (shared): $1,038/month (20.8%). Untagged: $416/month (8.3%). reservations: $435/month (8.7%). **By Environment:** production: $3,100/month (62.0%). development: $1,200/month (24.0%). staging: $284/month (5.7%). Untagged: $416/month (8.3%). **Reconciliation:** Direct + shared + untagged = $5,000/month. Matches subscription-level total. No leakage. |
| **Evidence** | Cost Management exports, Screenshot #01 |
| **FinOps Foundation** | Cost Allocation |
| **Status** | **Pass** |

---

### 3 — Shared Cost Distribution Implemented

| Field | Detail |
|-------|--------|
| **Expected State** | `cost-allocation-engine.py` distributes shared costs across consuming teams using documented allocation methods. Distribution is transparent, reproducible, and auditable. |
| **Observed State** | `cost-allocation-engine.py` **operational.** Shared cost pool: $1,038/month distributed: **VNet/VPN Gateway ($312/month):** Distributed proportional to connected resource cost. CC-1001: $224 (71.8%). CC-1002: $56 (17.9%). CC-1003: $32 (10.3%). **Entra ID licensing ($148/month):** Distributed equal per user. 12 users across 3 cost centers. CC-1001: $74 (6 users). CC-1002: $37 (3 users). CC-1003: $37 (3 users). **Defender for Cloud ($312/month):** Distributed proportional to protected resource count. CC-1001: 47 resources → $218. CC-1002: 12 resources → $56. CC-1003: 8 resources → $38. **Key Vault ($48/month):** Distributed proportional to transaction count. CC-1001: 82% of transactions → $39. CC-1002: 12% → $6. CC-1003: 6% → $3. **Log Analytics ($156/month):** Distributed proportional to ingestion. CC-1001: 68% → $106. CC-1002: 22% → $34. CC-1003: 10% → $16. **Shared storage ($62/month):** Distributed proportional to data volume. CC-1001: $42. CC-1002: $14. CC-1003: $6. **After distribution — fully loaded cost per cost center:** CC-1001: $2,847 direct + $703 shared = $3,550 (71.0%). CC-1002: $412 direct + $203 shared = $615 (12.3%). CC-1003: $287 direct + $132 shared = $419 (8.4%). Untagged: $416 (8.3%). **$5,000 total. Zero leakage.** |
| **Evidence** | `cost-allocation-engine.py` output, Screenshot #03 |
| **FinOps Foundation** | Cost Allocation |
| **Status** | **Pass** |

---

### 4 — Showback Reports Generated and Distributed

| Field | Detail |
|-------|--------|
| **Expected State** | Monthly showback reports generated for each team/cost center showing: direct costs, shared cost allocation, total fully-loaded cost, top resources by spend, month-over-month trend, and budget status. Reports distributed to resource owners. |
| **Observed State** | `showback-report.py` **operational.** 4 weekly reports generated over 30-day assessment period. Sample monthly report (CC-1001 Engineering): **Summary:** Direct: $2,847. Shared: $703. Fully loaded: $3,550. Budget: $3,800. Variance: -$250 (6.6% under budget). **Top 5 resources:** (1) SQL Database $331, (2) App Service $270, (3) VM D4s_v5 $178, (4) Cosmos DB $137, (5) Log Analytics $106. **Trend:** January: $3,280. February (projected): $3,550 (+8.2%). Cause: new project resources (expected growth per Pack 02 disposition). **Distribution:** Reports emailed to cost center owner (weekly summary, monthly detail). **Finding:** Reports are generating and distributing. The format is clear and actionable. Engineering lead confirmed the showback report surfaced the weekend VM cost ($34.80) that Pack 02 also flagged — cross-pack visibility working. |
| **Evidence** | Sample showback report output, Screenshot #02 |
| **FinOps Foundation** | Showback / Chargeback |
| **Status** | **Pass** |

---

### 5 — Untagged Cost Quarantine Operational

| Field | Detail |
|-------|--------|
| **Expected State** | Untagged costs isolated in quarantine bucket. Weekly report identifies untagged resources with cost, creation date, and subscription. Escalation to engineering lead for tagging remediation. |
| **Observed State** | Quarantine bucket **operational.** Current quarantine: $416/month across 12 untagged resources (Pack 01 backfill targets). **Quarantine breakdown:** 3 resources owned by departed employee (Pack 01 hygiene scan finding): $89/month. 4 resources with missing CostCenter (unmapped to GL): $187/month. 2 resources candidate for decommission: $72/month. 3 Microsoft-managed resource groups (exempt from tagging): $68/month. **Weekly escalation:** Report sent to engineering lead each Monday. Week 1: 15 resources quarantined. Week 4: 12 resources (3 tagged during period). Trending down as Pack 01 backfill progresses. **Finding:** The quarantine makes untagged costs impossible to ignore. The departed employee's $89/month was invisible before quarantine — now it's highlighted weekly until resolved. The 3 Microsoft-managed RGs are documented exceptions (Pack 01 Control 10). |
| **Evidence** | Quarantine report, Screenshot #04 |
| **FinOps Foundation** | Cost Allocation |
| **Status** | **Pass** |

---

### 6 — Unit Economics Calculated

| Field | Detail |
|-------|--------|
| **Expected State** | Cost normalized against business metrics: cost per user, cost per transaction, cost per environment. Enables efficiency tracking over time. |
| **Observed State** | Unit economics **calculated** for available metrics: **Cost per user:** $5,000 total ÷ 12 active users = $416.67/user/month. Benchmark: varies widely by industry. Baseline established for trend tracking. **Cost per environment:** Production: $3,100 (62%). Development: $1,200 (24%). Staging: $284 (5.7%). Ratio production:development = 2.6:1. Industry benchmark for healthy ratio: 3:1 to 5:1. Our development environment is slightly heavy relative to production — potential optimization target for Pack 05. **Cost per project:** customer-portal: $1,823/month. data-pipeline: $412/month. internal-tools: $287/month. (Revenue attribution not available in lab — would enable cost-per-revenue in client environment.) **Finding:** Unit economics are baseline measurements. Their value is in the trend, not the absolute number. If cost per user increases while user count is flat, efficiency is degrading. If cost per transaction decreases while transactions grow, the platform is scaling efficiently. These metrics will become meaningful after 3+ months of data. |
| **Evidence** | Unit economics calculations in showback report |
| **FinOps Foundation** | Showback / Chargeback |
| **Status** | **Pass** |

---

### 7 — Budget vs Actual Tracking Operational

| Field | Detail |
|-------|--------|
| **Expected State** | Per-team monthly budget established. Actual spend tracked against budget. Variance analysis with explanation for over/under. Feeds Pack 02 budget threshold alerts. |
| **Observed State** | Budget vs actual **tracked** for 3 cost centers: **CC-1001 (Engineering):** Budget: $3,800. Actual: $3,550. Variance: -$250 (6.6% under). Status: ✅ healthy. **CC-1002 (Data):** Budget: $700. Actual: $615. Variance: -$85 (12.1% under). Status: ✅ healthy. **CC-1003 (Operations):** Budget: $500. Actual: $419. Variance: -$81 (16.2% under). Status: ✅ healthy. **Total:** Budget: $5,000. Actual: $4,584 (excluding untagged quarantine of $416). Variance: -$416 (8.3% under — the quarantine gap). **Finding:** All 3 cost centers are under budget. The $416 variance between allocated budget and attributed cost equals the untagged quarantine exactly. This confirms the quarantine is capturing the gap between what's budgeted and what's attributable. As Pack 01 tag compliance approaches 99%, the quarantine shrinks and budget vs actual closes to near-zero variance. |
| **Evidence** | `budget-vs-actual.json`, Screenshot #05 |
| **FinOps Foundation** | Showback / Chargeback |
| **Status** | **Pass** |

---

### 8 — Reservation Savings Attribution Completed

| Field | Detail |
|-------|--------|
| **Expected State** | Pack 03 projected reservation savings ($313/month) attributed to the teams and cost centers that benefit. Savings credited in showback reports. |
| **Observed State** | Savings attribution **configured** using Pack 01 tags on reserved resources: **CC-1001 (Engineering):** 3 reservations (SQL, App Service, VM). Projected savings: $279/month. Credited in showback report. **CC-1002 (Data):** 1 reservation (Cosmos DB). Projected savings: $34/month. Credited in showback report. **Finding:** Savings attribution requires the same tags that cost attribution requires. Because Pack 01 tags are on all 4 reservation candidates, the savings flow through the same allocation model. The team that benefits from the reservation sees the credit. **Note:** Actual vs projected attribution will validate when reservations are purchased (Pack 03 Control 10 dependency). |
| **Evidence** | Savings attribution in showback report |
| **FinOps Foundation** | Rate Optimization, Cost Allocation |
| **Status** | **Pass** |

---

### 9 — Chargeback-Ready Model Validated

| Field | Detail |
|-------|--------|
| **Expected State** | Allocation model produces outputs suitable for general ledger integration. Format compatible with standard financial systems. Cost center codes map to GL accounts. |
| **Observed State** | Allocation engine produces **GL-ready output:** Each line item includes: cost center, project, amount, allocation method (direct/shared/untagged), period, and GL account mapping placeholder. **Finding:** The output format is GL-ready but the GL integration is not configured. Lab environment does not have a financial system (QuickBooks, NetSuite, etc.) to receive the feed. The model is validated at the data layer — costs allocate correctly, shared costs distribute reproducibly, and the output format includes the fields a GL system would need. **Gap:** No financial system integration exists. In a client engagement, this would be the handoff to the finance team: "here is your monthly cost allocation file; map these cost center codes to your GL accounts." |
| **Status** | **Partial** — allocation model GL-ready but no financial system to integrate with |

---

### 10 — Cross-Pack Cost Traceability Validated End-to-End

| Field | Detail |
|-------|--------|
| **Expected State** | A single resource can be traced from Pack 01 (tag), through Pack 02 (anomaly if triggered), Pack 03 (reservation if applicable), Pack 04 (cost allocation), to Pack 05 (waste if identified). Full lifecycle cost traceability. |
| **Observed State** | **Traced the development VM (weekend anomaly) end-to-end:** Pack 01: Tagged `Owner: dev-team`, `Environment: development`, `CostCenter: CC-1001`, `Project: customer-portal`. ✅ Pack 02: Weekend anomaly detected ($34.80 on Saturday-Sunday). Dispositioned: Unexpected — waste. ✅ Pack 03: Fitness score 38/100 (development, weekday-only runtime, medium criticality). Recommendation: on-demand. ✅ Pack 04: Cost allocated to CC-1001, dev-team, customer-portal. Visible in showback report. ✅ Pack 05: Feed queued for waste elimination (auto-shutdown). ⏳ (Pack 05 not yet built) **Finding:** 4 of 5 packs traced successfully. Pack 05 is the final link. The cross-pack traceability works because Pack 01 tags create the common identifier. Without the `Owner` tag, Pack 04 couldn't attribute the cost. Without the `Environment` tag, Pack 03 couldn't score the fitness. Without the `CostCenter` tag, the showback report couldn't charge it. Tags are the connective tissue. |
| **Status** | **Fail** — 4 of 5 packs traced; Pack 05 (waste elimination) not yet built to complete the chain |

---

## Remediation Tracker

| # | Control | Finding | Owner | Remediation | Target Date | Status |
|---|---------|---------|-------|-------------|-------------|--------|
| 5 | Quarantine | $416/month untagged — 12 resources | R. Myers | Pack 01 backfill campaign | 2026-03-15 | Open |
| 9 | GL integration | No financial system for chargeback feed | R. Myers | Configure when finance system selected | When applicable | Open |
| 10 | End-to-end trace | Pack 05 not yet built | R. Myers | Build Pack 05 to complete chain | Next pack | Open |

---

## Watchstander Notes

1. **$416/month in untagged costs is the cost of incomplete governance.** That's $4,992/year that nobody officially owns. It's not lost — it's in the quarantine — but it's unattributed. Every dollar in quarantine is a dollar that a team incurred but isn't being held accountable for. The quarantine makes the problem visible. Pack 01 tag enforcement makes it shrink. The goal is $0 in quarantine. We're at $416 and trending down.

2. **Shared cost distribution is where most chargeback programs fail.** Teams accept direct cost attribution — "I provisioned the VM, I own the cost." They resist shared cost allocation — "Why am I paying for the VPN gateway? I didn't ask for it." The answer is documented in `shared-cost-rules.json` with a rationale for every method. Proportional by connected resource cost is defensible because the team with more compute generates more network traffic. Equal per user for licensing is defensible because each user consumes one license. The rationale matters because the first time a team disputes their shared allocation, you need the documented justification.

3. **The development-to-production ratio of 2.6:1 is a signal.** Industry benchmarks suggest 3:1 to 5:1. Our development environment is consuming 24% of total spend — slightly heavy for a lab with limited development activity. This feeds Pack 05 directly. The question is: "Is 24% of spend in development justified by the development activity?" If yes, the ratio is healthy. If the development environment is running production-sized resources for intermittent use, it's waste. Pack 05 will answer this.

4. **Showback before chargeback is the right maturity path.** Chargeback requires finance integration, GL mapping, and organizational buy-in. Showback requires tags and a report. Start with visibility. Let teams see what they spend. The behavior change often happens at showback — when an engineering lead sees that their sandbox costs $800/month, they ask "why?" without needing a formal chargeback to motivate the question. Chargeback formalizes what showback initiates.

5. **Zero leakage in the allocation proves the model is sound.** Direct ($4,584) + untagged quarantine ($416) = $5,000 total subscription cost. No cost is lost. No cost is double-counted. No cost is attributed to the wrong team. The allocation engine is a conservation-of-mass exercise — every dollar that enters the subscription exits through attribution, shared distribution, or quarantine. Zero leakage is the proof that the model is complete.

---

*Assessment conducted by Robert Myers, MBA | SailPoint ISL, Security+, CCSK, CC*
*Stella Maris Governance — 2026*
