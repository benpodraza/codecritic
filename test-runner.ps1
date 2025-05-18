# Step 1: Run black formatting check
Write-Host "Running black check..."
black --check .
if ($LASTEXITCODE -ne 0) { exit 1 }

# Step 2: Run tests with coverage (and tee output so it's visible)
Write-Host "`nRunning pytest with coverage..."
pytest tests --cov=app --cov-report=term --cov-report=html | Tee-Object -FilePath coverage_output.txt

# Step 3: Re-display all coverage report lines to the terminal
Write-Host "`nFull coverage report:"
Get-Content coverage_output.txt | ForEach-Object { Write-Host $_ }

# Step 4: Filter files with <100% coverage and >0 lines
Write-Host "`nFiles with less than 100% coverage:"
Get-Content coverage_output.txt | Where-Object {
    $_ -match '^\s*app.*\s+\d+%\s+\d+\s+\d+'
} | ForEach-Object {
    $columns = ($_ -split '\s+')
    $filename = $columns[0]
    $coverage = [int]($columns[1] -replace "%", "")
    $lines = [int]$columns[2]
    $missing = $columns[3]
    if ($coverage -lt 100 -and $lines -gt 0) {
        Write-Host "$filename - $coverage% covered, missing lines: $missing"
    }
}

# Step 5: Print command to open HTML report (but do not run it)
$htmlPath = Join-Path -Path (Get-Location) -ChildPath "htmlcov/index.html"
Write-Host "`nTo open the full report in your browser, run:"
Write-Host "Start-Process `"$htmlPath`""
