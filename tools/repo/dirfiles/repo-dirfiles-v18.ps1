<#
repo-dirfiles-v18.ps1

Right-click friendly repository structure exporter.

Default behavior:
  - Resolve the Git worktree root from the script location first.
  - Write outputs to <repo-root>/tmp even when the script lives in tools/dirfiles.
  - Prefer Git tracked files for clean repo analysis.
  - Fall back to a lean filesystem scan if Git is unavailable or fails.
  - Use bright foreground colors only after the one-time session theme.
  - Bracketed fixed-width status labels: [INFO], [STEP], [RUN], [PASS], [WARN], [ERROR].
  - Timestamp column uses readable grey; default text is white.
  - [STEP] is cyan, [RUN] live/progress is magenta, [PASS] is green, warnings are yellow, errors are red.
  - Use one transient live status line plus readable milestone lines.

Kept outputs:
  tmp/dir_tree.txt
  tmp/dir_tree.json
  tmp/dirfiles_manifest.json
  tmp/dirfiles_run.log
  tmp/dirfiles.zip

Temporary outputs, removed after successful zip unless -KeepJsonReports:
  tmp/files_root.json
  tmp/files_<first-level-dir>.json
#>

param(
    [Parameter(Position = 0)]
    [string]$Path,

    [ValidateSet("Live", "Compact", "Quiet", "Verbose")]
    [string]$StatusMode = "Live",

    [ValidateSet("Auto", "TrueColor", "ConsoleColor", "Mono")]
    [string]$Theme = "Auto",

    # Sets the current console session to a readable black-background theme at startup.
    # This changes only the current window/session, not saved console defaults.
    [switch]$NoConsoleTheme,

    # Disables ANSI truecolor even when supported.
    [switch]$NoAnsi,

    [ValidateSet("Auto", "Always", "Never")]
    [string]$PauseMode = "Auto",

    [switch]$Filesystem,
    [switch]$TrackedOnly,
    [switch]$IncludeUntracked,
    [switch]$IncludeGit,
    [switch]$NoLean,
    [switch]$No7Zip,
    [switch]$NoZip,
    [switch]$KeepJsonReports,
    [switch]$IncludeAbsolutePaths,
    [switch]$AsciiTree,
    [switch]$NoColor,
    [switch]$Trace,
    [switch]$StrictGit,

    [string[]]$ExcludeDir = @(),

    [ValidateRange(1, 1000000)]
    [int]$StatusEvery = 800,

    [ValidateRange(100, 10000)]
    [int]$LiveMinIntervalMs = 250
)

$ErrorActionPreference = "Stop"

# -----------------------------
# Constants and state
# -----------------------------

$TmpFolderName = "tmp"
$ZipFileName = "dirfiles.zip"
$RunLogFileName = "dirfiles_run.log"
$ManifestFileName = "dirfiles_manifest.json"
$DirTreeJsonFileName = "dir_tree.json"
$DirTreeTextFileName = "dir_tree.txt"
$RootFilesFileName = "files_root.json"
$SchemaName = "repo-dirfiles-json-v18"

$DefaultLeanExcludes = @(
    ".git", "tmp",
    "out", "build", "dist", "target", "bin", "obj",
    "node_modules", ".venv", "venv", "env",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".tox", ".nox", ".next", ".nuxt", ".gradle", ".idea", ".vs",
    "coverage", ".cache"
)

$script:StartTime = Get-Date
$script:RunLogPath = $null
$script:WarningCount = 0
$script:Warnings = New-Object System.Collections.ArrayList
$script:LiveActive = $false
$script:LastLiveAt = Get-Date "2000-01-01"
$script:LastLiveText = ""
$script:ExitCode = 0
$script:UseColor = (-not $NoColor) -and ($Theme -ne "Mono")
$script:UseAnsi = $false
$script:Esc = [char]27
$script:LogLevelWidth = 7
$script:KeyColumnWidth = 16

# -----------------------------
# Console UI: readable current-session theme + foreground-only log roles
# -----------------------------

function Enable-VirtualTerminalOutput {
    try {
        if ($NoAnsi -or $Theme -eq "ConsoleColor" -or $Theme -eq "Mono") { return $false }
        if (-not ("RepoDirfilesConsoleNative" -as [type])) {
            $source = @"
using System;
using System.Runtime.InteropServices;

public static class RepoDirfilesConsoleNative {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern IntPtr GetStdHandle(int nStdHandle);

    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern bool GetConsoleMode(IntPtr hConsoleHandle, out int lpMode);

    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern bool SetConsoleMode(IntPtr hConsoleHandle, int dwMode);
}
"@
            Add-Type -TypeDefinition $source -ErrorAction Stop | Out-Null
        }

        $stdOut = [RepoDirfilesConsoleNative]::GetStdHandle(-11)
        if ($stdOut -eq [IntPtr]::Zero) { return $false }

        $mode = 0
        if (-not [RepoDirfilesConsoleNative]::GetConsoleMode($stdOut, [ref]$mode)) { return $false }

        $ENABLE_VIRTUAL_TERMINAL_PROCESSING = 4
        $newMode = $mode -bor $ENABLE_VIRTUAL_TERMINAL_PROCESSING

        if (-not [RepoDirfilesConsoleNative]::SetConsoleMode($stdOut, $newMode)) { return $false }
        return $true
    }
    catch {
        return $false
    }
}

function Initialize-ConsoleSessionTheme {
    # This is deliberately a session/window theme, not per-line background styling.
    # It fixes right-click PowerShell windows whose saved palette/background makes
    # normal ConsoleColor output unreadable.
    if (-not $NoConsoleTheme) {
        try {
            [Console]::ForegroundColor = [ConsoleColor]::White
            [Console]::BackgroundColor = [ConsoleColor]::Black
            $raw = $Host.UI.RawUI
            $raw.ForegroundColor = "White"
            $raw.BackgroundColor = "Black"
            Clear-Host
        }
        catch { }
    }

    $script:UseAnsi = $false
    if ($script:UseColor -and $Theme -ne "ConsoleColor") {
        $script:UseAnsi = Enable-VirtualTerminalOutput
    }

    if ($script:UseAnsi) {
        # Truecolor foregrounds mostly bypass customized conhost palette slots.
        # Keep a black background for the current screen after the one-time theme setup.
        [Console]::Write("$($script:Esc)[48;2;0;0;0m$($script:Esc)[38;2;235;235;235m")
        if (-not $NoConsoleTheme) {
            [Console]::Write("$($script:Esc)[2J$($script:Esc)[H")
        }
    }
}

function Get-AnsiForRole {
    param([string]$Role)
    if (-not $script:UseAnsi) { return "" }
    # Foreground-only semantic palette. Background is set once at startup.
    switch ($Role) {
        "TIME"     { return "$($script:Esc)[38;2;160;160;160m" }     # readable grey timestamp
        "STEP"     { return "$($script:Esc)[1;38;2;0;230;255m" }     # bright cyan
        "PASS"     { return "$($script:Esc)[1;38;2;0;255;110m" }     # bright green
        "RUN"      { return "$($script:Esc)[1;38;2;255;235;0m" }     # bright yellow for persisted RUN events
        "PROGRESS" { return "$($script:Esc)[1;38;2;255;80;255m" }    # bright magenta live line
        "WARN"     { return "$($script:Esc)[1;38;2;255;235;0m" }     # bright yellow
        "NOTE"     { return "$($script:Esc)[1;38;2;255;235;0m" }     # bright yellow
        "ERROR"    { return "$($script:Esc)[1;38;2;255;70;70m" }     # bright red
        "FAIL"     { return "$($script:Esc)[1;38;2;255;70;70m" }     # bright red
        default     { return "$($script:Esc)[38;2;230;230;230m" }     # light grey-white
    }
}

