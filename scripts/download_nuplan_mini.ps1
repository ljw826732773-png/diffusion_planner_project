param(
    [string]$DatasetRoot = "",
    [switch]$SkipExtract
)

$ErrorActionPreference = "Stop"

function Download-File {
    param(
        [string]$Url,
        [string]$OutFile,
        [Int64]$ExpectedSize
    )

    if (Test-Path $OutFile) {
        $currentSize = (Get-Item $OutFile).Length
        if ($ExpectedSize -gt 0 -and $currentSize -eq $ExpectedSize) {
            Write-Output "Already downloaded: $OutFile"
            return
        }
        if ($ExpectedSize -gt 0 -and $currentSize -gt $ExpectedSize) {
            Write-Output "Existing file is larger than expected; deleting and restarting: $OutFile"
            Remove-Item -LiteralPath $OutFile -Force
        } else {
            Write-Output "Partial file found; resuming download:"
            Write-Output "  $OutFile"
            Write-Output "  current=$currentSize expected=$ExpectedSize"
        }
    }

    Write-Output "Downloading:"
    Write-Output "  $Url"
    Write-Output "to:"
    Write-Output "  $OutFile"

    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if ($curl) {
        & curl.exe -L --retry 10 --retry-delay 5 --retry-all-errors -C - -o $OutFile $Url
        if ($LASTEXITCODE -eq 0) {
            return
        }
        Write-Output "curl failed with exit code $LASTEXITCODE, trying BITS."
    }

    try {
        Start-BitsTransfer -Source $Url -Destination $OutFile -ErrorAction Stop
    } catch {
        Write-Output "BITS download failed, falling back to Invoke-WebRequest without resume support."
        Invoke-WebRequest -Uri $Url -OutFile $OutFile
    }
}

function Extract-Zip {
    param(
        [string]$ZipFile,
        [string]$Destination
    )

    Write-Output "Extracting:"
    Write-Output "  $ZipFile"
    Write-Output "to:"
    Write-Output "  $Destination"

    tar -xf $ZipFile -C $Destination
}

function Test-DbFiles {
    param(
        [string]$Path
    )

    if (-not (Test-Path $Path)) {
        return $false
    }

    return @(Get-ChildItem -Path $Path -Filter "*.db" -File -ErrorAction SilentlyContinue).Count -gt 0
}

function Test-Extracted {
    param(
        [string]$Name,
        [string]$DatasetRoot
    )

    if ($Name -eq "nuplan-maps-v1.0.zip") {
        return Test-Path (Join-Path $DatasetRoot "maps\nuplan-maps-v1.0.json")
    }

    if ($Name -eq "nuplan-v1.1_mini.zip") {
        $expectedMini = Join-Path $DatasetRoot "nuplan-v1.1\splits\mini"
        $awsMini = Join-Path $DatasetRoot "data\cache\mini"
        return (Test-DbFiles -Path $expectedMini) -or (Test-DbFiles -Path $awsMini)
    }

    return $false
}

function Ensure-NuplanMiniLayout {
    param(
        [string]$DatasetRoot
    )

    $expectedMini = Join-Path $DatasetRoot "nuplan-v1.1\splits\mini"
    $expectedSplits = Split-Path $expectedMini -Parent
    $awsMini = Join-Path $DatasetRoot "data\cache\mini"
    $sensorBlobs = Join-Path $DatasetRoot "nuplan-v1.1\sensor_blobs"

    New-Item -ItemType Directory -Force -Path $expectedSplits | Out-Null
    New-Item -ItemType Directory -Force -Path $sensorBlobs | Out-Null

    if ((Test-Path $expectedMini) -and (Test-DbFiles -Path $expectedMini)) {
        Write-Output "nuPlan mini layout is ready:"
        Write-Output "  $expectedMini"
        return
    }

    if (Test-DbFiles -Path $awsMini) {
        if (Test-Path $expectedMini) {
            $existingDbCount = @(Get-ChildItem -Path $expectedMini -Filter "*.db" -File -ErrorAction SilentlyContinue).Count
            if ($existingDbCount -eq 0) {
                throw "Expected mini path exists but has no .db files: $expectedMini. Remove or rename it, then rerun this script."
            }
        }

        $target = (Resolve-Path $awsMini).Path
        Write-Output "AWS mini zip extracted to data\cache\mini."
        Write-Output "Creating junction expected by nuPlan devkit:"
        Write-Output "  $expectedMini -> $target"
        New-Item -ItemType Junction -Path $expectedMini -Target $target | Out-Null
        return
    }

    Write-Output "Mini .db files were not found yet under:"
    Write-Output "  $expectedMini"
    Write-Output "  $awsMini"
}

