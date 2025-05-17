# PowerShell Test Runner for CodeCritic

# Ensure we're in the project root
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Set PYTHONPATH to include current directory
$env:PYTHONPATH = "."

# 1) Run pytest to execute tests and collect coverage data
pytest `
  tests `
  --cov=app `
  --disable-warnings `
  --maxfail=3 `
  --tb=short

# 2) Print a terminal report for only those files missing coverage
coverage report -m --skip-covered

# 3) Generate the HTML report
coverage html

# 4) Print path in a browser-friendly format
$reportPath = (Resolve-Path "htmlcov/index.html").Path
$fileUri    = "file:///" + ($reportPath -replace '\\','/')

Write-Host ""
Write-Host "HTML coverage report:"
Write-Host "  $fileUri  ← Copy & paste this into your browser"
