<#
dirfiles.ps1

Generates:
  ./tmp/dir_tree.txt
  ./tmp/files_<first-level-dir>.txt
  ./tmp/dirfiles.zip

Default target:
  - If -Path is supplied: use that.
  - Else if script is inside ./tmp: use parent directory.
  - Else: use script directory.

Usage:
  pwsh ./repo-dirfiles.ps1
  pwsh ./repo-dirfiles.ps1 -Trace
  powershell -ExecutionPolicy Bypass -File .\repo-dirfiles.ps1
#>

param(
    [Parameter(Position = 0)]
    [string]$Path,

    # Very noisy: logs directories as they are scanned.
    [switch]$Trace,

    # Disable PowerShell progress bar.
    [switch]$NoProgress,

    # Do not pause at end.
    [switch]$NoPause
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$TmpFolderName       = "tmp"
$ZipFileName         = "dirfiles.zip"
$DirTreeFileName     = "dir_tree.txt"
$ExcludeGitByDefault = $true

$script:StartTime = Get-Date

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $elapsed = (Get-Date) - $script:StartTime
    $stamp = "{0:hh\:mm\:ss}" -f $elapsed
    Write-Host "[$stamp] [$Level] $Message"
}

function Format-ByteSize {
    param([long]$Bytes)

    if ($Bytes -ge 1GB) { return "{0:N2} GB" -f ($Bytes / 1GB) }
    if ($Bytes -ge 1MB) { return "{0:N2} MB" -f ($Bytes / 1MB) }
    if ($Bytes -ge 1KB) { return "{0:N2} KB" -f ($Bytes / 1KB) }

    return "$Bytes B"
}

function Resolve-TargetRoot {
    param([string]$InputPath)

    if (-not [string]::IsNullOrWhiteSpace($InputPath)) {
        return (Resolve-Path -LiteralPath $InputPath).ProviderPath
    }

    $scriptDir = $PSScriptRoot

    if ([string]::IsNullOrWhiteSpace($scriptDir)) {
        $scriptDir = (Get-Location).ProviderPath
    }

    $scriptDirItem = Get-Item -LiteralPath $scriptDir

    if ($scriptDirItem.Name -ieq $TmpFolderName) {
        return $scriptDirItem.Parent.FullName
    }

    return $scriptDirItem.FullName
}

function Test-IsExcludedDirectory {
    param(
        [System.IO.DirectoryInfo]$Directory,
        [string]$OutputDirFullPath,
        [bool]$ExcludeGit
    )

    $dirFull = [System.IO.Path]::GetFullPath($Directory.FullName).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )

    $outFull = [System.IO.Path]::GetFullPath($OutputDirFullPath).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )

    if ($dirFull -ieq $outFull) {
        return $true
    }

    if ($ExcludeGit -and $Directory.Name -ieq ".git") {
        return $true
    }

    return $false
}

function Test-IsSymlinkOrReparsePoint {
    param([System.IO.FileSystemInfo]$Item)

    return (($Item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)
}

function Get-SafeFileStem {
    param([string]$Name)

    $safe = $Name -replace '[^\p{L}\p{Nd}\._-]+', '_'
    $safe = $safe.Trim('_', '.', '-')

    if ([string]::IsNullOrWhiteSpace($safe)) {
        return "unnamed"
    }

    return $safe
}

function Write-Utf8NoBomText {
    param(
        [string]$FilePath,
        [string]$Text
    )

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($FilePath, $Text, $utf8NoBom)
}

function Get-SortedChildren {
    param(
        [System.IO.DirectoryInfo]$Directory,
        [bool]$DirectoriesOnly
    )

    if ($DirectoriesOnly) {
        return @(Get-ChildItem -LiteralPath $Directory.FullName -Force -Directory -ErrorAction SilentlyContinue |
            Sort-Object @{ Expression = { $_.Name.ToLowerInvariant() } }, Name)
    }

    return @(Get-ChildItem -LiteralPath $Directory.FullName -Force -ErrorAction SilentlyContinue |
        Sort-Object `
            @{ Expression = { if ($_.PSIsContainer) { 0 } else { 1 } } },
            @{ Expression = { $_.Name.ToLowerInvariant() } },
            Name)
}

function Add-TreeLines {
    param(
        [System.Text.StringBuilder]$Builder,
        [System.IO.DirectoryInfo]$Directory,
        [string]$OutputDirFullPath,
        [string]$Prefix,
        [bool]$DirectoriesOnly,
        [bool]$ExcludeGit,
        [hashtable]$Stats
    )

    if ($Trace) {
        Write-Log "Scanning: $($Directory.FullName)" "TRACE"
    }

    $childrenRaw = Get-SortedChildren -Directory $Directory -DirectoriesOnly:$DirectoriesOnly
    $children = @()

    foreach ($child in $childrenRaw) {
        if ($child.PSIsContainer) {
            if (Test-IsExcludedDirectory -Directory $child -OutputDirFullPath $OutputDirFullPath -ExcludeGit:$ExcludeGit) {
                $Stats.ExcludedDirectories++
                continue
            }
        }

        $children += $child
    }

    for ($i = 0; $i -lt $children.Count; $i++) {
        $child = $children[$i]
        $isLast = ($i -eq ($children.Count - 1))

        $connector = "+-- "

        if ($isLast) {
            $nextPrefix = $Prefix + "    "
        }
        else {
            $nextPrefix = $Prefix + "|   "
        }

        $name = $child.Name

        if ($child.PSIsContainer) {
            $name = $name + "/"
            $Stats.Directories++
        }
        else {
            $Stats.Files++
        }

        if (Test-IsSymlinkOrReparsePoint -Item $child) {
            $name = $name + " -> [link]"
            $Stats.Links++
        }

        [void]$Builder.Append($Prefix)
        [void]$Builder.Append($connector)
        [void]$Builder.AppendLine($name)

        if ($child.PSIsContainer -and -not (Test-IsSymlinkOrReparsePoint -Item $child)) {
            Add-TreeLines `
                -Builder $Builder `
                -Directory $child `
                -OutputDirFullPath $OutputDirFullPath `
                -Prefix $nextPrefix `
                -DirectoriesOnly:$DirectoriesOnly `
                -ExcludeGit:$ExcludeGit `
                -Stats $Stats
        }
    }
}

