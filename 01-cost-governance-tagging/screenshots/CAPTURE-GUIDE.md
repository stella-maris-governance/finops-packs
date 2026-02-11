# Screenshot Capture Guide — Cost Governance & Tagging

---

### 01 — Azure Policy Assignments
**Path:** Azure Portal > Policy > Assignments
**Show:** All 4 tag policies deployed with scope and effect

### 02 — Tag Compliance Dashboard
**Path:** `tag-compliance-report.py` output or Azure Portal > Policy > Compliance
**Show:** Required and recommended compliance percentages

### 03 — Policy Deny Event
**Path:** Azure Activity Log filtered to Policy deny
**Show:** Resource creation blocked for missing required tags

### 04 — Cost Management Group-by-Tag
**Path:** Azure Portal > Cost Management > Cost Analysis > Group by Tag
**Show:** Cost breakdown by Owner or Environment tag

### 05 — Tag Hygiene Scan
**Path:** `tag-hygiene-scan.py` output
**Show:** Orphan owner finding or expired resource finding
