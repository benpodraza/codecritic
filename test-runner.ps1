# PowerShell Test Runner for CodeCritic

# Ensure we're in the project root
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Set PYTHONPATH to include current directory
$env:PYTHONPATH = "."

# Run pytest with full coverage detail
pytest `
  tests `
  --cov=app `
  --cov-report=term-missing `
  --cov-report=html `
  --disable-warnings `
  --maxfail=3 `
  --tb=short

# Print path in a browser-friendly format
$reportPath = (Resolve-Path "htmlcov/index.html").Path
$fileUri = "file:///" + ($reportPath -replace '\\', '/')

Write-Host "HTML coverage report:"
Write-Host "$fileUri  ← Copy and paste this into your browser"