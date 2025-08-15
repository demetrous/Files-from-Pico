# Creates the Pico W Tiny Server asset tree and downloads local copies of CSS/JS/images.
# Usage:
#   Right-click -> Run with PowerShell
#   (or) powershell -NoProfile -ExecutionPolicy Bypass -File ".\create_pico_assets.ps1" "C:\my\root\folder"

param(
  [string]$Root
)

# Default root next to script if not provided
if (-not $Root) {
  if ($PSScriptRoot) { $Root = Join-Path -Path $PSScriptRoot -ChildPath 'pico_tiny_server' }
  else { $Root = Join-Path -Path (Get-Location) -ChildPath 'pico_tiny_server' }
}

# Prefer TLS 1.2 for Invoke-WebRequest on older Windows
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}

# Create directories
$subdirs = @('static\css', 'static\js', 'static\assets')
foreach ($sd in $subdirs) {
  $full = Join-Path -Path $Root -ChildPath $sd
  New-Item -ItemType Directory -Force -Path $full | Out-Null
}

# Files to fetch (hero image renamed to raspberry.jpg to match your server code)
$files = @(
  @{ Url = 'https://cdn.jsdelivr.net/gh/demetrous/tiny-server-assets/css/styles.css'; Out = 'static\css\styles.css' },
  @{ Url = 'https://cdn.jsdelivr.net/gh/demetrous/tiny-server-assets/js/bootstrap.bundle.min.js'; Out = 'static\js\bootstrap.bundle.min.js' },
  @{ Url = 'https://cdn.jsdelivr.net/gh/demetrous/tiny-server-assets/js/scripts.js'; Out = 'static\js\scripts.js' },
  @{ Url = 'https://cdn.jsdelivr.net/gh/demetrous/tiny-server-assets/assets/favicon.ico'; Out = 'static\assets\favicon.ico' },
  @{ Url = 'https://cdn.jsdelivr.net/gh/demetrous/tiny-server-assets/assets/raspberry-pi-pico-w-hand.jpg'; Out = 'static\assets\raspberry.jpg' }
)

foreach ($f in $files) {
  $out = Join-Path -Path $Root -ChildPath $f.Out
  try {
    Invoke-WebRequest -Uri $f.Url -OutFile $out -UseBasicParsing -TimeoutSec 60
    Write-Host "Downloaded -> $($f.Out)"
  }
  catch {
    Write-Warning "Failed to download $($f.Url). Creating placeholder: $($f.Out)"
    New-Item -ItemType File -Force -Path $out | Out-Null
  }
}

# Write a quick README
$readmePath = Join-Path -Path $Root -ChildPath 'README.txt'
@"
How to use:

1) In Thonny, connect to the Pico W.
2) Upload the 'static' folder from:
   $Root
3) Run your Microdot server that serves /static (the code you have).
"@ | Set-Content -Path $readmePath -Encoding UTF8

Write-Host ""
Write-Host "All set. Root: $Root"
