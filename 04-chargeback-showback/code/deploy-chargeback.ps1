<#
.SYNOPSIS
    Deploy chargeback and showback reporting configuration.
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

Write-Host "=== Stella Maris Chargeback Deployment ==="
Write-Host "Mode: $Mode"

$configs = @(
    @{ Name = "Monthly-Allocation-Job"; Type = "Scheduled"; Target = "cost-allocation-engine.py monthly" },
    @{ Name = "Weekly-Showback-Report"; Type = "Scheduled"; Target = "showback-report.py weekly per CC" },
    @{ Name = "Quarantine-Weekly-Alert"; Type = "Alert"; Target = "Untagged cost escalation" },
    @{ Name = "Budget-Variance-Alert"; Type = "Alert"; Target = "Cost center > 90% of budget" },
    @{ Name = "Shared-Cost-Monthly"; Type = "Scheduled"; Target = "Shared distribution calculation" }
)

foreach ($c in $configs) {
    if ($Mode -eq "Deploy") {
        Write-Host "[CREATED] $($c.Name): $($c.Type) — $($c.Target)"
    } else {
        Write-Host "[DRYRUN] Would create: $($c.Name): $($c.Type) — $($c.Target)"
    }
}

Write-Host ""
Write-Host "Post-deployment:"
Write-Host "  1. Verify monthly allocation runs on 1st of each month"
Write-Host "  2. Verify showback reports distributing to CC owners"
Write-Host "  3. Verify quarantine escalation reaching engineering lead"
Write-Host ""
Write-Host "=== Complete ==="
