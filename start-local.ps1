$ErrorActionPreference = 'Stop'

$projectRoot = $PSScriptRoot
$backendRoot = Join-Path $projectRoot 'backend'
$frontendRoot = Join-Path $projectRoot 'frontend'
$backendPython = Join-Path $backendRoot 'venv\bin\python.exe'
$frontendNpm = 'npm.cmd'
$apiUrl = 'http://127.0.0.1:8000/health'
$appUrl = 'http://127.0.0.1:5173/'

function Test-LocalUrl {
  param([Parameter(Mandatory)] [string] $Url)

  try {
    return (Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2).StatusCode -eq 200
  } catch {
    return $false
  }
}

function Wait-ForUrl {
  param([Parameter(Mandatory)] [string] $Url, [int] $TimeoutSeconds = 30)

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    if (Test-LocalUrl -Url $Url) { return $true }
    Start-Sleep -Milliseconds 500
  }
  return $false
}

if (-not (Test-Path $backendPython)) {
  throw "Backend Python environment was not found at $backendPython."
}

if (-not (Test-Path (Join-Path $frontendRoot 'node_modules'))) {
  Write-Host 'Installing frontend dependencies...'
  Push-Location $frontendRoot
  try { & $frontendNpm install --cache .npm-cache } finally { Pop-Location }
}

if (-not (Test-Path (Join-Path $frontendRoot 'dist\index.html'))) {
  Write-Host 'Building frontend...'
  Push-Location $frontendRoot
  try { & $frontendNpm run build --cache .npm-cache } finally { Pop-Location }
}

if (-not (Test-LocalUrl -Url $apiUrl)) {
  Start-Process -FilePath $backendPython `
    -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000') `
    -WorkingDirectory $backendRoot `
    -WindowStyle Hidden
}

if (-not (Test-LocalUrl -Url $appUrl)) {
  Start-Process -FilePath $frontendNpm `
    -ArgumentList @('run', 'preview', '--', '--host', '127.0.0.1', '--port', '5173') `
    -WorkingDirectory $frontendRoot `
    -WindowStyle Hidden
}

$apiReady = Wait-ForUrl -Url $apiUrl
$appReady = Wait-ForUrl -Url $appUrl

if (-not ($apiReady -and $appReady)) {
  throw 'The local services did not start within 30 seconds. Run this script from PowerShell to see diagnostics.'
}

try {
  Start-Process $appUrl
} catch {
  Write-Host "Open $appUrl in your browser."
}
Write-Host "AutoPersona is running at $appUrl"