function Get-ConsoleColorForRole {
    param([string]$Role)
    # No Black, no Dark*, no Gray/Grey foregrounds.
    if (-not $script:UseColor) { return [ConsoleColor]::White }
    switch ($Role) {
        "TIME"     { return [ConsoleColor]::Gray }
        "STEP"     { return [ConsoleColor]::Cyan }
        "PASS"     { return [ConsoleColor]::Green }
        "RUN"      { return [ConsoleColor]::Yellow }
        "PROGRESS" { return [ConsoleColor]::Magenta }
        "WARN"     { return [ConsoleColor]::Yellow }
        "NOTE"     { return [ConsoleColor]::Yellow }
        "ERROR"    { return [ConsoleColor]::Red }
        "FAIL"     { return [ConsoleColor]::Red }
        default     { return [ConsoleColor]::White }
    }
}

function Get-ElapsedText {
    $elapsed = (Get-Date) - $script:StartTime
    return ("{0:hh\:mm\:ss}" -f $elapsed)
}

function Get-ConsoleWidthSafe {
    try {
        $w = [Console]::WindowWidth
        if ($w -lt 60) { return 80 }
        return ($w - 1)
    }
    catch { return 120 }
}

function Limit-TextMiddle {
    param(
        [string]$Text,
        [int]$Max = 100
    )
    if ($null -eq $Text) { return "" }
    if ($Max -lt 10) { return $Text.Substring(0, [Math]::Min($Text.Length, $Max)) }
    if ($Text.Length -le $Max) { return $Text }
    $left = [int][Math]::Floor(($Max - 5) / 2)
    $right = $Max - $left - 5
    return ($Text.Substring(0, $left) + " ... " + $Text.Substring($Text.Length - $right))
}

function Format-Count {
    param([long]$Value)
    return ("{0:N0}" -f $Value)
}

function Format-LevelText {
    param([string]$Level)
    $levelName = "INFO"
    if (-not [string]::IsNullOrWhiteSpace($Level)) {
        $levelName = $Level.ToUpperInvariant()
    }
    return (("[" + $levelName + "]") + (" " * $script:LogLevelWidth)).Substring(0, $script:LogLevelWidth)
}

function Format-LogTextLine {
    param(
        [string]$Timestamp,
        [string]$Level,
        [string]$Message
    )
    return ("{0} {1}  {2}" -f $Timestamp, (Format-LevelText -Level $Level), $Message)
}

function Write-RunLog {
    param(
        [string]$Level,
        [string]$Message
    )
    if ([string]::IsNullOrWhiteSpace($script:RunLogPath)) { return }
    try {
        $line = Format-LogTextLine -Timestamp ((Get-Date).ToUniversalTime().ToString("o")) -Level $Level -Message $Message
        Add-Content -LiteralPath $script:RunLogPath -Value $line -Encoding UTF8
    }
    catch { }
}

function Write-TextRole {
    param(
        [string]$Text,
        [string]$Role = "INFO",
        [switch]$NoNewLine
    )

    if ($script:UseAnsi) {
        [Console]::Write((Get-AnsiForRole $Role) + $Text)
        [Console]::Write((Get-AnsiForRole "INFO"))
        if (-not $NoNewLine) { [Console]::WriteLine() }
        return
    }

    try {
        [Console]::ForegroundColor = Get-ConsoleColorForRole $Role
        if ($NoNewLine) { [Console]::Write($Text) } else { [Console]::WriteLine($Text) }
        [Console]::ForegroundColor = [ConsoleColor]::White
    }
    catch {
        Write-Host $Text -ForegroundColor White -NoNewline:$NoNewLine
        if (-not $NoNewLine) { Write-Host "" -ForegroundColor White }
    }
}

function Clear-LiveLine {
    if (-not $script:LiveActive) { return }
    try {
        $w = Get-ConsoleWidthSafe
        if ($script:UseAnsi) {
            [Console]::Write("`r" + (Get-AnsiForRole "INFO") + (" " * $w) + "`r")
        }
        else {
            [Console]::ForegroundColor = [ConsoleColor]::White
            [Console]::Write("`r" + (" " * $w) + "`r")
        }
    }
    catch {
        Write-TextRole -Text "" -Role "INFO"
    }
    $script:LiveActive = $false
    $script:LastLiveText = ""
}

function Write-EventLine {
    param(
        [string]$Level,
        [string]$Message
    )
    if ($StatusMode -eq "Quiet" -and $Level -notin @("ERROR", "WARN", "PASS")) {
        Write-RunLog -Level $Level -Message $Message
        return
    }

    Clear-LiveLine

    $elapsed = Get-ElapsedText
    $levelText = Format-LevelText -Level $Level
    $prefix = "$elapsed "
    $available = [Math]::Max(30, (Get-ConsoleWidthSafe - $prefix.Length - $levelText.Length - 2))
    $msg = Limit-TextMiddle -Text $Message -Max $available

    # Fixed-column, log-style whitespace: timestamp, bracketed level, message.
    Write-TextRole -Text $prefix -Role "TIME" -NoNewLine
    Write-TextRole -Text $levelText -Role $Level -NoNewLine
    Write-TextRole -Text "  " -Role "INFO" -NoNewLine

    if ($Level -eq "INFO") {
        Write-TextRole -Text $msg -Role "INFO"
    }
    else {
        Write-TextRole -Text $msg -Role $Level
    }

    Write-RunLog -Level $Level -Message $Message
}

function Write-KeyValueLine {
    param(
        [string]$Key,
        [string]$Value,
        [string]$Level = "INFO"
    )
    # Fixed columns; no tabs, no per-line background color. Copy/paste friendly.
    $keyFixed = ($Key + (" " * $script:KeyColumnWidth)).Substring(0, $script:KeyColumnWidth)
    Write-EventLine -Level $Level -Message ($keyFixed + " " + $Value)
}

function Write-LiveLine {
    param(
        [string]$Phase,
        [string]$Detail = "",
        [string]$Counters = "",
        [switch]$Force
    )
    if ($StatusMode -ne "Live") { return }

    $now = Get-Date
    if (-not $Force) {
        $ms = ($now - $script:LastLiveAt).TotalMilliseconds
        if ($ms -lt $LiveMinIntervalMs) { return }
    }
    $script:LastLiveAt = $now

    $elapsed = Get-ElapsedText
    $w = Get-ConsoleWidthSafe
    $core = Format-LogTextLine -Timestamp $elapsed -Level "RUN" -Message $Phase
    if (-not [string]::IsNullOrWhiteSpace($Counters)) { $core += " | " + $Counters }
    if (-not [string]::IsNullOrWhiteSpace($Detail)) { $core += " | " + $Detail }

    $text = Limit-TextMiddle -Text $core -Max $w
    $text = $text.PadRight($w)

    try {
        [Console]::Write("`r")
        if ($script:UseAnsi) {
            [Console]::Write((Get-AnsiForRole "PROGRESS") + $text + (Get-AnsiForRole "INFO"))
        }
        else {
            [Console]::ForegroundColor = Get-ConsoleColorForRole "PROGRESS"
            [Console]::Write($text)
            [Console]::ForegroundColor = [ConsoleColor]::White
        }
        $script:LiveActive = $true
        $script:LastLiveText = $text
    }
    catch {
        Write-TextRole -Text $text -Role "PROGRESS"
        $script:LiveActive = $false
    }
}

Initialize-ConsoleSessionTheme

function Add-WarningMessage {
    param([string]$Message)
    $script:WarningCount++
    if ($script:Warnings.Count -lt 100) {
        [void]$script:Warnings.Add([ordered]@{
            time_utc = (Get-Date).ToUniversalTime().ToString("o")
            message = $Message
        })
    }
    Write-EventLine -Level "WARN" -Message $Message
}