function New-TreeReport {
    param(
        [System.IO.DirectoryInfo]$RootDirectory,
        [string]$OutputDirFullPath,
        [bool]$DirectoriesOnly,
        [bool]$ExcludeGit
    )

    $builder = New-Object System.Text.StringBuilder

    $stats = @{
        Directories = 0
        Files = 0
        Links = 0
        ExcludedDirectories = 0
    }

    [void]$builder.AppendLine(".")

    Add-TreeLines `
        -Builder $builder `
        -Directory $RootDirectory `
        -OutputDirFullPath $OutputDirFullPath `
        -Prefix "" `
        -DirectoriesOnly:$DirectoriesOnly `
        -ExcludeGit:$ExcludeGit `
        -Stats $stats

    return @{
        Text = ($builder.ToString() -replace "`r`n", "`n")
        Stats = $stats
    }
}

function Get-BestZipCompressionLevel {
    $names = [System.Enum]::GetNames([System.IO.Compression.CompressionLevel])

    if ($names -contains "SmallestSize") {
        return [System.Enum]::Parse([System.IO.Compression.CompressionLevel], "SmallestSize")
    }

    return [System.IO.Compression.CompressionLevel]::Optimal
}

function New-ZipFromFiles {
    param(
        [string[]]$Files,
        [string]$ZipPath
    )

    Add-Type -AssemblyName System.IO.Compression | Out-Null

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem | Out-Null
    }
    catch {
        # Not required on newer PowerShell/.NET runtimes.
    }

    if (Test-Path -LiteralPath $ZipPath) {
        Write-Log "Removing old zip: $ZipPath"
        Remove-Item -LiteralPath $ZipPath -Force
    }

    $compressionLevel = Get-BestZipCompressionLevel
    Write-Log "Creating zip using compression level: $compressionLevel"

    $zipStream = [System.IO.File]::Open(
        $ZipPath,
        [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::ReadWrite,
        [System.IO.FileShare]::None
    )

    try {
        $zipArchive = New-Object System.IO.Compression.ZipArchive(
            $zipStream,
            [System.IO.Compression.ZipArchiveMode]::Create,
            $false
        )

        try {
            for ($i = 0; $i -lt $Files.Count; $i++) {
                $file = $Files[$i]
                $entryName = Split-Path -Leaf $file

                if (-not $NoProgress) {
                    $percent = [int](($i / [Math]::Max($Files.Count, 1)) * 100)
                    Write-Progress `
                        -Activity "Creating dirfiles.zip" `
                        -Status "Adding $entryName" `
                        -PercentComplete $percent
                }

                Write-Log "Zipping: $entryName"

                [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
                    $zipArchive,
                    $file,
                    $entryName,
                    $compressionLevel
                ) | Out-Null
            }

            if (-not $NoProgress) {
                Write-Progress -Activity "Creating dirfiles.zip" -Completed
            }
        }
        finally {
            $zipArchive.Dispose()
        }
    }
    finally {
        $zipStream.Dispose()
    }
}

# -----------------------------
# Main
# -----------------------------

try {
    Write-Log "Starting repo directory/file report generation."

    $targetRoot = Resolve-TargetRoot -InputPath $Path
    $targetRootItem = Get-Item -LiteralPath $targetRoot

    if (-not $targetRootItem.PSIsContainer) {
        throw "Target path is not a directory: $targetRoot"
    }

    $outputDir = Join-Path $targetRootItem.FullName $TmpFolderName

    Write-Log "Target root: $($targetRootItem.FullName)"
    Write-Log "Output dir:  $outputDir"

    if (-not (Test-Path -LiteralPath $outputDir)) {
        Write-Log "Creating output directory."
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }

    $generatedFiles = New-Object System.Collections.Generic.List[string]

    # 1. Full directory-only tree.
    Write-Log "Generating directory-only tree: $DirTreeFileName"

    $dirTreePath = Join-Path $outputDir $DirTreeFileName

    $dirTreeReport = New-TreeReport `
        -RootDirectory $targetRootItem `
        -OutputDirFullPath $outputDir `
        -DirectoriesOnly:$true `
        -ExcludeGit:$ExcludeGitByDefault

    Write-Utf8NoBomText -FilePath $dirTreePath -Text $dirTreeReport.Text
    $generatedFiles.Add($dirTreePath)

    $dirTreeSize = (Get-Item -LiteralPath $dirTreePath).Length

    Write-Log ("Wrote {0} | dirs={1}, files={2}, links={3}, excluded_dirs={4}, size={5}" -f `
        $DirTreeFileName,
        $dirTreeReport.Stats.Directories,
        $dirTreeReport.Stats.Files,
        $dirTreeReport.Stats.Links,
        $dirTreeReport.Stats.ExcludedDirectories,
        (Format-ByteSize $dirTreeSize)
    )

    # 2. One files_<dir>.txt per first-level directory.
    Write-Log "Finding first-level directories."

    $firstLevelDirs = @(Get-ChildItem -LiteralPath $targetRootItem.FullName -Force -Directory -ErrorAction SilentlyContinue |
        Sort-Object @{ Expression = { $_.Name.ToLowerInvariant() } }, Name)

    $firstLevelDirs = @($firstLevelDirs | Where-Object {
        -not (Test-IsExcludedDirectory -Directory $_ -OutputDirFullPath $outputDir -ExcludeGit:$ExcludeGitByDefault)
    })

    Write-Log "First-level directories to report: $($firstLevelDirs.Count)"

    $usedNames = @{}

    for ($index = 0; $index -lt $firstLevelDirs.Count; $index++) {
        $dir = $firstLevelDirs[$index]
        $ordinal = $index + 1

        if (-not $NoProgress) {
            $percent = [int](($index / [Math]::Max($firstLevelDirs.Count, 1)) * 100)
            Write-Progress `
                -Activity "Generating first-level directory reports" `
                -Status "[$ordinal/$($firstLevelDirs.Count)] $($dir.Name)" `
                -PercentComplete $percent
        }

        Write-Log "Generating report [$ordinal/$($firstLevelDirs.Count)]: $($dir.Name)/"

        $stem = Get-SafeFileStem -Name $dir.Name
        $baseName = "files_$stem"
        $finalName = $baseName
        $n = 2

        while ($usedNames.ContainsKey($finalName.ToLowerInvariant())) {
            $finalName = "$baseName`_$n"
            $n++
        }

        $usedNames[$finalName.ToLowerInvariant()] = $true

        $reportPath = Join-Path $outputDir "$finalName.txt"

        $treeReport = New-TreeReport `
            -RootDirectory $dir `
            -OutputDirFullPath $outputDir `
            -DirectoriesOnly:$false `
            -ExcludeGit:$ExcludeGitByDefault

        Write-Utf8NoBomText -FilePath $reportPath -Text $treeReport.Text
        $generatedFiles.Add($reportPath)

        $reportSize = (Get-Item -LiteralPath $reportPath).Length

        Write-Log ("Wrote {0} | dirs={1}, files={2}, links={3}, excluded_dirs={4}, size={5}" -f `
            (Split-Path -Leaf $reportPath),
            $treeReport.Stats.Directories,
            $treeReport.Stats.Files,
            $treeReport.Stats.Links,
            $treeReport.Stats.ExcludedDirectories,
            (Format-ByteSize $reportSize)
        )
    }

    if (-not $NoProgress) {
        Write-Progress -Activity "Generating first-level directory reports" -Completed
    }

    # 3. Zip reports.
    $zipPath = Join-Path $outputDir $ZipFileName

    Write-Log "Preparing zip archive."
    New-ZipFromFiles -Files $generatedFiles.ToArray() -ZipPath $zipPath

    $zipSize = (Get-Item -LiteralPath $zipPath).Length
    $elapsed = (Get-Date) - $script:StartTime

    Write-Host ""
    Write-Log "DONE" "PASS"
    Write-Log "Target root: $($targetRootItem.FullName)" "PASS"
    Write-Log "Output dir:  $outputDir" "PASS"
    Write-Log "Zip file:    $zipPath" "PASS"
    Write-Log "Zip size:    $(Format-ByteSize $zipSize)" "PASS"
    Write-Log "Text files:  $($generatedFiles.Count)" "PASS"
    Write-Log ("Elapsed:     {0:hh\:mm\:ss}" -f $elapsed) "PASS"
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Log "FAILED: $($_.Exception.Message)" "ERROR"
    Write-Host $_.ScriptStackTrace
    Write-Host ""
    exit 1
}
finally {
    if (-not $NoPause) {
        Write-Host "Press Enter to close..."
        [void](Read-Host)
    }
}