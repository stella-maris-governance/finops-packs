# Waste Elimination & Right-Sizing Operations Runbook

> **Version:** 1.0.0 | **Author:** Robert Myers, MBA | Stella Maris Governance

---

## 1. Purpose

Systematic identification and elimination of cloud waste across 6 categories. Every idle resource gets a decision. Every decision gets tracked. Every savings gets verified.

---

## 2. Weekly Scan Cycle

| Day | Action | Tool |
|-----|--------|------|
| Monday | Full waste scan (all 6 categories) | `waste-scanner.py` |
| Monday | Orphan detection | `orphan-detector.py` |
| Tuesday | New findings triaged and dispositioned | Manual review |
| Wednesday | Remediation actions executed (orphans, idle) | Azure portal / CLI |
| Thursday | Right-sizing analysis (monthly) | `rightsizing-analyzer.py` |
| Friday | Register updated, metrics reported | `waste-register.json` |

---

## 3. Disposition Decision Framework

For each finding, ask in order:

1. **Is anyone using this resource?** → No → Decommission
2. **Is it the right size?** → Too big → Right-size
3. **Does it need to run 24/7?** → No → Schedule
4. **Is there a valid business reason to keep it as-is?** → Document justification
5. **Can we act now?** → No → Defer with date

---

## 4. Right-Sizing Safety Protocol

**Non-production:**
1. Confirm current utilization (P95, not average)
2. Identify target SKU
3. Resize during business hours (low risk)
4. Monitor 48 hours post-resize
5. Update waste register with confirmed savings

**Production:**
1. Confirm utilization over 30+ days (P95)
2. Identify target SKU with 20% headroom
3. Schedule change window
4. Prepare rollback plan (resize back to original)
5. Resize during maintenance window
6. Monitor 72 hours post-resize
7. If degradation detected: rollback immediately
8. If stable: update register with confirmed savings

---

## 5. Auto-Shutdown Management

| Environment | Schedule | Override Process |
|------------|----------|-----------------|
| Development | 8am-6pm weekdays | Tag `KeepRunning: true` to exempt |
| Test | 7am-8pm weekdays | Tag `KeepRunning: true` to exempt |
| Sandbox | 9am-5pm weekdays | Tag `KeepRunning: true` to exempt |
| Staging | 6am-10pm daily | Deployment windows override |
| Production | 24/7 | N/A — never auto-shutdown |

Override tags are reviewed weekly. Permanent `KeepRunning` tags require justification.

---

## 6. Metrics and Reporting

Monthly report to Principal:

| Metric | Target |
|--------|--------|
| Total waste identified | Decreasing month-over-month |
| Waste as % of total spend | < 15% (industry: 20-35%) |
| Findings remediated within SLA | > 80% |
| Orphan count | Trending to zero |
| Auto-shutdown coverage | 100% of non-production compute |
| Confirmed savings vs projected | Within 20% variance |

---

*Stella Maris Governance — 2026*
