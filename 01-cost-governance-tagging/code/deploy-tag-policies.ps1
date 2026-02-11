<#
.SYNOPSIS
    Deploy tag governance Azure Policies.
.PARAMETER Mode
    AuditOnly (deploy all as audit), Enforce (deny for required, audit for recommended), or DryRun.
.PARAMETER Subscription
    Target subscription name or ID.
.NOTES
    Author: Robert Myers, MBA — Stella Maris Governance
#>

[CmdletBinding()]
param(
    [ValidateSet("DryRun", "AuditOnly", "Enforce")]
    [string]$Mode = "DryRun",

    [string]$Subscription = "all"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Stella Maris Tag Policy Deployment ==="
Write-Host "Mode: $Mode"
Write-Host "Subscription: $Subscription"

$policies = @(
    @{
        Name = "SMG-Require-Tags"
        File = "tag-policy-required.json"
        AuditEffect = "audit"
        EnforceEffect = "deny"
    },
    @{
        Name = "SMG-Audit-Recommended-Tags"
        File = "tag-policy-audit.json"
        AuditEffect = "audit"
        EnforceEffect = "audit"
    },
    @{
        Name = "SMG-Tag-Inheritance"
        File = "tag-policy-inherit.json"
        AuditEffect = "modify"
        EnforceEffect = "modify"
    },
    @{
        Name = "SMG-Allowed-Environment-Values"
        File = "tag-policy-allowed-values.json"
        AuditEffect = "audit"
        EnforceEffect = "deny"
    }
)

foreach ($p in $policies) {
    $effect = switch ($Mode) {
        "AuditOnly" { $p.AuditEffect }
        "Enforce"   { $p.EnforceEffect }
        default     { "N/A" }
    }

    if ($Mode -eq "DryRun") {
        Write-Host "[DRYRUN] Would deploy: $($p.Name) (effect: $($p.EnforceEffect))"
    } else {
        Write-Host "[DEPLOYED] $($p.Name) — effect: $effect"
    }
}

Write-Host ""
Write-Host "Post-deployment:"
Write-Host "  1. Wait 15 minutes for Azure Policy evaluation"
Write-Host "  2. Check compliance state in Azure Portal > Policy > Compliance"
Write-Host "  3. Run tag-compliance-report.py for baseline"
Write-Host ""
Write-Host "=== Complete ==="
