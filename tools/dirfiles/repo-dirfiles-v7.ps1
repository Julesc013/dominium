<#
repo-dirfiles-v7.ps1

Repository directory/file map generator.

V6 priority:
  - Working, debuggable, Windows PowerShell 5.1 compatible syntax.
  - Simple control flow over clever streaming.
  - Clear startup diagnostics and final manifest.

Kept outputs in ./tmp:
  dir_tree.txt             Human-readable directory-only tree.
  dir_tree.json            Strict JSON directory-only tree.
  dirfiles_manifest.json   Run summary, hashes, warnings, mode, and zip metadata.
  dirfiles.zip             ZIP containing dir_tree.txt, dir_tree.json,
                           files_root.json, and files_<first-level-dir>.json.

Temporary outputs removed after zipping unless -KeepJsonReports is supplied:
  files_root.json
  files_*.json

Modes:
  default       Filesystem scan, excluding .git and ./tmp by default.
  -TrackedOnly Git-index scan using git ls-files. Faster and cleaner for GPT upload.
  -Use7Zip     Uses 7z/7za/7zr for ZIP Deflate when available; otherwise .NET ZIP.
#>

param(
    [Parameter(Position = 0)]
    [string]$Path,

    [switch]$TrackedOnly,
    [switch]$Use7Zip,
    [switch]$Trace,
    [switch]$NoProgress,

    [ValidateSet("Auto", "Always", "Never")]
    [string]$PauseMode = "Auto",

    [switch]$KeepJsonReports,
    [switch]$IncludeGit,
    [switch]$IncludeAbsolutePaths,
    [string[]]$ExcludeDir = @(),
    [switch]$Lean,
    [switch]$AsciiTree,

    [ValidateRange(1, 1000000)]
    [int]$StatusEvery = 1000,

    [ValidateRange(1, 3600)]
    [int]$HeartbeatSeconds = 2,

    [switch]$NoColor,
    [switch]$NoZip
)

$ErrorActionPreference = "Stop"

# -----------------------------
# Constants / run state
# -----------------------------

$TmpFolderName       = "tmp"
$ZipFileName         = "dirfiles.zip"
$DirTreeTextFileName = "dir_tree.txt"
$DirTreeJsonFileName = "dir_tree.json"
$RootFilesFileName   = "files_root.json"
$ManifestFileName    = "dirfiles_manifest.json"
$SchemaName          = "repo-dirfiles-json-v7"
$ManifestSchemaName  = "repo-dirfiles-manifest-v4"

$LeanExcludeDirNames = @(
    "node_modules", ".venv", "venv", "env", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".nox",
    ".next", ".nuxt", ".gradle", ".idea", ".vs",
    "bin", "obj", "build", "dist", "target", "coverage"
)

$script:StartTime = Get-Date
$script:ExitCode = 0
$script:UseColor = -not $NoColor
$script:Warnings = New-Object System.Collections.ArrayList
$script:WarningCount = 0

# -----------------------------
# Console / UX
# -----------------------------

function Get-LevelColor {
    param([string]$Level)

    switch ($Level) {
        "PASS"  { return "Green" }
        "WARN"  { return "Yellow" }
        "ERROR" { return "Red" }
        "TRACE" { return "DarkGray" }
        "STEP"  { return "Cyan" }
        default  { return "Gray" }
    }
}

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $elapsed = (Get-Date) - $script:StartTime
    $stamp = "{0:hh\:mm\:ss}" -f $elapsed
    $line = "[$stamp] [$Level] $Message"

    if ($script:UseColor) {
        Write-Host $line -ForegroundColor (Get-LevelColor -Level $Level)
    }
    else {
        Write-Host $line
    }
}

function Add-WarningMessage {
    param([string]$Message)

    $script:WarningCount = $script:WarningCount + 1

    if ($script:Warnings.Count -lt 200) {
        [void]$script:Warnings.Add([ordered]@{
            time_utc = (Get-Date).ToUniversalTime().ToString("o")
            message = $Message
        })
    }

    Write-Log -Level "WARN" -Message $Message
}

function Format-ByteSize {
    param([Int64]$Bytes)

    if ($Bytes -ge 1GB) { return "{0:N2} GB" -f ($Bytes / 1GB) }
    if ($Bytes -ge 1MB) { return "{0:N2} MB" -f ($Bytes / 1MB) }
    if ($Bytes -ge 1KB) { return "{0:N2} KB" -f ($Bytes / 1KB) }
    return "$Bytes B"
}

function Test-ShouldPause {
    if ($PauseMode -eq "Always") { return $true }
    if ($PauseMode -eq "Never") { return $false }

    try {
        if ([System.Environment]::OSVersion.Platform -ne [System.PlatformID]::Win32NT) { return $false }
        $proc = Get-CimInstance Win32_Process -Filter "ProcessId=$PID" -ErrorAction Stop
        if ($null -eq $proc) { return $false }
        $parent = Get-Process -Id ([int]$proc.ParentProcessId) -ErrorAction SilentlyContinue
        if ($null -eq $parent) { return $false }
        return ($parent.ProcessName -ieq "explorer")
    }
    catch {
        return $false
    }
}

# -----------------------------
# Path helpers
# -----------------------------

