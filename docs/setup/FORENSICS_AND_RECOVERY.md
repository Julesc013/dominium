# Forensics, Reporting, and Recovery (Plan S-5)

Plan S-5 turns Setup Core into a “truth database + forensic trail” system:

- `installed_state.dsustate` is the **single authoritative record** of what is installed (components + owned files).
- `audit.dsu.log` is a **structured forensic trail** of what happened during operations.

The audit log is never used as authority for “what is installed”; it is only supporting evidence.

## Files and Defaults

Typical locations after install:

- Installed state: `<install_root>/.dsu/installed_state.dsustate`
- Audit log: `audit.dsu.log` (default CLI output in the current working directory; override with `--log`)

## CLI Forensics Commands

All outputs are deterministic (stable ordering) when run with deterministic configuration; JSON output uses stable key ordering.

### List installed components

```text
dominium-setup list-installed --state <path-to-installed_state.dsustate> --format json --deterministic 1
```

Produces a component inventory + install roots + digests.

### Verify integrity

```text
dominium-setup verify --state <path-to-installed_state.dsustate> --json
```

Verification checks:

- existence of owned files
- SHA-256 re-hash and digest comparison
- “extra” files under install roots (does not follow symlinks out of root)

Exit codes:

- `0`: verification OK
- `2`: verification completed but found missing/modified/extra files
- `3`: invalid input/state

### Report bundle (JSON/text)

```text
dominium-setup report --state <path-to-installed_state.dsustate> --out <dir> --format json
```

Writes machine-readable reports to `<dir>` (stable output).

## “What did this installer touch?”

Use `dominium-setup report` or the core API `dsu_report_touched_paths`:

- Owned files: files that will be removed on uninstall by default.
- Owned directories: parent directories implied by owned files (removed if empty and safe).
- User data / cache: recorded ownership categories (preserved by default).

## Uninstall Impact Preview

```text
dominium-setup uninstall-preview --state <path-to-installed_state.dsustate> --json
```

Preview is state-driven and lists only what the installer owns (plus derived empty-dir removals). User data is excluded by default.

You may restrict the preview to specific components:

```text
dominium-setup uninstall-preview --state <path> --components core,data --json
```

## Recovery Guidance

### Verification failures (missing/modified/extra)

- Missing/modified owned files usually indicate partial deletion, corruption, or user edits.
- Extra files indicate drift under the install root (often user-created files, caches, or abandoned artifacts).

Recommended actions:

- Run a repair/upgrade operation using the same resolved set, or reinstall.
- Use `uninstall-preview` to understand what would be removed before attempting a clean uninstall.

### Missing or corrupt installed-state

If `installed_state.dsustate` is missing or fails validation:

- Setup Core cannot safely determine what to remove (state is the authority).
- Use the audit log (if present) for forensic review only (`dsu_log_export_json`), but do not treat it as truth.
- Preferred recovery is reinstall/repair to regenerate a valid state, then uninstall via state.

### Audit log missing or corrupt

- Installs/uninstalls can still be driven purely by installed-state.
- Loss of the log only reduces forensic visibility; it does not change installed-state authority.

## Safety Notes

- State never references paths outside its declared install roots.
- Verification does not follow symlinks out of root.
- Uninstall removes owned files only and removes directories only when empty and safe; user data is preserved by default.

## See also

- `docs/setup/TROUBLESHOOTING.md`
- `docs/setup/JOURNAL_FORMAT.md`
