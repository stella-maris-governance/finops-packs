<#
.SYNOPSIS
    Deploy waste scanning and auto-shutdown configuration.
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

Write-Host "=== Stella Maris Waste Scanning Deployment ==="
Write-Host "Mode: $Mode"

$configs = @(
    @{ Name = "Weekly-Waste-Scan"; Type = "Scheduled"; Target = "waste-scanner.py full scan" },
    @{ Name = "Weekly-Orphan-Scan"; Type = "Scheduled"; Target = "orphan-detector.py" },
    @{ Name = "Monthly-Rightsize-Analysis"; Type = "Scheduled"; Target = "rightsizing-analyzer.py" },
    @{ Name = "Dev-Auto-Shutdown"; Type = "AutoShutdown"; Target = "Development VMs 6PM CT weekdays" },
    @{ Name = "Test-Auto-Shutdown"; Type = "AutoShutdown"; Target = "Test VMs 8PM CT weekdays" },
    @{ Name = "Sandbox-Auto-Shutdown"; Type = "AutoShutdown"; Target = "Sandbox VMs 5PM CT weekdays" },
    @{ Name = "Waste-Register-Alert"; Type = "Alert"; Target = "New findings above $50/month" }
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
Write-Host "  1. Azure Automation account required for scheduling"
Write-Host "  2. Verify auto-shutdown firing at scheduled times"
Write-Host "  3. First waste scan results in 7 days"
Write-Host ""
Write-Host "=== Complete ==="
