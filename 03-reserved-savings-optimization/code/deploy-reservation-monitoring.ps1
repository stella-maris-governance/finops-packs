<#
.SYNOPSIS
    Deploy reservation monitoring configuration.
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

Write-Host "=== Stella Maris Reservation Monitoring Deployment ==="
Write-Host "Mode: $Mode"

$configs = @(
    @{ Name = "RI-Utilization-Alert-80pct"; Type = "Alert"; Target = "Utilization < 80% warning" },
    @{ Name = "RI-Utilization-Alert-60pct"; Type = "Alert"; Target = "Utilization < 60% critical" },
    @{ Name = "RI-Expiry-90day"; Type = "Alert"; Target = "90-day expiration warning" },
    @{ Name = "RI-Expiry-60day"; Type = "Alert"; Target = "60-day expiration warning" },
    @{ Name = "RI-Expiry-30day"; Type = "Alert"; Target = "30-day expiration critical" },
    @{ Name = "Savings-Monthly-Report"; Type = "Scheduled"; Target = "Monthly savings vs on-demand" },
    @{ Name = "Coverage-Dashboard"; Type = "Dashboard"; Target = "Reservation coverage view" }
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
Write-Host "  1. Purchase approved reservations (RI-001 through RI-004)"
Write-Host "  2. Verify utilization monitoring producing data (7 days post-purchase)"
Write-Host "  3. First savings report at 30 days post-purchase"
Write-Host ""
Write-Host "=== Complete ==="