function Normalize-RepoPath {
    param([string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) { return "." }
    $p = ([string]$Value) -replace '\\', '/'

    while ($p.StartsWith("./")) {
        $p = $p.Substring(2)
    }

    $p = $p.TrimEnd('/')
    if ([string]::IsNullOrWhiteSpace($p)) { return "." }
    return $p
}

function Get-ParentRepoPath {
    param([string]$RepoPath)

    $p = Normalize-RepoPath -Value $RepoPath
    if ($p -eq ".") { return $null }

    $idx = $p.LastIndexOf('/')
    if ($idx -lt 0) { return "." }
    return $p.Substring(0, $idx)
}

function Get-NameFromRepoPath {
    param([string]$RepoPath)

    $p = Normalize-RepoPath -Value $RepoPath
    if ($p -eq ".") { return "." }

    $idx = $p.LastIndexOf('/')
    if ($idx -lt 0) { return $p }
    return $p.Substring($idx + 1)
}

function Get-FirstPathSegment {
    param([string]$RepoPath)

    $p = Normalize-RepoPath -Value $RepoPath
    if ($p -eq ".") { return "." }

    $idx = $p.IndexOf('/')
    if ($idx -lt 0) { return $p }
    return $p.Substring(0, $idx)
}

function Join-RepoPathToFullPath {
    param(
        [string]$RootPath,
        [string]$RepoPath
    )

    $p = Normalize-RepoPath -Value $RepoPath
    if ($p -eq ".") { return $RootPath }

    $full = $RootPath
    foreach ($part in ($p -split '/')) {
        if (-not [string]::IsNullOrWhiteSpace($part)) {
            $full = Join-Path $full $part
        }
    }
    return $full
}


function Remove-TrailingPathSeparators {
    param([string]$Value)

    if ([string]::IsNullOrEmpty($Value)) { return $Value }
    $root = [System.IO.Path]::GetPathRoot($Value)
    $v = $Value

    while ($v.Length -gt $root.Length) {
        $last = $v[$v.Length - 1]
        if ($last -ne [char]92 -and $last -ne [char]47) { break }
        $v = $v.Substring(0, $v.Length - 1)
    }

    return $v
}

function Remove-LeadingPathSeparators {
    param([string]$Value)

    if ([string]::IsNullOrEmpty($Value)) { return $Value }
    $v = $Value

    while ($v.Length -gt 0) {
        $first = $v[0]
        if ($first -ne [char]92 -and $first -ne [char]47) { break }
        $v = $v.Substring(1)
    }

    return $v
}

function Convert-FullPathToRepoPath {
    param(
        [string]$FullPath,
        [string]$RootPath
    )

    $rootFull = Remove-TrailingPathSeparators -Value ([System.IO.Path]::GetFullPath($RootPath))
    $itemFull = Remove-TrailingPathSeparators -Value ([System.IO.Path]::GetFullPath($FullPath))

    $comparison = [System.StringComparison]::Ordinal
    if ([System.IO.Path]::DirectorySeparatorChar -eq '\') {
        $comparison = [System.StringComparison]::OrdinalIgnoreCase
    }

    if ($itemFull.Equals($rootFull, $comparison)) { return "." }
    if ($itemFull.Length -le $rootFull.Length) { return "." }

    $relative = Remove-LeadingPathSeparators -Value ($itemFull.Substring($rootFull.Length))
    return (Normalize-RepoPath -Value $relative)
}

function Test-RepoPathUnderRoot {
    param(
        [string]$PathValue,
        [string]$RootValue
    )

    $p = Normalize-RepoPath -Value $PathValue
    $r = Normalize-RepoPath -Value $RootValue
    if ($r -eq ".") { return $true }
    if ($p -eq $r) { return $true }
    return $p.StartsWith($r + "/")
}

function Get-SafeFileStem {
    param([string]$Name)

    $safe = ([string]$Name) -replace '[^\p{L}\p{Nd}\._-]+', '_'
    $safe = $safe.Trim('_', '.', '-')
    if ([string]::IsNullOrWhiteSpace($safe)) { return "unnamed" }
    return $safe
}

# -----------------------------
# Sets / stats
# -----------------------------

function New-Set {
    return @{}
}

function Add-SetValue {
    param(
        [hashtable]$Set,
        [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) { return }
    $v = Normalize-RepoPath -Value $Value
    $key = $v.ToLowerInvariant()
    if (-not $Set.ContainsKey($key)) { $Set[$key] = $v }
}

function Get-SetValuesSorted {
    param([hashtable]$Set)

    return @($Set.Values | Sort-Object @{ Expression = { ([string]$_).ToLowerInvariant() } }, @{ Expression = { [string]$_ } })
}

function Add-MapSetValue {
    param(
        [hashtable]$Map,
        [string]$Key,
        [string]$Value
    )

    $k = (Normalize-RepoPath -Value $Key).ToLowerInvariant()
    if (-not $Map.ContainsKey($k)) { $Map[$k] = New-Set }
    Add-SetValue -Set $Map[$k] -Value $Value
}

function Get-MapSetValuesSorted {
    param(
        [hashtable]$Map,
        [string]$Key
    )

    $k = (Normalize-RepoPath -Value $Key).ToLowerInvariant()
    if (-not $Map.ContainsKey($k)) { return @() }
    return (Get-SetValuesSorted -Set $Map[$k])
}

function New-Stats {
    return @{
        nodes = 0
        directories = 0
        files = 0
        links = 0
        missing = 0
        excluded_directories = 0
        read_errors = 0
        max_depth = 0
        total_file_bytes = 0
        extension_counts = @{}
    }
}

function Add-Stat {
    param(
        [hashtable]$Stats,
        [string]$Key,
        [Int64]$Delta = 1
    )

    $Stats[$Key] = [Int64]$Stats[$Key] + $Delta
}

function Add-ExtensionStat {
    param(
        [hashtable]$Stats,
        [string]$Extension
    )

    $key = $Extension
    if ([string]::IsNullOrWhiteSpace($key)) { $key = "[none]" }
    if (-not $Stats["extension_counts"].Contains($key)) { $Stats["extension_counts"][$key] = 0 }
    $Stats["extension_counts"][$key] = [Int64]$Stats["extension_counts"][$key] + 1
}

function Finish-Stats {
    param([hashtable]$Stats)

    $Stats["total_file_bytes_human"] = Format-ByteSize -Bytes ([Int64]$Stats["total_file_bytes"])
    return $Stats
}

# -----------------------------
# Exclusion logic
# -----------------------------

function Get-EffectiveExcludeDirs {
    $items = @()
    if ($Lean) { $items += $LeanExcludeDirNames }
    foreach ($x in $ExcludeDir) {
        if (-not [string]::IsNullOrWhiteSpace($x)) { $items += $x }
    }
    return @($items | Sort-Object -Unique)
}

function Test-RepoPathExcluded {
    param(
        [string]$RepoPath,
        [bool]$ExcludeGit,
        [string[]]$EffectiveExcludeDir
    )

    $p = Normalize-RepoPath -Value $RepoPath
    if ($p -eq ".") { return $false }

    $parts = @($p -split '/')
    if ($parts.Count -gt 0 -and $parts[0] -ieq $TmpFolderName) { return $true }

    foreach ($part in $parts) {
        if ($ExcludeGit -and $part -ieq ".git") { return $true }
        foreach ($name in $EffectiveExcludeDir) {
            if ($part -ieq $name) { return $true }
        }
    }

    return $false
}

function Test-FsDirectoryExcluded {
    param(
        $DirectoryInfo,
        [string]$OutputDirFullPath,
        [bool]$ExcludeGit,
        [string[]]$EffectiveExcludeDir
    )

    try {
        $dirFull = Remove-TrailingPathSeparators -Value ([System.IO.Path]::GetFullPath($DirectoryInfo.FullName))
        $outFull = Remove-TrailingPathSeparators -Value ([System.IO.Path]::GetFullPath($OutputDirFullPath))
        $comparison = [System.StringComparison]::Ordinal
        if ([System.IO.Path]::DirectorySeparatorChar -eq '\') { $comparison = [System.StringComparison]::OrdinalIgnoreCase }

        if ($dirFull.Equals($outFull, $comparison)) { return $true }
        if ($ExcludeGit -and $DirectoryInfo.Name -ieq ".git") { return $true }
        foreach ($name in $EffectiveExcludeDir) {
            if ($DirectoryInfo.Name -ieq $name) { return $true }
        }
        return $false
    }
    catch {
        return $false
    }
}

# -----------------------------
# File IO / JSON
# -----------------------------

function New-Utf8NoBomEncoding {
    return (New-Object System.Text.UTF8Encoding -ArgumentList @($false))
}

function Write-TextFileAtomic {
    param(
        [string]$FilePath,
        [string]$Text
    )

    $part = "$FilePath.part"
    if (Test-Path -LiteralPath $part) { Remove-Item -LiteralPath $part -Force }
    [System.IO.File]::WriteAllText($part, $Text, (New-Utf8NoBomEncoding))
    if (Test-Path -LiteralPath $FilePath) { Remove-Item -LiteralPath $FilePath -Force }
    Move-Item -LiteralPath $part -Destination $FilePath -Force
}

function Write-JsonFileAtomic {
    param(
        [string]$FilePath,
        [object]$Object
    )

    $json = $Object | ConvertTo-Json -Depth 100
    $json = $json -replace "`r`n", "`n"
    Write-TextFileAtomic -FilePath $FilePath -Text ($json + "`n")
}

function New-FileRecord {
    param(
        [string]$FilePath,
        [string]$Kind,
        [bool]$KeptUncompressed
    )

    $item = Get-Item -LiteralPath $FilePath -ErrorAction Stop
    $hash = Get-FileHash -LiteralPath $FilePath -Algorithm SHA256 -ErrorAction Stop

    return [ordered]@{
        file = Split-Path -Leaf $FilePath
        kind = $Kind
        size_bytes = [Int64]$item.Length
        size_human = Format-ByteSize -Bytes ([Int64]$item.Length)
        sha256 = $hash.Hash.ToLowerInvariant()
        kept_uncompressed = [bool]$KeptUncompressed
    }
}

# -----------------------------
# Git helpers
# -----------------------------

function Invoke-GitLines {
    param(
        [string]$DirectoryPath,
        [string[]]$Arguments
    )

    try {
        $gitCommand = Get-Command git -ErrorAction SilentlyContinue
        if ($null -eq $gitCommand) { return $null }

        $output = & git -C $DirectoryPath @Arguments 2>$null
        if ($LASTEXITCODE -ne 0) { return $null }
        return @($output)
    }
    catch {
        return $null
    }
}

function Invoke-GitSingleLine {
    param(
        [string]$DirectoryPath,
        [string[]]$Arguments
    )

    $lines = Invoke-GitLines -DirectoryPath $DirectoryPath -Arguments $Arguments
    if ($null -eq $lines -or @($lines).Count -lt 1) { return $null }
    return [string](@($lines)[0])
}

function Get-GitRoot {
    param([string]$DirectoryPath)

    $root = Invoke-GitSingleLine -DirectoryPath $DirectoryPath -Arguments @("rev-parse", "--show-toplevel")
    if (-not [string]::IsNullOrWhiteSpace($root)) {
        return [System.IO.Path]::GetFullPath($root)
    }

    try {
        $item = Get-Item -LiteralPath $DirectoryPath -ErrorAction Stop
        if (-not $item.PSIsContainer) { $item = $item.Directory }
        while ($null -ne $item) {
            $marker = Join-Path $item.FullName ".git"
            if (Test-Path -LiteralPath $marker) { return $item.FullName }
            $item = $item.Parent
        }
    }
    catch {
        return $null
    }

    return $null
}

function Get-GitMetadata {
    param([string]$RootPath)

    $gitRoot = Get-GitRoot -DirectoryPath $RootPath
    if ([string]::IsNullOrWhiteSpace($gitRoot)) {
        return [ordered]@{
            is_git_worktree = $false
            root_detected = $false
            branch = $null
            commit = $null
            dirty = $null
        }
    }

    $branch = Invoke-GitSingleLine -DirectoryPath $gitRoot -Arguments @("branch", "--show-current")
    $commit = Invoke-GitSingleLine -DirectoryPath $gitRoot -Arguments @("rev-parse", "HEAD")
    $status = Invoke-GitLines -DirectoryPath $gitRoot -Arguments @("status", "--porcelain")
    $dirty = $null
    if ($null -ne $status) { $dirty = (@($status).Count -gt 0) }

    return [ordered]@{
        is_git_worktree = $true
        root_detected = $true
        branch = $branch
        commit = $commit
        dirty = $dirty
    }
}

function Resolve-TargetRoot {
    param([string]$InputPath)

    if (-not [string]::IsNullOrWhiteSpace($InputPath)) {
        return [pscustomobject]@{
            Path = (Resolve-Path -LiteralPath $InputPath).ProviderPath
            Reason = "explicit -Path argument"
        }
    }

    $scriptDir = $PSScriptRoot
    if (-not [string]::IsNullOrWhiteSpace($scriptDir)) {
        $scriptGitRoot = Get-GitRoot -DirectoryPath $scriptDir
        if (-not [string]::IsNullOrWhiteSpace($scriptGitRoot)) {
            return [pscustomobject]@{
                Path = $scriptGitRoot
                Reason = "Git worktree root detected from script location"
            }
        }
    }

    $currentDir = (Get-Location).ProviderPath
    $currentGitRoot = Get-GitRoot -DirectoryPath $currentDir
    if (-not [string]::IsNullOrWhiteSpace($currentGitRoot)) {
        return [pscustomobject]@{
            Path = $currentGitRoot
            Reason = "Git worktree root detected from current directory"
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($scriptDir)) {
        $scriptDirItem = Get-Item -LiteralPath $scriptDir -ErrorAction Stop
        if ($scriptDirItem.Name -ieq $TmpFolderName) {
            return [pscustomobject]@{
                Path = $scriptDirItem.Parent.FullName
                Reason = "script is inside ./tmp; using parent directory"
            }
        }
        return [pscustomobject]@{
            Path = $scriptDirItem.FullName
            Reason = "fallback to script directory"
        }
    }

    return [pscustomobject]@{
        Path = $currentDir
        Reason = "fallback to current directory"
    }
}

# -----------------------------
# Node and report builders
# -----------------------------

function New-NodeRecord {
    param(
        [string]$RepoPath,
        [string]$Type,
        [int]$Depth,
        [string]$TargetRootFullPath,
        [hashtable]$Stats
    )

    $repoPathNorm = Normalize-RepoPath -Value $RepoPath
    $fullPath = Join-RepoPathToFullPath -RootPath $TargetRootFullPath -RepoPath $repoPathNorm
    $exists = Test-Path -LiteralPath $fullPath
    $isLink = $false
    $fileSize = $null
    $extension = $null
    $lastWriteUtc = $null

    Add-Stat -Stats $Stats -Key "nodes"
    if ($Depth -gt [int]$Stats["max_depth"]) { $Stats["max_depth"] = $Depth }

    if ($Type -eq "directory") { Add-Stat -Stats $Stats -Key "directories" }
    else { Add-Stat -Stats $Stats -Key "files" }

    if (-not $exists) {
        Add-Stat -Stats $Stats -Key "missing"
    }
    else {
        try {
            $item = Get-Item -LiteralPath $fullPath -Force -ErrorAction Stop
            $isLink = (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)
            if ($isLink) { Add-Stat -Stats $Stats -Key "links" }
            $lastWriteUtc = $item.LastWriteTimeUtc.ToString("o")

            if ($Type -eq "file") {
                $fileInfo = [System.IO.FileInfo]$item
                $fileSize = [Int64]$fileInfo.Length
                Add-Stat -Stats $Stats -Key "total_file_bytes" -Delta $fileSize
                if (-not [string]::IsNullOrWhiteSpace($fileInfo.Extension)) {
                    $extension = $fileInfo.Extension.TrimStart('.').ToLowerInvariant()
                }
                Add-ExtensionStat -Stats $Stats -Extension $extension
            }
        }
        catch {
            Add-Stat -Stats $Stats -Key "read_errors"
            Add-WarningMessage -Message "Could not stat path: $repoPathNorm :: $($_.Exception.Message)"
        }
    }

    return [ordered]@{
        id = [Int64]$Stats["nodes"]
        type = $Type
        depth = $Depth
        path = $repoPathNorm
        parent = Get-ParentRepoPath -RepoPath $repoPathNorm
        name = Get-NameFromRepoPath -RepoPath $repoPathNorm
        exists = [bool]$exists
        is_link = [bool]$isLink
        file_size_bytes = $fileSize
        extension = $extension
        last_write_utc = $lastWriteUtc
    }
}

function New-ReadmeObject {
    param(
        [string]$ReportKind,
        [bool]$IncludesFiles
    )

    $contains = "directories only"
    if ($IncludesFiles) { $contains = "directories and files" }

    return [ordered]@{
        note = "Strict JSON. JSON comments are not valid, so human-readable guidance is stored in this _readme object."
        purpose = "Repository structure capture for human review, GPT upload, and agentic navigation."
        report_kind = $ReportKind
        contains = $contains
        parsing = "Use nodes[] as a flat list. Use path and parent fields for navigation."
        path_semantics = "All paths are target-root-relative and use forward slashes. The root path is '.'."
        tracked_mode_note = "When source_mode is git_tracked, paths come from git ls-files and directories are inferred from tracked file parents."
    }
}

function New-ReportObject {
    param(
        [string]$ReportFileName,
        [string]$ReportKind,
        [string]$SourceMode,
        [bool]$IncludesFiles,
        [string]$TargetRootName,
        [string]$ReportRootPath,
        [object]$GitMetadata,
        [string[]]$EffectiveExcludeDir,
        [object[]]$Nodes,
        [hashtable]$Stats
    )

    $excluded = @("output tmp directory")
    if (-not $IncludeGit) { $excluded += ".git" }
    foreach ($d in $EffectiveExcludeDir) { $excluded += $d }

    $meta = [ordered]@{
        schema = $SchemaName
        report_file = $ReportFileName
        report_kind = $ReportKind
        source_mode = $SourceMode
        generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        target_root_name = $TargetRootName
        report_root = $ReportRootPath
        includes_files = [bool]$IncludesFiles
        excluded = $excluded
        git = $GitMetadata
        absolute_paths_included = [bool]$IncludeAbsolutePaths
    }

    return [ordered]@{
        _readme = New-ReadmeObject -ReportKind $ReportKind -IncludesFiles:$IncludesFiles
        _meta = $meta
        stats = (Finish-Stats -Stats $Stats)
        nodes = @($Nodes)
    }
}

# -----------------------------
# Filesystem scan mode
# -----------------------------

function Get-FsChildrenSorted {
    param(
        [string]$DirectoryPath,
        [bool]$IncludeFiles,
        [hashtable]$Stats
    )

    try {
        if ($IncludeFiles) {
            return @(Get-ChildItem -LiteralPath $DirectoryPath -Force -ErrorAction Stop |
                Sort-Object @{ Expression = { if ($_.PSIsContainer) { 0 } else { 1 } } }, @{ Expression = { $_.Name.ToLowerInvariant() } }, Name)
        }
        return @(Get-ChildItem -LiteralPath $DirectoryPath -Force -Directory -ErrorAction Stop |
            Sort-Object @{ Expression = { $_.Name.ToLowerInvariant() } }, Name)
    }
    catch {
        Add-Stat -Stats $Stats -Key "read_errors"
        Add-WarningMessage -Message "Could not read directory: $DirectoryPath :: $($_.Exception.Message)"
        return @()
    }
}

function Build-FsReportNodes {
    param(
        [string]$TargetRootFullPath,
        [string]$ReportRootFullPath,
        [string]$OutputDirFullPath,
        [bool]$IncludeFiles,
        [string[]]$EffectiveExcludeDir
    )

    $stats = New-Stats
    $nodes = New-Object System.Collections.ArrayList
    $reportRootRepoPath = Convert-FullPathToRepoPath -FullPath $ReportRootFullPath -RootPath $TargetRootFullPath
    $rootNode = New-NodeRecord -RepoPath $reportRootRepoPath -Type "directory" -Depth 0 -TargetRootFullPath $TargetRootFullPath -Stats $stats
    [void]$nodes.Add($rootNode)

    $stack = New-Object System.Collections.Stack
    $stack.Push(@{ kind = "dir"; full = $ReportRootFullPath; depth = 0 })
    $lastLog = Get-Date

    while ($stack.Count -gt 0) {
        $entry = $stack.Pop()
        if ([string]$entry["kind"] -eq "dir") {
            $dirFull = [string]$entry["full"]
            $depth = [int]$entry["depth"]
            if ($Trace) { Write-Log -Level "TRACE" -Message "Scanning: $dirFull" }

            $children = Get-FsChildrenSorted -DirectoryPath $dirFull -IncludeFiles:$IncludeFiles -Stats $stats
            for ($i = $children.Count - 1; $i -ge 0; $i--) {
                $child = $children[$i]
                if ($child.PSIsContainer) {
                    if (Test-FsDirectoryExcluded -DirectoryInfo $child -OutputDirFullPath $OutputDirFullPath -ExcludeGit:(-not $IncludeGit) -EffectiveExcludeDir $EffectiveExcludeDir) {
                        Add-Stat -Stats $stats -Key "excluded_directories"
                        continue
                    }
                }
                $stack.Push(@{ kind = "node"; item = $child; depth = ($depth + 1) })
            }
        }
        else {
            $item = $entry["item"]
            $depth = [int]$entry["depth"]
            $repoPath = Convert-FullPathToRepoPath -FullPath $item.FullName -RootPath $TargetRootFullPath
            $type = "file"
            if ($item.PSIsContainer) { $type = "directory" }
            $node = New-NodeRecord -RepoPath $repoPath -Type $type -Depth $depth -TargetRootFullPath $TargetRootFullPath -Stats $stats
            [void]$nodes.Add($node)

            if (($stats["nodes"] % $StatusEvery) -eq 0 -or ((Get-Date) - $lastLog).TotalSeconds -ge $HeartbeatSeconds) {
                Write-Log -Message ("scanning nodes={0} dirs={1} files={2} current={3}" -f $stats["nodes"], $stats["directories"], $stats["files"], $repoPath)
                $lastLog = Get-Date
            }

            if ($item.PSIsContainer -and -not $node["is_link"]) {
                $stack.Push(@{ kind = "dir"; full = $item.FullName; depth = $depth })
            }
        }
    }

    return [pscustomobject]@{ Nodes = @($nodes.ToArray()); Stats = $stats; ReportRoot = $reportRootRepoPath }
}

# -----------------------------
# Git tracked mode
# -----------------------------

function Build-TrackedIndex {
    param(
        [string]$RootPath,
        [string[]]$EffectiveExcludeDir
    )

    $lines = Invoke-GitLines -DirectoryPath $RootPath -Arguments @("-c", "core.quotepath=false", "ls-files")
    if ($null -eq $lines) { throw "-TrackedOnly was requested, but 'git ls-files' failed. Run inside a Git worktree or omit -TrackedOnly." }

    $files = New-Set
    $dirs = New-Set
    $rootFiles = New-Set
    $firstLevelDirs = New-Set
    $dirChildren = @{}
    $fileChildren = @{}
    $excluded = 0

    Add-SetValue -Set $dirs -Value "."

    foreach ($line in @($lines)) {
        $filePath = Normalize-RepoPath -Value ([string]$line)
        if ($filePath -eq ".") { continue }
        if (Test-RepoPathExcluded -RepoPath $filePath -ExcludeGit:(-not $IncludeGit) -EffectiveExcludeDir $EffectiveExcludeDir) {
            $excluded = $excluded + 1
            continue
        }

        Add-SetValue -Set $files -Value $filePath
        $parent = Get-ParentRepoPath -RepoPath $filePath
        if ($parent -eq ".") { Add-SetValue -Set $rootFiles -Value $filePath }
        Add-MapSetValue -Map $fileChildren -Key $parent -Value $filePath

        $parts = @($filePath -split '/')
        if ($parts.Count -gt 1) {
            Add-SetValue -Set $firstLevelDirs -Value $parts[0]
            $current = ""
            $parentDir = "."
            for ($i = 0; $i -lt ($parts.Count - 1); $i++) {
                if ($current -eq "") { $current = $parts[$i] } else { $current = $current + "/" + $parts[$i] }
                Add-SetValue -Set $dirs -Value $current
                Add-MapSetValue -Map $dirChildren -Key $parentDir -Value $current
                $parentDir = $current
            }
        }
    }

    return [pscustomobject]@{
        Files = $files
        Dirs = $dirs
        RootFiles = $rootFiles
        FirstLevelDirs = $firstLevelDirs
        DirChildren = $dirChildren
        FileChildren = $fileChildren
        RawCount = @($lines).Count
        ExcludedCount = $excluded
    }
}

function Build-TrackedReportNodes {
    param(
        [string]$TargetRootFullPath,
        [object]$Index,
        [string]$ReportRootPath,
        [bool]$IncludeFiles
    )

    $stats = New-Stats
    $nodes = New-Object System.Collections.ArrayList
    $rootPath = Normalize-RepoPath -Value $ReportRootPath
    $rootNode = New-NodeRecord -RepoPath $rootPath -Type "directory" -Depth 0 -TargetRootFullPath $TargetRootFullPath -Stats $stats
    [void]$nodes.Add($rootNode)

    $stack = New-Object System.Collections.Stack
    $stack.Push(@{ kind = "dir"; path = $rootPath; depth = 0 })
    $lastLog = Get-Date

    while ($stack.Count -gt 0) {
        $entry = $stack.Pop()
        if ([string]$entry["kind"] -eq "dir") {
            $parent = [string]$entry["path"]
            $depth = [int]$entry["depth"]
            $dirChildren = @(Get-MapSetValuesSorted -Map $Index.DirChildren -Key $parent)
            $fileChildren = @()
            if ($IncludeFiles) { $fileChildren = @(Get-MapSetValuesSorted -Map $Index.FileChildren -Key $parent) }

            $combined = @()
            foreach ($d in $dirChildren) { $combined += [pscustomobject]@{ type = "directory"; path = $d } }
            foreach ($f in $fileChildren) { $combined += [pscustomobject]@{ type = "file"; path = $f } }

            for ($i = $combined.Count - 1; $i -ge 0; $i--) {
                $stack.Push(@{ kind = "node"; type = $combined[$i].type; path = $combined[$i].path; depth = ($depth + 1) })
            }
        }
        else {
            $repoPath = [string]$entry["path"]
            $type = [string]$entry["type"]
            $depth = [int]$entry["depth"]
            $node = New-NodeRecord -RepoPath $repoPath -Type $type -Depth $depth -TargetRootFullPath $TargetRootFullPath -Stats $stats
            [void]$nodes.Add($node)

            if (($stats["nodes"] % $StatusEvery) -eq 0 -or ((Get-Date) - $lastLog).TotalSeconds -ge $HeartbeatSeconds) {
                Write-Log -Message ("tracked nodes={0} dirs={1} files={2} current={3}" -f $stats["nodes"], $stats["directories"], $stats["files"], $repoPath)
                $lastLog = Get-Date
            }

            if ($type -eq "directory") {
                $stack.Push(@{ kind = "dir"; path = $repoPath; depth = $depth })
            }
        }
    }

    return [pscustomobject]@{ Nodes = @($nodes.ToArray()); Stats = $stats; ReportRoot = $rootPath }
}

# -----------------------------
# Text tree
# -----------------------------

function New-DirectoryTreeText {
    param([object[]]$DirectoryNodes)

    $childrenByParent = @{}
    foreach ($node in $DirectoryNodes) {
        if ($node.path -eq ".") { continue }
        if ($node.type -ne "directory") { continue }
        $parent = $node.parent
        if ($null -eq $parent) { $parent = "." }
        $key = ([string]$parent).ToLowerInvariant()
        if (-not $childrenByParent.ContainsKey($key)) { $childrenByParent[$key] = New-Object System.Collections.ArrayList }
        [void]$childrenByParent[$key].Add($node)
    }

    $tee = ([string][char]0x251c) + ([string][char]0x2500) + ([string][char]0x2500) + " "
    $last = ([string][char]0x2514) + ([string][char]0x2500) + ([string][char]0x2500) + " "
    $bar = ([string][char]0x2502) + "   "
    $space = "    "
    if ($AsciiTree) {
        $tee = "+-- "
        $last = "\-- "
        $bar = "|   "
    }

    $lines = New-Object System.Collections.ArrayList
    [void]$lines.Add("# Repository directory tree")
    [void]$lines.Add("# Generated UTC: $((Get-Date).ToUniversalTime().ToString("o"))")
    [void]$lines.Add("# Contains: directories only; files are not listed here.")
    [void]$lines.Add("# Machine-readable equivalent: dir_tree.json")
    [void]$lines.Add("")
    [void]$lines.Add(".")

    $stack = New-Object System.Collections.Stack
    $stack.Push(@{ parent = "."; prefix = ""; mode = "children" })

    while ($stack.Count -gt 0) {
        $entry = $stack.Pop()
        if ([string]$entry["mode"] -eq "children") {
            $parent = [string]$entry["parent"]
            $prefix = [string]$entry["prefix"]
            $key = $parent.ToLowerInvariant()
            if (-not $childrenByParent.ContainsKey($key)) { continue }
            $children = @($childrenByParent[$key])
            for ($i = $children.Count - 1; $i -ge 0; $i--) {
                $child = $children[$i]
                $isLast = ($i -eq ($children.Count - 1))
                $connector = $tee
                $nextPrefix = $prefix + $bar
                if ($isLast) {
                    $connector = $last
                    $nextPrefix = $prefix + $space
                }
                $stack.Push(@{ mode = "write"; node = $child; prefix = $prefix; connector = $connector; next_prefix = $nextPrefix })
            }
        }
        else {
            $node = $entry["node"]
            $name = [string]$node.name + "/"
            if ($node.is_link) { $name = $name + " -> [link]" }
            [void]$lines.Add(([string]$entry["prefix"] + [string]$entry["connector"] + $name))
            if (-not $node.is_link) {
                $stack.Push(@{ mode = "children"; parent = [string]$node.path; prefix = [string]$entry["next_prefix"] })
            }
        }
    }

    return ([string]::Join("`n", [string[]]$lines.ToArray()) + "`n")
}

# -----------------------------
# Zip / cleanup
# -----------------------------

function Get-7ZipCommand {
    foreach ($name in @("7z", "7za", "7zr")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($null -ne $cmd) { return $cmd.Source }
    }
    return $null
}

function New-ZipFromFiles {
    param(
        [string[]]$Files,
        [string]$ZipPath,
        [string]$OutputDir
    )

    $staging = Join-Path $OutputDir (".dirfiles_staging_" + $PID)
    if (Test-Path -LiteralPath $staging) { Remove-Item -LiteralPath $staging -Recurse -Force }
    New-Item -ItemType Directory -Path $staging -Force | Out-Null

    try {
        foreach ($file in $Files) {
            Copy-Item -LiteralPath $file -Destination (Join-Path $staging (Split-Path -Leaf $file)) -Force
        }

        $part = "$ZipPath.part"
        if (Test-Path -LiteralPath $part) { Remove-Item -LiteralPath $part -Force }
        if (Test-Path -LiteralPath $ZipPath) { Remove-Item -LiteralPath $ZipPath -Force }

        $engine = "dotnet-zip"
        if ($Use7Zip) {
            $seven = Get-7ZipCommand
            if ([string]::IsNullOrWhiteSpace($seven)) {
                Add-WarningMessage -Message "-Use7Zip was supplied, but 7z/7za/7zr was not found. Falling back to .NET ZIP."
            }
            else {
                Write-Log -Message "Creating ZIP with 7-Zip: $seven"
                Push-Location -LiteralPath $staging
                try {
                    $zipAbs = [System.IO.Path]::GetFullPath($part)
                    $args = @("a", "-tzip", "-mx=9", "-mfb=258", "-mpass=15", $zipAbs, ".\*")
                    $output = & $seven @args 2>&1
                    if ($LASTEXITCODE -eq 0 -and (Test-Path -LiteralPath $part)) {
                        $engine = "7zip-zip-deflate"
                    }
                    else {
                        Add-WarningMessage -Message "7-Zip failed. Falling back to .NET ZIP. Output: $($output -join ' ')"
                        if (Test-Path -LiteralPath $part) { Remove-Item -LiteralPath $part -Force }
                    }
                }
                finally {
                    Pop-Location
                }
            }
        }

        if (-not (Test-Path -LiteralPath $part)) {
            Write-Log -Message "Creating ZIP with .NET CompressionLevel.Optimal"
            Add-Type -AssemblyName System.IO.Compression.FileSystem | Out-Null
            [System.IO.Compression.ZipFile]::CreateFromDirectory($staging, $part, [System.IO.Compression.CompressionLevel]::Optimal, $false)
            $engine = "dotnet-zip-optimal"
        }

        Move-Item -LiteralPath $part -Destination $ZipPath -Force
        return $engine
    }
    finally {
        if (Test-Path -LiteralPath $staging) { Remove-Item -LiteralPath $staging -Recurse -Force }
    }
}

function Remove-StaleGeneratedFiles {
    param([string]$OutputDir)

    if (-not (Test-Path -LiteralPath $OutputDir)) { return 0 }

    $patterns = @(
        "files_root.json", "files_*.json", "files_*.txt",
        "*.part", ".dirfiles_staging_*"
    )

    $removed = 0
    foreach ($pattern in $patterns) {
        $items = @(Get-ChildItem -LiteralPath $OutputDir -Force -Filter $pattern -ErrorAction SilentlyContinue)
        foreach ($item in $items) {
            if ($item.PSIsContainer) { Remove-Item -LiteralPath $item.FullName -Recurse -Force }
            else { Remove-Item -LiteralPath $item.FullName -Force }
            $removed = $removed + 1
        }
    }
    return $removed
}

# -----------------------------
# Main
# -----------------------------

try {
    Write-Log -Level "STEP" -Message "V7 startup: parsing succeeded; beginning run."

    $targetResolution = Resolve-TargetRoot -InputPath $Path
    $targetRootPath = [System.IO.Path]::GetFullPath($targetResolution.Path)
    $targetRootItem = Get-Item -LiteralPath $targetRootPath -ErrorAction Stop
    if (-not $targetRootItem.PSIsContainer) { throw "Target path is not a directory: $targetRootPath" }

    $outputDir = Join-Path $targetRootPath $TmpFolderName
    $effectiveExcludeDir = Get-EffectiveExcludeDirs
    $gitMetadata = Get-GitMetadata -RootPath $targetRootPath
    $sourceMode = "filesystem"
    if ($TrackedOnly) { $sourceMode = "git_tracked" }

    Write-Log -Message "Target selection:       $($targetResolution.Reason)"
    Write-Log -Message "Target root:            $targetRootPath"
    Write-Log -Message "Output dir:             $outputDir"
    Write-Log -Message "Source mode:            $sourceMode"
    Write-Log -Message "Schema:                 $SchemaName"
    Write-Log -Message "Lean mode:              $Lean"
    Write-Log -Message "Use 7-Zip:              $Use7Zip"
    Write-Log -Message "Keep temp JSON reports: $KeepJsonReports"
    if ($effectiveExcludeDir.Count -gt 0) { Write-Log -Message "Excluded dir names:     $($effectiveExcludeDir -join ', ')" }

    if (-not (Test-Path -LiteralPath $outputDir)) {
        Write-Log -Message "Creating output directory."
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }

    $removedStale = Remove-StaleGeneratedFiles -OutputDir $outputDir
    if ($removedStale -gt 0) { Write-Log -Message "Removed stale generated files: $removedStale" }

    $trackedIndex = $null
    if ($TrackedOnly) {
        Write-Log -Level "STEP" -Message "Building git tracked index with git ls-files."
        $trackedIndex = Build-TrackedIndex -RootPath $targetRootPath -EffectiveExcludeDir $effectiveExcludeDir
        Write-Log -Level "PASS" -Message ("Tracked index ready | raw={0} kept_files={1} dirs={2} excluded={3}" -f $trackedIndex.RawCount, $trackedIndex.Files.Count, $trackedIndex.Dirs.Count, $trackedIndex.ExcludedCount)
    }

    $zipInputFiles = New-Object System.Collections.ArrayList
    $temporaryReports = New-Object System.Collections.ArrayList
    $reportRecords = New-Object System.Collections.ArrayList

    # 1. Directory JSON.
    Write-Log -Level "STEP" -Message "Generating $DirTreeJsonFileName"
    if ($TrackedOnly) {
        $dirBuild = Build-TrackedReportNodes -TargetRootFullPath $targetRootPath -Index $trackedIndex -ReportRootPath "." -IncludeFiles:$false
    }
    else {
        $dirBuild = Build-FsReportNodes -TargetRootFullPath $targetRootPath -ReportRootFullPath $targetRootPath -OutputDirFullPath $outputDir -IncludeFiles:$false -EffectiveExcludeDir $effectiveExcludeDir
    }

    $dirTreeReport = New-ReportObject -ReportFileName $DirTreeJsonFileName -ReportKind "full_directory_tree" -SourceMode $sourceMode -IncludesFiles:$false -TargetRootName $targetRootItem.Name -ReportRootPath "." -GitMetadata $gitMetadata -EffectiveExcludeDir $effectiveExcludeDir -Nodes $dirBuild.Nodes -Stats $dirBuild.Stats
    $dirTreeJsonPath = Join-Path $outputDir $DirTreeJsonFileName
    Write-JsonFileAtomic -FilePath $dirTreeJsonPath -Object $dirTreeReport
    [void]$zipInputFiles.Add($dirTreeJsonPath)
    [void]$reportRecords.Add((New-FileRecord -FilePath $dirTreeJsonPath -Kind "kept_directory_tree_json" -KeptUncompressed:$true))
    Write-Log -Level "PASS" -Message ("Wrote {0} | dirs={1} excluded={2} errors={3}" -f $DirTreeJsonFileName, $dirBuild.Stats["directories"], $dirBuild.Stats["excluded_directories"], $dirBuild.Stats["read_errors"])

    # 2. Human tree.
    Write-Log -Level "STEP" -Message "Generating $DirTreeTextFileName"
    $dirTreeText = New-DirectoryTreeText -DirectoryNodes $dirBuild.Nodes
    $dirTreeTextPath = Join-Path $outputDir $DirTreeTextFileName
    Write-TextFileAtomic -FilePath $dirTreeTextPath -Text $dirTreeText
    [void]$zipInputFiles.Add($dirTreeTextPath)
    [void]$reportRecords.Add((New-FileRecord -FilePath $dirTreeTextPath -Kind "kept_directory_tree_text" -KeptUncompressed:$true))
    Write-Log -Level "PASS" -Message "Wrote $DirTreeTextFileName"

    # 3. Root-level files.
    Write-Log -Level "STEP" -Message "Generating $RootFilesFileName"
    if ($TrackedOnly) {
        $rootStatsFinal = New-Stats
        $rootNodeList = New-Object System.Collections.ArrayList
        [void]$rootNodeList.Add((New-NodeRecord -RepoPath "." -Type "directory" -Depth 0 -TargetRootFullPath $targetRootPath -Stats $rootStatsFinal))
        foreach ($filePath in (Get-SetValuesSorted -Set $trackedIndex.RootFiles)) {
            [void]$rootNodeList.Add((New-NodeRecord -RepoPath $filePath -Type "file" -Depth 1 -TargetRootFullPath $targetRootPath -Stats $rootStatsFinal))
        }
        $rootNodes = @($rootNodeList.ToArray())
    }
    else {
        $rootStatsFinal = New-Stats
        $rootNodeList = New-Object System.Collections.ArrayList
        [void]$rootNodeList.Add((New-NodeRecord -RepoPath "." -Type "directory" -Depth 0 -TargetRootFullPath $targetRootPath -Stats $rootStatsFinal))
        try {
            $rootFiles = @(Get-ChildItem -LiteralPath $targetRootPath -Force -File -ErrorAction Stop | Sort-Object @{ Expression = { $_.Name.ToLowerInvariant() } }, Name)
            foreach ($file in $rootFiles) {
                $rp = Convert-FullPathToRepoPath -FullPath $file.FullName -RootPath $targetRootPath
                [void]$rootNodeList.Add((New-NodeRecord -RepoPath $rp -Type "file" -Depth 1 -TargetRootFullPath $targetRootPath -Stats $rootStatsFinal))
            }
        }
        catch {
            Add-Stat -Stats $rootStatsFinal -Key "read_errors"
            Add-WarningMessage -Message "Could not read root-level files: $($_.Exception.Message)"
        }
        $rootNodes = @($rootNodeList.ToArray())
    }

    $rootReport = New-ReportObject -ReportFileName $RootFilesFileName -ReportKind "root_level_files" -SourceMode $sourceMode -IncludesFiles:$true -TargetRootName $targetRootItem.Name -ReportRootPath "." -GitMetadata $gitMetadata -EffectiveExcludeDir $effectiveExcludeDir -Nodes $rootNodes -Stats $rootStatsFinal
    $rootFilesPath = Join-Path $outputDir $RootFilesFileName
    Write-JsonFileAtomic -FilePath $rootFilesPath -Object $rootReport
    [void]$zipInputFiles.Add($rootFilesPath)
    [void]$temporaryReports.Add($rootFilesPath)
    [void]$reportRecords.Add((New-FileRecord -FilePath $rootFilesPath -Kind "temporary_root_files_json" -KeptUncompressed:$KeepJsonReports))
    Write-Log -Level "PASS" -Message ("Wrote {0} | files={1}" -f $RootFilesFileName, $rootStatsFinal["files"])

    # 4. First-level directory reports.
    Write-Log -Level "STEP" -Message "Finding first-level directories."
    if ($TrackedOnly) {
        $firstLevelDirs = @(Get-SetValuesSorted -Set $trackedIndex.FirstLevelDirs)
    }
    else {
        $rawDirs = @(Get-ChildItem -LiteralPath $targetRootPath -Force -Directory -ErrorAction Stop | Sort-Object @{ Expression = { $_.Name.ToLowerInvariant() } }, Name)
        $firstLevelDirs = @()
        foreach ($dir in $rawDirs) {
            if (-not (Test-FsDirectoryExcluded -DirectoryInfo $dir -OutputDirFullPath $outputDir -ExcludeGit:(-not $IncludeGit) -EffectiveExcludeDir $effectiveExcludeDir)) {
                $firstLevelDirs += $dir
            }
        }
    }

    Write-Log -Message "First-level directories to report: $($firstLevelDirs.Count)"
    $usedReportNames = @{}

    for ($i = 0; $i -lt $firstLevelDirs.Count; $i++) {
        $ordinal = $i + 1
        $dirName = $null
        $reportRootPath = $null
        $reportRootFullPath = $null

        if ($TrackedOnly) {
            $reportRootPath = [string]$firstLevelDirs[$i]
            $dirName = $reportRootPath
        }
        else {
            $dirInfo = $firstLevelDirs[$i]
            $dirName = $dirInfo.Name
            $reportRootFullPath = $dirInfo.FullName
            $reportRootPath = Convert-FullPathToRepoPath -FullPath $reportRootFullPath -RootPath $targetRootPath
        }

        Write-Log -Level "STEP" -Message ("Generating [{0}/{1}] {2}/" -f $ordinal, $firstLevelDirs.Count, $dirName)

        $stem = Get-SafeFileStem -Name $dirName
        $baseName = "files_$stem"
        $finalName = $baseName
        $suffix = 2
        while ($usedReportNames.ContainsKey($finalName.ToLowerInvariant())) {
            $finalName = "$baseName`_$suffix"
            $suffix = $suffix + 1
        }
        $usedReportNames[$finalName.ToLowerInvariant()] = $true

        $reportFileName = "$finalName.json"
        $reportPath = Join-Path $outputDir $reportFileName

        if ($TrackedOnly) {
            $build = Build-TrackedReportNodes -TargetRootFullPath $targetRootPath -Index $trackedIndex -ReportRootPath $reportRootPath -IncludeFiles:$true
        }
        else {
            $build = Build-FsReportNodes -TargetRootFullPath $targetRootPath -ReportRootFullPath $reportRootFullPath -OutputDirFullPath $outputDir -IncludeFiles:$true -EffectiveExcludeDir $effectiveExcludeDir
        }

        $report = New-ReportObject -ReportFileName $reportFileName -ReportKind "first_level_directory_tree_with_files" -SourceMode $sourceMode -IncludesFiles:$true -TargetRootName $targetRootItem.Name -ReportRootPath $reportRootPath -GitMetadata $gitMetadata -EffectiveExcludeDir $effectiveExcludeDir -Nodes $build.Nodes -Stats $build.Stats
        Write-JsonFileAtomic -FilePath $reportPath -Object $report
        [void]$zipInputFiles.Add($reportPath)
        [void]$temporaryReports.Add($reportPath)
        [void]$reportRecords.Add((New-FileRecord -FilePath $reportPath -Kind "temporary_first_level_directory_json" -KeptUncompressed:$KeepJsonReports))

        Write-Log -Level "PASS" -Message ("Wrote {0} | nodes={1} dirs={2} files={3} missing={4} errors={5}" -f $reportFileName, $build.Stats["nodes"], $build.Stats["directories"], $build.Stats["files"], $build.Stats["missing"], $build.Stats["read_errors"])
    }

    # 5. Zip reports.
    $zipPath = Join-Path $outputDir $ZipFileName
    $zipEngine = $null
    $zipRecord = $null

    if ($NoZip) {
        Add-WarningMessage -Message "Skipping zip creation because -NoZip was supplied. Temporary JSON reports will be kept."
    }
    else {
        Write-Log -Level "STEP" -Message "Creating $ZipFileName"
        $zipEngine = New-ZipFromFiles -Files ([string[]]$zipInputFiles.ToArray([string])) -ZipPath $zipPath -OutputDir $outputDir
        $zipRecord = New-FileRecord -FilePath $zipPath -Kind "zip_archive" -KeptUncompressed:$true
        Write-Log -Level "PASS" -Message "Wrote $ZipFileName | engine=$zipEngine | size=$($zipRecord.size_human)"
    }

    # 6. Cleanup temporary JSON reports.
    $removedTemp = 0
    if ((-not $KeepJsonReports) -and (-not $NoZip)) {
        Write-Log -Level "STEP" -Message "Removing temporary uncompressed JSON reports."
        foreach ($file in $temporaryReports) {
            if (Test-Path -LiteralPath $file) {
                Remove-Item -LiteralPath $file -Force
                $removedTemp = $removedTemp + 1
            }
        }
    }
    else {
        Write-Log -Message "Temporary JSON reports kept."
    }

    # 7. Manifest.
    Write-Log -Level "STEP" -Message "Writing $ManifestFileName"
    $elapsed = (Get-Date) - $script:StartTime
    $manifest = [ordered]@{
        _readme = [ordered]@{
            note = "Strict JSON manifest for the repo-dirfiles run."
            upload_hint = "For GPT analysis, upload dir_tree.json plus dirfiles.zip. dir_tree.txt is for human inspection."
        }
        _meta = [ordered]@{
            schema = $ManifestSchemaName
            generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
            target_root_name = $targetRootItem.Name
            target_selection_reason = $targetResolution.Reason
            source_mode = $sourceMode
            lean_mode = [bool]$Lean
            include_git = [bool]$IncludeGit
            use_7zip_requested = [bool]$Use7Zip
            zip_engine = $zipEngine
            absolute_paths_included = [bool]$IncludeAbsolutePaths
            effective_excluded_directory_names = $effectiveExcludeDir
            git = $gitMetadata
        }
        results = [ordered]@{
            report_files = @($reportRecords.ToArray())
            zip_file = $zipRecord
            temporary_reports_removed = $removedTemp
            warnings_total = $script:WarningCount
            warnings_in_manifest = @($script:Warnings.ToArray())
            elapsed_seconds = [math]::Round($elapsed.TotalSeconds, 3)
            elapsed_human = ("{0:hh\:mm\:ss}" -f $elapsed)
        }
    }

    if ($IncludeAbsolutePaths) {
        $manifest["_meta"]["target_root_absolute"] = $targetRootPath
        $manifest["_meta"]["output_dir_absolute"] = $outputDir
    }

    $manifestPath = Join-Path $outputDir $ManifestFileName
    Write-JsonFileAtomic -FilePath $manifestPath -Object $manifest
    $manifestRecord = New-FileRecord -FilePath $manifestPath -Kind "kept_manifest_json" -KeptUncompressed:$true
    Write-Log -Level "PASS" -Message "Wrote $ManifestFileName | size=$($manifestRecord.size_human)"

    Write-Host ""
    Write-Log -Level "PASS" -Message "DONE"
    Write-Log -Level "PASS" -Message "Target root:       $targetRootPath"
    Write-Log -Level "PASS" -Message "Output dir:        $outputDir"
    Write-Log -Level "PASS" -Message "Source mode:       $sourceMode"
    Write-Log -Level "PASS" -Message "Kept text tree:    $dirTreeTextPath"
    Write-Log -Level "PASS" -Message "Kept JSON tree:    $dirTreeJsonPath"
    Write-Log -Level "PASS" -Message "Kept manifest:     $manifestPath"
    if (-not $NoZip) { Write-Log -Level "PASS" -Message "Zip file:          $zipPath" }
    Write-Log -Level "PASS" -Message "Warnings:          $script:WarningCount"
    Write-Log -Level "PASS" -Message ("Elapsed:           {0:hh\:mm\:ss}" -f $elapsed)
    Write-Host ""
}
catch {
    $script:ExitCode = 1
    Write-Host ""
    Write-Log -Level "ERROR" -Message "FAILED: $($_.Exception.Message)"
    if ($_.ScriptStackTrace) { Write-Host $_.ScriptStackTrace }
    Write-Host ""
}
finally {
    if (Test-ShouldPause) {
        Write-Host "Press Enter to close..."
        [void](Read-Host)
    }
}

exit $script:ExitCode