function Format-ByteSize {
    param([long]$Bytes)
    if ($Bytes -ge 1GB) { return "{0:N2} GB" -f ($Bytes / 1GB) }
    if ($Bytes -ge 1MB) { return "{0:N2} MB" -f ($Bytes / 1MB) }
    if ($Bytes -ge 1KB) { return "{0:N2} KB" -f ($Bytes / 1KB) }
    return "$Bytes B"
}

# -----------------------------
# Path / Git helpers
# -----------------------------

function Test-IsDirectoryItem {
    param([object]$Item)
    return ($Item -is [System.IO.DirectoryInfo])
}

function Test-IsReparsePoint {
    param([System.IO.FileSystemInfo]$Item)
    return (($Item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)
}

function Normalize-RepoPath {
    param([string]$PathText)
    if ($null -eq $PathText) { return "" }
    $p = $PathText.Trim()
    $p = $p -replace "\\", "/"
    while ($p.StartsWith("/")) { $p = $p.Substring(1) }
    while ($p.Contains("//")) { $p = $p.Replace("//", "/") }
    if ($p -eq "") { return "." }
    return $p
}

function Get-ParentRepoPath {
    param([string]$RepoPath)
    $p = Normalize-RepoPath $RepoPath
    if ($p -eq "." -or [string]::IsNullOrWhiteSpace($p)) { return $null }
    $i = $p.LastIndexOf("/")
    if ($i -lt 0) { return "." }
    return $p.Substring(0, $i)
}

function Get-RepoName {
    param([string]$RepoPath)
    $p = Normalize-RepoPath $RepoPath
    if ($p -eq ".") { return "." }
    $i = $p.LastIndexOf("/")
    if ($i -lt 0) { return $p }
    return $p.Substring($i + 1)
}

function Get-Depth {
    param([string]$RepoPath)
    $p = Normalize-RepoPath $RepoPath
    if ($p -eq ".") { return 0 }
    return (($p -split "/").Count)
}

function Join-RepoPathToFullPath {
    param(
        [string]$RootPath,
        [string]$RepoPath
    )
    $p = Normalize-RepoPath $RepoPath
    if ($p -eq ".") { return $RootPath }
    $native = $p.Replace("/", [System.IO.Path]::DirectorySeparatorChar)
    return (Join-Path $RootPath $native)
}

function Convert-FullToRepoPath {
    param(
        [string]$RootPath,
        [string]$FullPath
    )
    $root = [System.IO.Path]::GetFullPath($RootPath).TrimEnd("\", "/")
    $full = [System.IO.Path]::GetFullPath($FullPath).TrimEnd("\", "/")
    if ($full.Equals($root, [System.StringComparison]::OrdinalIgnoreCase)) { return "." }
    if ($full.Length -le $root.Length) { return "." }
    $rel = $full.Substring($root.Length).TrimStart("\", "/")
    return Normalize-RepoPath $rel
}

function Get-GitCommandPath {
    $cmd = Get-Command git -ErrorAction SilentlyContinue
    if ($null -eq $cmd) { return $null }
    if ($cmd.Path) { return $cmd.Path }
    if ($cmd.Source) { return $cmd.Source }
    return "git"
}

function Invoke-GitSimpleLines {
    param(
        [string]$RootPath,
        [string[]]$Arguments
    )
    try {
        $output = & git -C $RootPath @Arguments 2>$null
        if ($LASTEXITCODE -ne 0) { return $null }
        return @($output)
    }
    catch { return $null }
}

function Get-GitRoot {
    param([string]$StartPath)
    $git = Get-GitCommandPath
    if (-not [string]::IsNullOrWhiteSpace($git)) {
        try {
            $root = & git -C $StartPath rev-parse --show-toplevel 2>$null
            if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($root)) {
                return [System.IO.Path]::GetFullPath(([string](@($root)[0])))
            }
        }
        catch { }
    }
    try {
        $item = Get-Item -LiteralPath $StartPath -ErrorAction Stop
        if (-not (Test-IsDirectoryItem $item)) { $item = $item.Directory }
        while ($null -ne $item) {
            if (Test-Path -LiteralPath (Join-Path $item.FullName ".git")) { return $item.FullName }
            $item = $item.Parent
        }
    }
    catch { }
    return $null
}

function Resolve-TargetRoot {
    param([string]$InputPath)
    if (-not [string]::IsNullOrWhiteSpace($InputPath)) {
        $resolved = (Resolve-Path -LiteralPath $InputPath).ProviderPath
        return [pscustomobject]@{ Path = $resolved; Reason = "explicit path argument" }
    }
    $scriptDir = $PSScriptRoot
    if (-not [string]::IsNullOrWhiteSpace($scriptDir)) {
        $scriptGitRoot = Get-GitRoot $scriptDir
        if (-not [string]::IsNullOrWhiteSpace($scriptGitRoot)) {
            return [pscustomobject]@{ Path = $scriptGitRoot; Reason = "Git worktree root detected from script location" }
        }
    }
    $cwd = (Get-Location).ProviderPath
    $cwdGitRoot = Get-GitRoot $cwd
    if (-not [string]::IsNullOrWhiteSpace($cwdGitRoot)) {
        return [pscustomobject]@{ Path = $cwdGitRoot; Reason = "Git worktree root detected from current directory" }
    }
    if ([string]::IsNullOrWhiteSpace($scriptDir)) {
        return [pscustomobject]@{ Path = $cwd; Reason = "fallback to current directory" }
    }
    $sd = Get-Item -LiteralPath $scriptDir
    if ($sd.Name -ieq $TmpFolderName) {
        return [pscustomobject]@{ Path = $sd.Parent.FullName; Reason = "script is inside tmp; using parent" }
    }
    return [pscustomobject]@{ Path = $sd.FullName; Reason = "fallback to script directory" }
}

function Get-GitMetadata {
    param([string]$RootPath)
    $root = Get-GitRoot $RootPath
    if ([string]::IsNullOrWhiteSpace($root)) {
        return [ordered]@{ is_git_worktree = $false; branch = $null; commit = $null; dirty = $null }
    }
    $branch = Invoke-GitSimpleLines -RootPath $root -Arguments @("branch", "--show-current")
    $commit = Invoke-GitSimpleLines -RootPath $root -Arguments @("rev-parse", "HEAD")
    $status = Invoke-GitSimpleLines -RootPath $root -Arguments @("status", "--porcelain")
    $branchValue = $null
    $commitValue = $null
    $dirtyValue = $null
    if ($null -ne $branch -and @($branch).Count -gt 0) { $branchValue = [string](@($branch)[0]) }
    if ($null -ne $commit -and @($commit).Count -gt 0) { $commitValue = [string](@($commit)[0]) }
    if ($null -ne $status) { $dirtyValue = (@($status).Count -gt 0) }
    return [ordered]@{
        is_git_worktree = $true
        branch = $branchValue
        commit = $commitValue
        dirty = $dirtyValue
    }
}

# -----------------------------
# External processes
# -----------------------------

function Start-ProcessWithSpinner {
    param(
        [string]$FilePath,
        [string[]]$ArgumentList,
        [string]$WorkingDirectory,
        [string]$StdOutPath,
        [string]$StdErrPath,
        [string]$Activity
    )
    if (Test-Path -LiteralPath $StdOutPath) { Remove-Item -LiteralPath $StdOutPath -Force }
    if (Test-Path -LiteralPath $StdErrPath) { Remove-Item -LiteralPath $StdErrPath -Force }
    $p = $null
    try {
        $p = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -WorkingDirectory $WorkingDirectory -RedirectStandardOutput $StdOutPath -RedirectStandardError $StdErrPath -NoNewWindow -PassThru
        $spin = @("-", "\", "|", "/")
        $i = 0
        while (-not $p.HasExited) {
            $i++
            $size = 0
            try { if (Test-Path -LiteralPath $StdOutPath) { $size = (Get-Item -LiteralPath $StdOutPath).Length } } catch { }
            $detail = "running " + $spin[$i % $spin.Count] + " output=" + (Format-ByteSize $size)
            Write-LiveLine -Phase $Activity -Counters "elapsed=$(Get-ElapsedText)" -Detail $detail -Force
            Start-Sleep -Milliseconds 250
            try { $p.Refresh() } catch { }
        }
        $p.WaitForExit()
        Clear-LiveLine
        return [int]$p.ExitCode
    }
    catch {
        Clear-LiveLine
        Add-WarningMessage ("process failed to start: " + $_.Exception.Message)
        return -9999
    }
    finally {
        if ($null -ne $p) { try { $p.Dispose() } catch { } }
    }
}

function Get-GitLsFilesLive {
    param(
        [string]$RootPath,
        [switch]$Others
    )
    $git = Get-GitCommandPath
    if ([string]::IsNullOrWhiteSpace($git)) { return $null }
    $outFile = [System.IO.Path]::GetTempFileName()
    $errFile = [System.IO.Path]::GetTempFileName()
    $args = @("-c", "core.quotepath=false", "ls-files")
    if ($Others) { $args = @("-c", "core.quotepath=false", "ls-files", "--others", "--exclude-standard") }
    $label = if ($Others) { "git untracked" } else { "git ls-files" }
    $code = Start-ProcessWithSpinner -FilePath $git -ArgumentList $args -WorkingDirectory $RootPath -StdOutPath $outFile -StdErrPath $errFile -Activity $label
    try {
        if ($code -ne 0) {
            $err = ""
            try { if (Test-Path -LiteralPath $errFile) { $err = (Get-Content -LiteralPath $errFile -Raw -ErrorAction SilentlyContinue) } } catch { }
            if (-not [string]::IsNullOrWhiteSpace($err)) { Add-WarningMessage ("git ls-files failed: " + (Limit-TextMiddle $err.Trim() 180)) }
            return $null
        }
        if (-not (Test-Path -LiteralPath $outFile)) { return @() }
        $lines = @(Get-Content -LiteralPath $outFile -ErrorAction Stop)
        return $lines
    }
    finally {
        try { if (Test-Path -LiteralPath $outFile) { Remove-Item -LiteralPath $outFile -Force } } catch { }
        try { if (Test-Path -LiteralPath $errFile) { Remove-Item -LiteralPath $errFile -Force } } catch { }
    }
}

# -----------------------------
# Index building
# -----------------------------

function New-Index {
    return @{
        files = @{}
        dirs = @{}
        root_files = @{}
        first_dirs = @{}
        dir_children = @{}
        file_children = @{}
        raw_count = 0
        excluded_count = 0
        missing_count = 0
        source_mode = "unknown"
    }
}

function Add-ToSet {
    param([hashtable]$Set, [string]$Value)
    if (-not $Set.ContainsKey($Value)) { $Set[$Value] = $true }
}

function Add-ChildSet {
    param([hashtable]$Map, [string]$Parent, [string]$Child)
    if (-not $Map.ContainsKey($Parent)) { $Map[$Parent] = @{} }
    if (-not $Map[$Parent].ContainsKey($Child)) { $Map[$Parent][$Child] = $true }
}

function Test-RepoPathExcluded {
    param(
        [string]$RepoPath,
        [string[]]$ExcludedNames
    )
    $p = Normalize-RepoPath $RepoPath
    if ($p -eq ".") { return $false }
    $parts = $p -split "/"
    foreach ($part in $parts) {
        foreach ($ex in $ExcludedNames) {
            if (-not [string]::IsNullOrWhiteSpace($ex) -and $part -ieq $ex) { return $true }
        }
    }
    return $false
}

function Add-FilePathToIndex {
    param(
        [hashtable]$Index,
        [string]$RepoFilePath,
        [string[]]$ExcludedNames
    )
    $filePath = Normalize-RepoPath $RepoFilePath
    if ($filePath -eq "." -or [string]::IsNullOrWhiteSpace($filePath)) { return }
    if (Test-RepoPathExcluded -RepoPath $filePath -ExcludedNames $ExcludedNames) {
        $Index["excluded_count"]++
        return
    }

    Add-ToSet -Set $Index["files"] -Value $filePath
    $parent = Get-ParentRepoPath $filePath
    if ($parent -eq ".") { Add-ToSet -Set $Index["root_files"] -Value $filePath }
    Add-ChildSet -Map $Index["file_children"] -Parent $parent -Child $filePath

    if ($parent -ne $null) {
        $acc = ""
        foreach ($part in ($parent -split "/")) {
            if ([string]::IsNullOrWhiteSpace($part) -or $part -eq ".") { continue }
            if ($acc -eq "") { $acc = $part } else { $acc = "$acc/$part" }
            Add-ToSet -Set $Index["dirs"] -Value $acc
            $p2 = Get-ParentRepoPath $acc
            if ($p2 -eq ".") { Add-ToSet -Set $Index["first_dirs"] -Value $acc }
            Add-ChildSet -Map $Index["dir_children"] -Parent $p2 -Child $acc
        }
    }
}

function Build-GitIndex {
    param(
        [string]$RootPath,
        [string[]]$ExcludedNames
    )
    Write-EventLine -Level "STEP" -Message "Loading tracked file list from Git index."
    $lines = Get-GitLsFilesLive -RootPath $RootPath
    if ($null -eq $lines) { return $null }
    if ($IncludeUntracked) {
        $other = Get-GitLsFilesLive -RootPath $RootPath -Others
        if ($null -ne $other) { $lines = @($lines) + @($other) }
    }
    $index = New-Index
    $index["source_mode"] = "git_tracked"
    $index["raw_count"] = @($lines).Count
    Add-ToSet -Set $index["dirs"] -Value "."
    $n = 0
    foreach ($line in @($lines)) {
        $n++
        Add-FilePathToIndex -Index $index -RepoFilePath ([string]$line) -ExcludedNames $ExcludedNames
        if (($n % $StatusEvery) -eq 0) {
            Write-LiveLine -Phase "indexing Git files" -Counters ("raw={0} kept={1} dirs={2} excl={3}" -f (Format-Count $n), (Format-Count $index["files"].Count), (Format-Count $index["dirs"].Count), (Format-Count $index["excluded_count"])) -Detail "building path map"
        }
    }
    Clear-LiveLine
    Write-EventLine -Level "PASS" -Message ("Git index ready | raw={0} kept_files={1} dirs={2} excluded={3}" -f (Format-Count $index["raw_count"]), (Format-Count $index["files"].Count), (Format-Count $index["dirs"].Count), (Format-Count $index["excluded_count"]))
    return $index
}

function Build-FilesystemIndex {
    param(
        [string]$RootPath,
        [string[]]$ExcludedNames
    )
    Write-EventLine -Level "STEP" -Message "Building lean filesystem index."
    $index = New-Index
    $index["source_mode"] = "filesystem"
    Add-ToSet -Set $index["dirs"] -Value "."
    $stack = New-Object System.Collections.Stack
    $rootItem = Get-Item -LiteralPath $RootPath
    $stack.Push($rootItem)
    $seen = 0
    while ($stack.Count -gt 0) {
        $dir = [System.IO.DirectoryInfo]$stack.Pop()
        $dirRepo = Convert-FullToRepoPath -RootPath $RootPath -FullPath $dir.FullName
        try {
            $items = @($dir.EnumerateFileSystemInfos())
        }
        catch {
            Add-WarningMessage ("Could not read directory: " + (Limit-TextMiddle $dirRepo 120) + " :: " + $_.Exception.Message)
            continue
        }
        foreach ($item in $items) {
            $seen++
            $rp = Convert-FullToRepoPath -RootPath $RootPath -FullPath $item.FullName
            if (Test-IsDirectoryItem $item) {
                if ((Test-RepoPathExcluded -RepoPath $rp -ExcludedNames $ExcludedNames) -or (Test-IsReparsePoint $item)) {
                    $index["excluded_count"]++
                    continue
                }
                Add-ToSet -Set $index["dirs"] -Value $rp
                $parent = Get-ParentRepoPath $rp
                if ($parent -eq ".") { Add-ToSet -Set $index["first_dirs"] -Value $rp }
                Add-ChildSet -Map $index["dir_children"] -Parent $parent -Child $rp
                $stack.Push($item)
            }
            else {
                Add-FilePathToIndex -Index $index -RepoFilePath $rp -ExcludedNames $ExcludedNames
            }
            if (($seen % $StatusEvery) -eq 0) {
                Write-LiveLine -Phase "filesystem scan" -Counters ("seen={0} files={1} dirs={2} excl={3}" -f (Format-Count $seen), (Format-Count $index["files"].Count), (Format-Count $index["dirs"].Count), (Format-Count $index["excluded_count"])) -Detail (Limit-TextMiddle $rp 50)
            }
        }
    }
    Clear-LiveLine
    Write-EventLine -Level "PASS" -Message ("Filesystem index ready | files={0} dirs={1} excluded={2}" -f (Format-Count $index["files"].Count), (Format-Count $index["dirs"].Count), (Format-Count $index["excluded_count"]))
    return $index
}

# -----------------------------
# Report generation
# -----------------------------

function New-Stats {
    return @{
        nodes = 0
        directories = 0
        files = 0
        missing = 0
        errors = 0
        total_file_bytes = [int64]0
        extension_counts = @{}
    }
}

function Add-ExtensionCount {
    param([hashtable]$Stats, [string]$Extension)
    $key = if ([string]::IsNullOrWhiteSpace($Extension)) { "[none]" } else { $Extension }
    if (-not $Stats["extension_counts"].ContainsKey($key)) { $Stats["extension_counts"][$key] = 0 }
    $Stats["extension_counts"][$key]++
}

function New-NodeRecord {
    param(
        [string]$RootPath,
        [string]$RepoPath,
        [string]$Type,
        [ref]$Id,
        [hashtable]$Stats
    )
    $Id.Value = [int]$Id.Value + 1
    $p = Normalize-RepoPath $RepoPath
    $full = Join-RepoPathToFullPath -RootPath $RootPath -RepoPath $p
    $exists = Test-Path -LiteralPath $full
    $size = $null
    $ext = $null
    $writeUtc = $null
    if ($Type -eq "file") {
        $Stats["files"]++
        $extRaw = [System.IO.Path]::GetExtension($p)
        if (-not [string]::IsNullOrWhiteSpace($extRaw)) { $ext = $extRaw.TrimStart(".").ToLowerInvariant() }
        Add-ExtensionCount -Stats $Stats -Extension $ext
        if ($exists) {
            try {
                $fi = Get-Item -LiteralPath $full -ErrorAction Stop
                $size = [int64]$fi.Length
                $writeUtc = $fi.LastWriteTimeUtc.ToString("o")
                $Stats["total_file_bytes"] = [int64]$Stats["total_file_bytes"] + $size
            }
            catch { $Stats["errors"]++ }
        }
        else { $Stats["missing"]++ }
    }
    else {
        $Stats["directories"]++
        if ($exists) {
            try { $di = Get-Item -LiteralPath $full -ErrorAction Stop; $writeUtc = $di.LastWriteTimeUtc.ToString("o") } catch { }
        }
    }
    $Stats["nodes"]++
    return [ordered]@{
        id = [int]$Id.Value
        type = $Type
        depth = (Get-Depth $p)
        path = $p
        parent = (Get-ParentRepoPath $p)
        name = (Get-RepoName $p)
        exists = [bool]$exists
        file_size_bytes = $size
        extension = $ext
        last_write_utc = $writeUtc
    }
}

function New-ReportObject {
    param(
        [string]$RootPath,
        [string]$ReportKind,
        [string]$ReportRoot,
        [bool]$IncludesFiles,
        [array]$Nodes,
        [hashtable]$Stats,
        [hashtable]$Index,
        [object]$GitMetadata,
        [string[]]$EffectiveExcludeDir
    )
    $meta = [ordered]@{
        schema = $SchemaName
        report_kind = $ReportKind
        generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        target_root_name = (Split-Path -Leaf $RootPath)
        report_root = $ReportRoot
        source_mode = $Index["source_mode"]
        includes_files = [bool]$IncludesFiles
        path_style = "repo-relative POSIX-style paths using forward slashes"
        excluded_directory_names = $EffectiveExcludeDir
        git = $GitMetadata
        absolute_paths_included = [bool]$IncludeAbsolutePaths
    }
    if ($IncludeAbsolutePaths) { $meta["target_root_absolute"] = $RootPath }
    return [ordered]@{
        _readme = [ordered]@{
            note = "Strict JSON. No comments. Human-readable guidance is stored in _readme and _meta."
            purpose = "Repository structure capture for human review, GPT upload, and agentic navigation."
            navigation = "Use nodes[].path and nodes[].parent. The root path is '.'."
        }
        _meta = $meta
        stats = [ordered]@{
            nodes = $Stats["nodes"]
            directories = $Stats["directories"]
            files = $Stats["files"]
            missing = $Stats["missing"]
            errors = $Stats["errors"]
            total_file_bytes = $Stats["total_file_bytes"]
            total_file_bytes_human = (Format-ByteSize $Stats["total_file_bytes"])
            extension_counts = $Stats["extension_counts"]
        }
        nodes = $Nodes
    }
}

function New-DirectoryTreeReport {
    param(
        [string]$RootPath,
        [hashtable]$Index,
        [object]$GitMetadata,
        [string[]]$EffectiveExcludeDir
    )
    $stats = New-Stats
    $id = 0
    $nodes = New-Object System.Collections.ArrayList
    $dirs = @($Index["dirs"].Keys | Sort-Object { if ($_ -eq ".") { "" } else { $_ } })
    foreach ($d in $dirs) {
        [void]$nodes.Add((New-NodeRecord -RootPath $RootPath -RepoPath $d -Type "directory" -Id ([ref]$id) -Stats $stats))
        if (($id % $StatusEvery) -eq 0) { Write-LiveLine -Phase "dir_tree.json" -Counters ("dirs={0}" -f (Format-Count $id)) -Detail "writing directory map" }
    }
    Clear-LiveLine
    return New-ReportObject -RootPath $RootPath -ReportKind "full_directory_tree" -ReportRoot "." -IncludesFiles:$false -Nodes @($nodes.ToArray()) -Stats $stats -Index $Index -GitMetadata $GitMetadata -EffectiveExcludeDir $EffectiveExcludeDir
}

function Get-SubtreePaths {
    param(
        [hashtable]$Set,
        [string]$RootPath
    )
    $r = Normalize-RepoPath $RootPath
    $prefix = if ($r -eq ".") { "" } else { "$r/" }
    $out = New-Object System.Collections.ArrayList
    foreach ($k in $Set.Keys) {
        $p = [string]$k
        if ($r -eq "." -or $p -eq $r -or $p.StartsWith($prefix)) { [void]$out.Add($p) }
    }
    return @($out.ToArray() | Sort-Object { if ($_ -eq ".") { "" } else { $_ } })
}

function New-FilesReport {
    param(
        [string]$RootPath,
        [hashtable]$Index,
        [string]$ReportRoot,
        [string]$ReportKind,
        [object]$GitMetadata,
        [string[]]$EffectiveExcludeDir
    )
    $stats = New-Stats
    $id = 0
    $nodes = New-Object System.Collections.ArrayList
    $dirs = Get-SubtreePaths -Set $Index["dirs"] -RootPath $ReportRoot
    foreach ($d in $dirs) {
        [void]$nodes.Add((New-NodeRecord -RootPath $RootPath -RepoPath $d -Type "directory" -Id ([ref]$id) -Stats $stats))
        if (($id % $StatusEvery) -eq 0) { Write-LiveLine -Phase $ReportKind -Counters ("nodes={0} dirs={1} files={2}" -f (Format-Count $id), (Format-Count $stats["directories"]), (Format-Count $stats["files"])) -Detail (Limit-TextMiddle $ReportRoot 40) }
    }
    $files = Get-SubtreePaths -Set $Index["files"] -RootPath $ReportRoot
    foreach ($f in $files) {
        [void]$nodes.Add((New-NodeRecord -RootPath $RootPath -RepoPath $f -Type "file" -Id ([ref]$id) -Stats $stats))
        if (($id % $StatusEvery) -eq 0) { Write-LiveLine -Phase $ReportKind -Counters ("nodes={0} dirs={1} files={2}" -f (Format-Count $id), (Format-Count $stats["directories"]), (Format-Count $stats["files"])) -Detail (Limit-TextMiddle $f 50) }
    }
    Clear-LiveLine
    return New-ReportObject -RootPath $RootPath -ReportKind $ReportKind -ReportRoot $ReportRoot -IncludesFiles:$true -Nodes @($nodes.ToArray()) -Stats $stats -Index $Index -GitMetadata $GitMetadata -EffectiveExcludeDir $EffectiveExcludeDir
}

function New-RootFilesReport {
    param(
        [string]$RootPath,
        [hashtable]$Index,
        [object]$GitMetadata,
        [string[]]$EffectiveExcludeDir
    )
    $stats = New-Stats
    $id = 0
    $nodes = New-Object System.Collections.ArrayList
    [void]$nodes.Add((New-NodeRecord -RootPath $RootPath -RepoPath "." -Type "directory" -Id ([ref]$id) -Stats $stats))
    $files = @($Index["root_files"].Keys | Sort-Object)
    foreach ($f in $files) {
        [void]$nodes.Add((New-NodeRecord -RootPath $RootPath -RepoPath $f -Type "file" -Id ([ref]$id) -Stats $stats))
    }
    return New-ReportObject -RootPath $RootPath -ReportKind "root_level_files" -ReportRoot "." -IncludesFiles:$true -Nodes @($nodes.ToArray()) -Stats $stats -Index $Index -GitMetadata $GitMetadata -EffectiveExcludeDir $EffectiveExcludeDir
}

function Write-JsonFile {
    param(
        [string]$FilePath,
        [object]$Object
    )
    $json = $Object | ConvertTo-Json -Depth 100
    $json = $json -replace "`r`n", "`n"
    $utf8 = New-Object System.Text.UTF8Encoding -ArgumentList $false
    [System.IO.File]::WriteAllText($FilePath, $json + "`n", $utf8)
}

function Write-TextFile {
    param([string]$FilePath, [string]$Text)
    $utf8 = New-Object System.Text.UTF8Encoding -ArgumentList $false
    [System.IO.File]::WriteAllText($FilePath, $Text, $utf8)
}

function New-AsciiOrBoxTreeText {
    param([hashtable]$Index)
    $children = @{}
    foreach ($d in $Index["dirs"].Keys) {
        $p = [string]$d
        if ($p -eq ".") { continue }
        $parent = Get-ParentRepoPath $p
        Add-ChildSet -Map $children -Parent $parent -Child $p
    }
    if ($AsciiTree) {
        $tee = "+-- "; $last = "`-- "; $bar = "|   "; $space = "    "
    }
    else {
        $tee = ([string][char]0x251C) + ([string][char]0x2500) + ([string][char]0x2500) + " "
        $last = ([string][char]0x2514) + ([string][char]0x2500) + ([string][char]0x2500) + " "
        $bar = ([string][char]0x2502) + "   "
        $space = "    "
    }
    $lines = New-Object System.Collections.ArrayList
    [void]$lines.Add("# Repository directory tree")
    [void]$lines.Add("# Generated UTC: " + (Get-Date).ToUniversalTime().ToString("o"))
    [void]$lines.Add("# Contains: directories only. Machine-readable equivalent: dir_tree.json")
    [void]$lines.Add("")
    [void]$lines.Add(".")

    function Add-TreeChildrenLocal {
        param([string]$Parent, [string]$Prefix)
        if (-not $children.ContainsKey($Parent)) { return }
        $kids = @($children[$Parent].Keys | Sort-Object)
        for ($i = 0; $i -lt $kids.Count; $i++) {
            $child = [string]$kids[$i]
            $isLast = ($i -eq ($kids.Count - 1))
            $conn = if ($isLast) { $last } else { $tee }
            $next = if ($isLast) { $Prefix + $space } else { $Prefix + $bar }
            [void]$lines.Add($Prefix + $conn + (Get-RepoName $child) + "/")
            Add-TreeChildrenLocal -Parent $child -Prefix $next
        }
    }
    Add-TreeChildrenLocal -Parent "." -Prefix ""
    return ([string]::Join("`n", ([string[]]$lines.ToArray())) + "`n")
}

# -----------------------------
# Zip / manifest
# -----------------------------

function Find-7Zip {
    $names = @("7z", "7za", "7zr")
    foreach ($n in $names) {
        $cmd = Get-Command $n -ErrorAction SilentlyContinue
        if ($null -ne $cmd) {
            if ($cmd.Path) { return $cmd.Path }
            if ($cmd.Source) { return $cmd.Source }
        }
    }
    $candidates = New-Object System.Collections.ArrayList
    if (-not [string]::IsNullOrWhiteSpace($env:ProgramFiles)) {
        [void]$candidates.Add((Join-Path $env:ProgramFiles "7-Zip\7z.exe"))
    }
    $pf86 = [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
    if (-not [string]::IsNullOrWhiteSpace($pf86)) {
        [void]$candidates.Add((Join-Path $pf86 "7-Zip\7z.exe"))
    }
    foreach ($c in @($candidates.ToArray())) { if (-not [string]::IsNullOrWhiteSpace($c) -and (Test-Path -LiteralPath $c)) { return $c } }
    return $null
}

function New-ZipWith7Zip {
    param([string]$OutputDir, [string[]]$Files, [string]$ZipPath)
    $seven = Find-7Zip
    if ([string]::IsNullOrWhiteSpace($seven)) { return $false }
    if (Test-Path -LiteralPath $ZipPath) { Remove-Item -LiteralPath $ZipPath -Force }
    $outFile = Join-Path $OutputDir "dirfiles_7z_stdout.tmp"
    $errFile = Join-Path $OutputDir "dirfiles_7z_stderr.tmp"
    $leafs = @()
    foreach ($f in $Files) { $leafs += (Split-Path -Leaf $f) }
    $args = @("a", "-tzip", "-mm=Deflate", "-mx=9", "-mfb=258", "-mpass=15", "-bd", "-y", (Split-Path -Leaf $ZipPath)) + $leafs
    Write-EventLine -Level "STEP" -Message "Compressing reports with 7-Zip Deflate."
    $code = Start-ProcessWithSpinner -FilePath $seven -ArgumentList $args -WorkingDirectory $OutputDir -StdOutPath $outFile -StdErrPath $errFile -Activity "7z compress"
    try { if (Test-Path -LiteralPath $outFile) { Remove-Item -LiteralPath $outFile -Force } } catch { }
    try { if (Test-Path -LiteralPath $errFile) { Remove-Item -LiteralPath $errFile -Force } } catch { }
    if ($code -eq 0 -and (Test-Path -LiteralPath $ZipPath)) { return $true }
    Add-WarningMessage "7-Zip failed or produced no zip; falling back to .NET ZIP."
    return $false
}

function New-ZipWithDotNet {
    param([string]$OutputDir, [string[]]$Files, [string]$ZipPath)
    Write-EventLine -Level "STEP" -Message "Compressing reports with .NET ZIP."
    Add-Type -AssemblyName System.IO.Compression.FileSystem | Out-Null
    $stage = Join-Path $OutputDir "dirfiles_zipstage"
    if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
    New-Item -ItemType Directory -Path $stage -Force | Out-Null
    foreach ($f in $Files) {
        Copy-Item -LiteralPath $f -Destination (Join-Path $stage (Split-Path -Leaf $f)) -Force
    }
    if (Test-Path -LiteralPath $ZipPath) { Remove-Item -LiteralPath $ZipPath -Force }
    [System.IO.Compression.ZipFile]::CreateFromDirectory($stage, $ZipPath, [System.IO.Compression.CompressionLevel]::Optimal, $false)
    Remove-Item -LiteralPath $stage -Recurse -Force
}

function New-FileRecord {
    param([string]$Path, [string]$Kind, [bool]$Kept)
    $item = Get-Item -LiteralPath $Path
    $hash = Get-FileHash -LiteralPath $Path -Algorithm SHA256
    return [ordered]@{
        file = (Split-Path -Leaf $Path)
        kind = $Kind
        size_bytes = [int64]$item.Length
        size_human = Format-ByteSize ([int64]$item.Length)
        sha256 = $hash.Hash.ToLowerInvariant()
        kept_uncompressed = [bool]$Kept
    }
}

function Write-Manifest {
    param(
        [string]$ManifestPath,
        [string]$RootPath,
        [string]$OutputDir,
        [hashtable]$Index,
        [object]$GitMetadata,
        [array]$Records,
        [object]$ZipRecord,
        [int]$Removed,
        [string[]]$EffectiveExcludeDir
    )
    $elapsed = (Get-Date) - $script:StartTime
    $obj = [ordered]@{
        _readme = [ordered]@{
            note = "Strict JSON manifest for this repo-dirfiles run."
            upload_hint = "Upload dir_tree.json plus dirfiles.zip for GPT/codebase analysis. dir_tree.txt is for human inspection."
        }
        _meta = [ordered]@{
            schema = "repo-dirfiles-manifest-v16"
            generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
            target_root_name = (Split-Path -Leaf $RootPath)
            output_dir_name = (Split-Path -Leaf $OutputDir)
            source_mode = $Index["source_mode"]
            lean_mode = (-not $NoLean)
            effective_excluded_directory_names = $EffectiveExcludeDir
            git = $GitMetadata
            warnings_total = $script:WarningCount
            elapsed_seconds = [Math]::Round($elapsed.TotalSeconds, 3)
            elapsed_human = ("{0:hh\:mm\:ss}" -f $elapsed)
        }
        results = [ordered]@{
            index = [ordered]@{
                raw_count = $Index["raw_count"]
                files = $Index["files"].Count
                directories = $Index["dirs"].Count
                excluded = $Index["excluded_count"]
                missing = $Index["missing_count"]
            }
            report_files = $Records
            zip_file = $ZipRecord
            temporary_reports_removed = $Removed
            warnings = @($script:Warnings.ToArray())
        }
    }
    if ($IncludeAbsolutePaths) {
        $obj["_meta"]["target_root_absolute"] = $RootPath
        $obj["_meta"]["output_dir_absolute"] = $OutputDir
    }
    Write-JsonFile -FilePath $ManifestPath -Object $obj
}

function Test-ShouldPause {
    if ($PauseMode -eq "Always") { return $true }
    if ($PauseMode -eq "Never") { return $false }
    try {
        $proc = Get-WmiObject Win32_Process -Filter "ProcessId=$PID" -ErrorAction Stop
        if ($null -eq $proc) { return $true }
        $parent = Get-Process -Id ([int]$proc.ParentProcessId) -ErrorAction SilentlyContinue
        if ($null -eq $parent) { return $true }
        return ($parent.ProcessName -ieq "explorer")
    }
    catch { return $true }
}

# -----------------------------
# Main
# -----------------------------

try {
    Write-EventLine -Level "STEP" -Message "V18 startup: bracketed readable UI enabled."

    $target = Resolve-TargetRoot -InputPath $Path
    $rootItem = Get-Item -LiteralPath $target.Path -ErrorAction Stop
    if (-not (Test-IsDirectoryItem $rootItem)) { throw "Target path is not a directory: $($target.Path)" }
    $rootPath = $rootItem.FullName
    $scriptDir = if ([string]::IsNullOrWhiteSpace($PSScriptRoot)) { (Get-Location).ProviderPath } else { $PSScriptRoot }
    $outputDir = Join-Path $rootPath $TmpFolderName
    if (-not (Test-Path -LiteralPath $outputDir)) { New-Item -ItemType Directory -Path $outputDir -Force | Out-Null }

    $script:RunLogPath = Join-Path $outputDir $RunLogFileName
    $utf8 = New-Object System.Text.UTF8Encoding -ArgumentList $false
    [System.IO.File]::WriteAllText($script:RunLogPath, "repo-dirfiles v18 run log`n", $utf8)

    $effectiveExcludeDir = @()
    if (-not $NoLean) { $effectiveExcludeDir += $DefaultLeanExcludes }
    if ($IncludeGit) { $effectiveExcludeDir = @($effectiveExcludeDir | Where-Object { $_ -ine ".git" }) }
    foreach ($e in $ExcludeDir) { if (-not [string]::IsNullOrWhiteSpace($e)) { $effectiveExcludeDir += $e } }
    $effectiveExcludeDir = @($effectiveExcludeDir | Sort-Object -Unique)

    $gitRoot = Get-GitRoot $rootPath
    $gitMetadata = Get-GitMetadata $rootPath
    $useGit = (-not $Filesystem) -and (-not [string]::IsNullOrWhiteSpace($gitRoot)) -and ($null -ne (Get-GitCommandPath))

    Write-KeyValueLine -Key "Target root" -Value $rootPath
    Write-KeyValueLine -Key "Output dir" -Value $outputDir
    Write-KeyValueLine -Key "Script dir" -Value $scriptDir
    $sourceModeText = "filesystem fallback"
    if ($useGit) { $sourceModeText = "git_tracked auto" }
    Write-KeyValueLine -Key "Source mode" -Value $sourceModeText
    Write-KeyValueLine -Key "UI theme" -Value ("theme=" + $Theme + "; labels=fixed-width bracketed; ansi_truecolor=" + $script:UseAnsi + "; session_black=" + (-not $NoConsoleTheme))
    Write-KeyValueLine -Key "Excludes" -Value ("{0} directory names; see manifest" -f $effectiveExcludeDir.Count)

    $stale = @("files_root.json", "files_*.json", "*.part", "dirfiles_zipstage")
    $removedStale = 0
    foreach ($pat in $stale) {
        foreach ($x in @(Get-ChildItem -LiteralPath $outputDir -Force -Filter $pat -ErrorAction SilentlyContinue)) {
            try { Remove-Item -LiteralPath $x.FullName -Recurse -Force; $removedStale++ } catch { }
        }
    }
    if ($removedStale -gt 0) { Write-EventLine -Level "INFO" -Message ("Removed stale generated files: " + $removedStale) }

    $index = $null
    if ($useGit) {
        $index = Build-GitIndex -RootPath $rootPath -ExcludedNames $effectiveExcludeDir
        if ($null -eq $index) {
            if ($StrictGit -or $TrackedOnly) {
                Add-WarningMessage "Git tracked scan failed; falling back would violate -StrictGit/-TrackedOnly."
                if ($StrictGit) { throw "Git tracked scan failed." }
            }
            Add-WarningMessage "Git tracked scan failed; falling back to lean filesystem scan."
            $index = Build-FilesystemIndex -RootPath $rootPath -ExcludedNames $effectiveExcludeDir
        }
    }
    else {
        $index = Build-FilesystemIndex -RootPath $rootPath -ExcludedNames $effectiveExcludeDir
    }

    $reportsForZip = New-Object System.Collections.ArrayList
    $temporaryReports = New-Object System.Collections.ArrayList
    $records = New-Object System.Collections.ArrayList

    Write-EventLine -Level "STEP" -Message "Generating dir_tree.json."
    $dirTreeJsonPath = Join-Path $outputDir $DirTreeJsonFileName
    $dirTree = New-DirectoryTreeReport -RootPath $rootPath -Index $index -GitMetadata $gitMetadata -EffectiveExcludeDir $effectiveExcludeDir
    Write-JsonFile -FilePath $dirTreeJsonPath -Object $dirTree
    [void]$reportsForZip.Add($dirTreeJsonPath)
    [void]$records.Add((New-FileRecord -Path $dirTreeJsonPath -Kind "kept_directory_tree_json" -Kept $true))
    Write-EventLine -Level "PASS" -Message ("Wrote dir_tree.json | dirs={0}" -f (Format-Count $dirTree.stats.directories))

    Write-EventLine -Level "STEP" -Message "Generating dir_tree.txt."
    $dirTreeTextPath = Join-Path $outputDir $DirTreeTextFileName
    Write-TextFile -FilePath $dirTreeTextPath -Text (New-AsciiOrBoxTreeText -Index $index)
    [void]$reportsForZip.Add($dirTreeTextPath)
    [void]$records.Add((New-FileRecord -Path $dirTreeTextPath -Kind "kept_directory_tree_text" -Kept $true))
    Write-EventLine -Level "PASS" -Message "Wrote dir_tree.txt."

    Write-EventLine -Level "STEP" -Message "Generating root-level files report."
    $rootReportPath = Join-Path $outputDir $RootFilesFileName
    $rootReport = New-RootFilesReport -RootPath $rootPath -Index $index -GitMetadata $gitMetadata -EffectiveExcludeDir $effectiveExcludeDir
    Write-JsonFile -FilePath $rootReportPath -Object $rootReport
    [void]$reportsForZip.Add($rootReportPath)
    [void]$temporaryReports.Add($rootReportPath)
    [void]$records.Add((New-FileRecord -Path $rootReportPath -Kind "temporary_all_files_json" -Kept $KeepJsonReports))
    Write-EventLine -Level "PASS" -Message ("Wrote files_root.json | files={0} missing={1}" -f (Format-Count $rootReport.stats.files), (Format-Count $rootReport.stats.missing))

    $firstDirs = @($index["first_dirs"].Keys | Sort-Object)
    $totalReports = $firstDirs.Count
    $i = 0
    foreach ($fd in $firstDirs) {
        $i++
        $safe = (Get-RepoName $fd) -replace '[^A-Za-z0-9._-]+', '_'
        if ([string]::IsNullOrWhiteSpace($safe)) { $safe = "unnamed" }
        $name = "files_$safe.json"
        $pathOut = Join-Path $outputDir $name
        Write-EventLine -Level "STEP" -Message ("Generating [$i/$totalReports] $name")
        $rep = New-FilesReport -RootPath $rootPath -Index $index -ReportRoot $fd -ReportKind "first_level_directory_tree_with_files" -GitMetadata $gitMetadata -EffectiveExcludeDir $effectiveExcludeDir
        Write-JsonFile -FilePath $pathOut -Object $rep
        [void]$reportsForZip.Add($pathOut)
        [void]$temporaryReports.Add($pathOut)
        [void]$records.Add((New-FileRecord -Path $pathOut -Kind "temporary_first_level_json" -Kept $KeepJsonReports))
        Write-EventLine -Level "PASS" -Message ("Wrote {0} | dirs={1} files={2} missing={3}" -f $name, (Format-Count $rep.stats.directories), (Format-Count $rep.stats.files), (Format-Count $rep.stats.missing))
    }

    $zipRecord = $null
    $zipPath = Join-Path $outputDir $ZipFileName
    if (-not $NoZip) {
        $zipped = $false
        if (-not $No7Zip) { $zipped = New-ZipWith7Zip -OutputDir $outputDir -Files @($reportsForZip.ToArray()) -ZipPath $zipPath }
        if (-not $zipped) { New-ZipWithDotNet -OutputDir $outputDir -Files @($reportsForZip.ToArray()) -ZipPath $zipPath }
        $zipRecord = New-FileRecord -Path $zipPath -Kind "zip_archive" -Kept $true
        Write-EventLine -Level "PASS" -Message ("Wrote dirfiles.zip | size=" + $zipRecord.size_human)
    }
    else {
        Write-EventLine -Level "WARN" -Message "Skipping zip because -NoZip was supplied."
    }

    $removedTemp = 0
    if ((-not $KeepJsonReports) -and (-not $NoZip)) {
        foreach ($f in @($temporaryReports.ToArray())) {
            try { if (Test-Path -LiteralPath $f) { Remove-Item -LiteralPath $f -Force; $removedTemp++ } } catch { }
        }
        Write-EventLine -Level "INFO" -Message ("Removed temporary JSON reports: " + $removedTemp)
    }
    elseif ($KeepJsonReports) {
        Write-EventLine -Level "INFO" -Message "Keeping temporary JSON reports because -KeepJsonReports was supplied."
    }

    $manifestPath = Join-Path $outputDir $ManifestFileName
    Write-Manifest -ManifestPath $manifestPath -RootPath $rootPath -OutputDir $outputDir -Index $index -GitMetadata $gitMetadata -Records @($records.ToArray()) -ZipRecord $zipRecord -Removed $removedTemp -EffectiveExcludeDir $effectiveExcludeDir
    $manifestRecord = New-FileRecord -Path $manifestPath -Kind "kept_manifest_json" -Kept $true
    Write-EventLine -Level "PASS" -Message ("Wrote dirfiles_manifest.json | size=" + $manifestRecord.size_human)

    $elapsed = (Get-Date) - $script:StartTime
    Write-EventLine -Level "PASS" -Message ("DONE | files={0} dirs={1} warnings={2} elapsed={3}" -f (Format-Count $index["files"].Count), (Format-Count $index["dirs"].Count), $script:WarningCount, ("{0:hh\:mm\:ss}" -f $elapsed))
    Write-EventLine -Level "INFO" -Message ("Output: " + $outputDir)
}
catch {
    $script:ExitCode = 1
    Clear-LiveLine
    $message = $_.Exception.Message
    Write-EventLine -Level "ERROR" -Message ("FAILED: " + $message)
    Write-RunLog -Level "ERROR" -Message ("FAILED: " + $message)
    Write-RunLog -Level "ERROR" -Message ($_.ScriptStackTrace)
    if ($Trace -and $StatusMode -ne "Quiet") {
        Write-EventLine -Level "NOTE" -Message "Trace mode is enabled; stack trace follows."
        Write-TextRole -Text ($_.ScriptStackTrace) -Role "INFO"
    }
    else {
        Write-EventLine -Level "NOTE" -Message "Stack trace was written to tmp/dirfiles_run.log."
    }
}
finally {
    Clear-LiveLine
    try {
        if ($script:UseAnsi) {
            [Console]::Write((Get-AnsiForRole "INFO"))
        }
        else {
            [Console]::ForegroundColor = [ConsoleColor]::White
        }
    } catch { }
    if (Test-ShouldPause) {
        Write-TextRole -Text "Press Enter to close..." -Role "INFO"
        [void](Read-Host)
    }
}

exit $script:ExitCode
