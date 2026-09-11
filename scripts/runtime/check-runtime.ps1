#Requires -Version 5.1
<#
.SYNOPSIS
    FARIA RF-01 runtime check (Windows/PowerShell).

.DESCRIPTION
    Verifies what can be verified automatically for the Hermes -> 9Router ->
    model runtime path, without ever printing secret values. Read
    scripts/runtime/README.md for the manual checks (normal chat, Telegram,
    unauthorized identity) this script cannot safely automate.

    This script does not fabricate success: any check that cannot run is
    reported as BLOCKED_BY_LOCAL_CONFIGURATION with the exact missing
    prerequisite, never silently skipped or marked as passing.
#>

param(
    [string]$EnvFile = (Join-Path $PSScriptRoot "..\..\.env")
)

$ErrorActionPreference = "Stop"
$results = @()

function Add-Result([string]$Check, [string]$Status, [string]$Detail) {
    $script:results += [PSCustomObject]@{ Check = $Check; Status = $Status; Detail = $Detail }
}

# --- Load .env (local only; values are never echoed) ------------------------
$envVars = @{}
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith('#') -or ($line.IndexOf('=') -lt 0)) { return }
        $idx = $line.IndexOf('=')
        $key = $line.Substring(0, $idx).Trim()
        $val = $line.Substring($idx + 1).Trim()
        $envVars[$key] = $val
    }
} else {
    Add-Result ".env present" "BLOCKED_BY_LOCAL_CONFIGURATION" "Missing $EnvFile. Copy .env.example to .env in the repo root and fill in real values, then re-run this script."
}

# --- Check A: 9Router reachability ------------------------------------------
$routerUrl = $envVars["ROUTER9_BASE_URL"]
if (-not $routerUrl) {
    Add-Result "A: 9Router reachability" "BLOCKED_BY_LOCAL_CONFIGURATION" "ROUTER9_BASE_URL is not set in .env. Set it to your running 9Router base URL (see .env.example)."
} else {
    $probeUrl = $routerUrl.TrimEnd('/') + "/models"
    try {
        $resp = Invoke-WebRequest -Uri $probeUrl -TimeoutSec 5 -UseBasicParsing
        Add-Result "A: 9Router reachability" "PASS" "GET $probeUrl -> HTTP $($resp.StatusCode)"
    } catch {
        Add-Result "A: 9Router reachability" "BLOCKED_BY_LOCAL_CONFIGURATION" "Could not reach $probeUrl. Confirm 9Router is running and ROUTER9_BASE_URL is correct for this host. Error: $($_.Exception.Message)"
    }
}

# --- Check B: Hermes container running --------------------------------------
$dockerAvailable = $true
try {
    docker version --format '{{.Server.Version}}' *> $null
    if ($LASTEXITCODE -ne 0) { $dockerAvailable = $false }
} catch {
    $dockerAvailable = $false
}

if (-not $dockerAvailable) {
    Add-Result "B: Hermes container running" "BLOCKED_BY_LOCAL_CONFIGURATION" "Docker is not available on this machine/shell. Install/start Docker Desktop, then run: docker compose -f infra/docker/compose.yaml --env-file .env up -d gateway"
} else {
    $status = (docker ps --filter "name=faria-hermes-gateway" --format "{{.Status}}") -join ""
    if (-not $status) {
        Add-Result "B: Hermes container running" "BLOCKED_BY_LOCAL_CONFIGURATION" "Container 'faria-hermes-gateway' is not running. From the repo root run: docker compose -f infra/docker/compose.yaml --env-file .env up -d gateway"
    } else {
        Add-Result "B: Hermes container running" "PASS" "faria-hermes-gateway: $status"
    }
}

# --- Checks C/D/E: require real credentials / human judgment ----------------
Add-Result "C: Normal Hermes chat" "MANUAL_STEP_REQUIRED" "No verified scripted one-shot CLI syntax was found in current Hermes docs. Follow 'Check C' in scripts/runtime/README.md (docker exec -it faria-hermes-gateway hermes, then send the smoke prompt interactively)."
Add-Result "D: Telegram gateway" "MANUAL_STEP_REQUIRED" "Requires a real allowlisted Telegram account. Follow 'Check D' in scripts/runtime/README.md."
Add-Result "E: Unauthorized identity rejected" "MANUAL_STEP_REQUIRED" "Requires a second, non-allowlisted Telegram account. Follow 'Check E' in scripts/runtime/README.md. Do not weaken the allowlist to make this easier to test."

$results | Format-Table -AutoSize -Wrap

$blocked = $results | Where-Object { $_.Status -eq "BLOCKED_BY_LOCAL_CONFIGURATION" }
if ($blocked) {
    Write-Host ""
    Write-Host "RF-01 PARTIALLY READY: $($blocked.Count) automated check(s) are BLOCKED_BY_LOCAL_CONFIGURATION." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host ""
    Write-Host "Automated checks passed. Continue with the manual checks (C, D, E) in scripts/runtime/README.md." -ForegroundColor Green
    exit 0
}
