# Screenshot Capture Guide — Anomaly Detection & Cost Alerting

---

### 01 — Budget Configuration
**Path:** Azure Portal > Cost Management > Budgets
**Show:** Budget with 4 threshold alerts configured

### 02 — Anomaly Detection
**Path:** Azure Cost Management anomaly view or `anomaly-detection.py` output
**Show:** Cost spike identified with investigation annotation

### 03 — Tag-Category Alert
**Path:** Alert log or dashboard
**Show:** Sandbox or environment cost threshold alert

### 04 — Resource-Level Spike
**Path:** `resource-spike-scan.py` output
**Show:** Individual resource with cost anomaly and owner attribution

### 05 — Alert Register
**Path:** `alert-register.json` or dashboard
**Show:** Triage log with dispositions (expected, waste, growth)
