$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendEntry = Join-Path $ProjectDir "backend\sign_recognition_api.py"
$RequirementsFile = Join-Path $ProjectDir "backend\requirements.txt"
$VenvDir = Join-Path $ProjectDir ".venv"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
$RuntimeDir = Join-Path $ProjectDir ".runtime"
$PidFile = Join-Path $RuntimeDir "server.pid"
$PortFile = Join-Path $RuntimeDir "server.port"
$UrlFile = Join-Path $RuntimeDir "server.url"
$StdoutLog = Join-Path $RuntimeDir "server.out.log"
$StderrLog = Join-Path $RuntimeDir "server.err.log"
$CandidatePorts = @(5001, 5002, 5003, 5004, 5005, 5010)

function Write-Step([string]$Message) {
  Write-Host "[INFO] $Message"
}

function Write-Fail([string]$Message) {
  Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-LocalPortInUse([int]$Port) {
  $client = New-Object System.Net.Sockets.TcpClient
  try {
    $async = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
    $success = $async.AsyncWaitHandle.WaitOne(300, $false)
    if (-not $success) {
      return $false
    }
    $client.EndConnect($async) | Out-Null
    return $true
  } catch {
    return $false
  } finally {
    $client.Close()
  }
}

function Stop-ProjectPythonProcesses() {
  if (Test-Path $PidFile) {
    $savedPid = Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($savedPid -match '^\d+$') {
      Stop-Process -Id ([int]$savedPid) -Force -ErrorAction SilentlyContinue
    }
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
  }

  $escapedBackendEntry = [regex]::Escape($BackendEntry)
  $pythonProcesses = Get-CimInstance Win32_Process | Where-Object {
    ($_.Name -in @("python.exe", "pythonw.exe")) -and
    $_.CommandLine -and
    ($_.CommandLine -match $escapedBackendEntry)
  }

  foreach ($process in $pythonProcesses) {
    Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
  }

  Remove-Item $PortFile, $UrlFile -Force -ErrorAction SilentlyContinue
}

function Get-AvailablePort() {
  foreach ($port in $CandidatePorts) {
    if (-not (Test-LocalPortInUse -Port $port)) {
      return $port
    }
  }

  throw "No available port found in candidate list."
}

function Wait-ForServer([string]$Url) {
  for ($i = 0; $i -lt 30; $i++) {
    try {
      $response = Invoke-WebRequest -Uri "$Url/api/health" -UseBasicParsing -TimeoutSec 2
      if ($response.StatusCode -eq 200) {
        return $true
      }
    } catch {
      Start-Sleep -Seconds 1
    }
  }

  return $false
}

function Ensure-PythonCommand() {
  if (Get-Command py -ErrorAction SilentlyContinue) {
    return @("py", "-3")
  }

  if (Get-Command python -ErrorAction SilentlyContinue) {
    return @("python")
  }

  throw "Python 3 not found. Install Python 3 first."
}

function Invoke-PythonCommand([string[]]$Args) {
  if ($pythonCommand.Length -gt 1) {
    & $pythonCommand[0] $pythonCommand[1] @Args
  } else {
    & $pythonCommand[0] @Args
  }
}

Set-Location $ProjectDir
New-Item -ItemType Directory -Path $RuntimeDir -Force | Out-Null

Write-Step "Stopping previous project services"
Stop-ProjectPythonProcesses

$pythonCommand = Ensure-PythonCommand

if (-not (Test-Path $PythonExe)) {
  Write-Step "Creating virtual environment"
  Invoke-PythonCommand -Args @("-m", "venv", $VenvDir)
}

if (-not (Test-Path $PythonExe)) {
  throw "Virtual environment creation failed."
}

Write-Step "Installing backend dependencies"
& $PythonExe -m pip install --upgrade pip
& $PythonExe -m pip install -r $RequirementsFile

if (-not (Test-Path (Join-Path $ProjectDir "dist\index.html"))) {
  throw "dist\index.html not found. Build the frontend before shipping to Windows."
}

$port = Get-AvailablePort
$serverUrl = "http://127.0.0.1:$port"

Write-Step "Starting server on $serverUrl"
$env:PORT = "$port"
$env:FLASK_DEBUG = "0"
$serverProcess = Start-Process -FilePath $PythonExe `
  -ArgumentList @($BackendEntry) `
  -WorkingDirectory $ProjectDir `
  -RedirectStandardOutput $StdoutLog `
  -RedirectStandardError $StderrLog `
  -PassThru

$serverProcess.Id | Set-Content -Path $PidFile -Encoding ASCII
$port | Set-Content -Path $PortFile -Encoding ASCII
$serverUrl | Set-Content -Path $UrlFile -Encoding ASCII

if (-not (Wait-ForServer -Url $serverUrl)) {
  Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
  Write-Fail "Server startup timed out."
  Write-Host "Check logs:"
  Write-Host "  $StdoutLog"
  Write-Host "  $StderrLog"
  exit 1
}

Write-Host ""
Write-Host "Server is ready: $serverUrl" -ForegroundColor Green
Write-Host "PID: $($serverProcess.Id)"
Write-Host "Logs:"
Write-Host "  $StdoutLog"
Write-Host "  $StderrLog"

Start-Process $serverUrl | Out-Null
exit 0
