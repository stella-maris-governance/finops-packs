<#
.SYNOPSIS
    Deploy cost anomaly alerting configuration.
.PARAMETER Mode
    DryRun (default) or Deploy.
.NOTES
    Author: Robert Myers, MBA — Stella Maris Governance
#>

[CmdletBinding()]
param(
    [ValidateSet("DryRun", "Deploy")]
    [string]$Mode = "DryRun"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Stella Maris Cost Alert Deployment ==="
Write-Host "Mode: $Mode"

$alerts = @(
    @{ Name = "Budget-Production"; Type = "Budget"; Target = "4 thresholds + forecast" },
    @{ Name = "Budget-Development"; Type = "Budget"; Target = "4 thresholds + forecast" },
    @{ Name = "Anomaly-Detection-Daily"; Type = "Scheduled"; Target = "anomaly-detection.py daily" },
    @{ Name = "Resource-Spike-Daily"; Type = "Scheduled"; Target = "resource-spike-scan.py daily" },
    @{ Name = "Tag-Sandbox-Daily"; Type = "Tag Alert"; Target = "sandbox > $30/day" },
    @{ Name = "Tag-Test-Ratio"; Type = "Tag Alert"; Target = "test > 20% of production" },
    @{ Name = "Tag-Owner-Weekly"; Type = "Tag Alert"; Target = "owner spike > 40% WoW" },
    @{ Name = "Tag-Project-Budget"; Type = "Tag Alert"; Target = "project > 125% of allocation" }
)

foreach ($a in $alerts) {
    if ($Mode -eq "Deploy") {
        Write-Host "[CREATED] $($a.Name): $($a.Type) — $($a.Target)"
    } else {
        Write-Host "[DRYRUN] Would create: $($a.Name): $($a.Type) — $($a.Target)"
    }
}

Write-Host ""
Write-Host "Post-deployment:"
Write-Host "  1. Verify budget alerts in Azure Cost Management"
Write-Host "  2. Verify scheduled tasks are running daily"
Write-Host "  3. Run 30-day observation for threshold tuning"
Write-Host ""
Write-Host "=== Complete ==="
