# Requires PowerShell 5.0+
# Downloads files listed in data_sources.yml into data_sources.cache if not already present

$yamlPath = "data_sources\data_sources.yml"
$cacheDir = "data_sources"

# Ensure the cache directory exists
if (-not (Test-Path $cacheDir)) {
    New-Item -ItemType Directory -Path $cacheDir | Out-Null
}

# Read YAML file
$yaml = Get-Content $yamlPath -Raw

# Parse YAML for URLs (simple regex for lines like: url: ...)
$entries = @()
$lines = $yaml -split "`n"
$url = $null
foreach ($line in $lines) {
    if ($line -match "^\s*url:\s*(.+)$") {
        $url = $Matches[1].Trim().Trim('"')
        # Extract filename from URL using string manipulation
        $filename = $url.Substring($url.LastIndexOf('/') + 1)
        if ($filename) {
            $entries += [PSCustomObject]@{ Url = $url; Filename = $filename }
        }
        $url = $null
    }
}

foreach ($i in 0..($entries.Count - 1)) {
    $entry = $entries[$i]
    $targetPath = Join-Path $cacheDir $entry.Filename
    if (-not (Test-Path $targetPath)) {
        Write-Host "Downloading $($entry.Url) to $targetPath using Edge..."
        $edgeProc = Start-Process "msedge.exe" $entry.Url -PassThru
        $downloadPath = Join-Path ([Environment]::GetFolderPath("UserProfile")) "Downloads" | Join-Path -ChildPath $entry.Filename
        Write-Host "Waiting for $($entry.Filename) to appear in Downloads..."
        while (-not (Test-Path $downloadPath)) {
            Start-Sleep -Seconds 2
        }
        # Close the Edge process (tab) after download
        if ($edgeProc -and !$edgeProc.HasExited) {
            try {
                Stop-Process -Id $edgeProc.Id -Force -ErrorAction SilentlyContinue
                if (Get-Process -Id $edgeProc.Id -ErrorAction SilentlyContinue) {
                    Write-Host "Closed Edge tab for $($entry.Filename)"
                } else {
                    Write-Host "Edge process for $($entry.Filename) was already closed."
                }
            } catch {
                Write-Host "Could not close Edge process (it may have already exited): $_"
            }
        }
        Copy-Item $downloadPath $targetPath -Force
        Write-Host "Copied $($entry.Filename) to $targetPath"
        # Wait 60 seconds only if another file still needs to be downloaded
        $remaining = $false
        for ($j = $i + 1; $j -lt $entries.Count; $j++) {
            $nextTarget = Join-Path $cacheDir $entries[$j].Filename
            if (-not (Test-Path $nextTarget)) {
                $remaining = $true
                break
            }
        }
        if ($remaining) {
            Write-Host "Waiting 60 seconds before next download to comply with bot policy..."
            Start-Sleep -Seconds 60
        }
    } else {
        Write-Host "$($entry.Filename) already exists. Skipping."
    }
}