if (-not $DatasetRoot) {
    if ($env:NUPLAN_DATA_ROOT) {
        $DatasetRoot = $env:NUPLAN_DATA_ROOT
    } elseif (Test-Path "D:\") {
        $DatasetRoot = "D:\nuplan-data\dataset"
    } else {
        $DatasetRoot = "$PSScriptRoot\..\work\nuplan-data\dataset"
    }
}

$DatasetRoot = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($DatasetRoot)
$DownloadDir = Join-Path $DatasetRoot "_downloads"

New-Item -ItemType Directory -Force -Path $DatasetRoot | Out-Null
New-Item -ItemType Directory -Force -Path $DownloadDir | Out-Null

$BaseUrl = "https://motional-nuplan.s3.ap-northeast-1.amazonaws.com/public/nuplan-v1.1"
$Files = @(
    @{
        Name = "nuplan-maps-v1.0.zip"
        Url = "$BaseUrl/nuplan-maps-v1.0.zip"
        Size = "0.97 GB"
        SizeBytes = 971557640
    },
    @{
        Name = "nuplan-v1.1_mini.zip"
        Url = "$BaseUrl/nuplan-v1.1_mini.zip"
        Size = "8.55 GB"
        SizeBytes = 8550100030
    }
)

Write-Output "DatasetRoot=$DatasetRoot"
Write-Output "DownloadDir=$DownloadDir"
Write-Output ""
Write-Output "Files to download:"
foreach ($file in $Files) {
    Write-Output "  $($file.Name) ($($file.Size))"
}
Write-Output ""

foreach ($file in $Files) {
    $zipPath = Join-Path $DownloadDir $file.Name
    Download-File -Url $file.Url -OutFile $zipPath -ExpectedSize $file.SizeBytes
    if (-not $SkipExtract) {
        if (Test-Extracted -Name $file.Name -DatasetRoot $DatasetRoot) {
            Write-Output "Already extracted: $($file.Name)"
        } else {
            Extract-Zip -ZipFile $zipPath -Destination $DatasetRoot
        }
    }
}

Ensure-NuplanMiniLayout -DatasetRoot $DatasetRoot

$env:NUPLAN_DATA_ROOT = $DatasetRoot
$env:NUPLAN_MAPS_ROOT = Join-Path $DatasetRoot "maps"
$env:NUPLAN_EXP_ROOT = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath(
    (Join-Path (Split-Path $DatasetRoot -Parent) "exp")
)

New-Item -ItemType Directory -Force -Path $env:NUPLAN_EXP_ROOT | Out-Null

Write-Output ""
Write-Output "Suggested environment variables:"
Write-Output "`$env:NUPLAN_DATA_ROOT=""$env:NUPLAN_DATA_ROOT"""
Write-Output "`$env:NUPLAN_MAPS_ROOT=""$env:NUPLAN_MAPS_ROOT"""
Write-Output "`$env:NUPLAN_EXP_ROOT=""$env:NUPLAN_EXP_ROOT"""

Write-Output ""
Write-Output "Run dataset check:"
Write-Output "scripts\check_nuplan_data.ps1 -NuplanDataRoot ""$env:NUPLAN_DATA_ROOT"" -NuplanMapsRoot ""$env:NUPLAN_MAPS_ROOT"" -NuplanExpRoot ""$env:NUPLAN_EXP_ROOT"""
