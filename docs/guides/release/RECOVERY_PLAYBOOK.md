Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Recovery Playbook (Setup + Launcher)

Doc Version: 1

This playbook lists deterministic recovery actions with exact commands. All commands are safe, offline, and do not install the launcher.

## 1) Verify installed state

```
dominium-setup verify --state <install_root>/.dsu/installed_state.dsustate --format json
```

If verification fails, proceed to repair.

## 2) Repair in place

```
dominium-setup export-invocation --manifest <manifest> --state <install_root>/.dsu/installed_state.dsustate --op repair --out repair.dsuinv
dominium-setup plan --manifest <manifest> --state <install_root>/.dsu/installed_state.dsustate --invocation repair.dsuinv --out repair.dsuplan
dominium-setup apply --plan repair.dsuplan
```

Notes:
- The manifest must match the installed product/version.
- The repair plan is deterministic in `--deterministic 1` mode.

## 3) Rollback from a journal

Use rollback after a failed/partial apply when a journal exists:

```
dominium-setup rollback --journal <journal_path> --dry-run
dominium-setup rollback --journal <journal_path>
```

`--dry-run` verifies intent without mutating files.

## 4) Uninstall preview

```
dominium-setup uninstall-preview --state <install_root>/.dsu/installed_state.dsustate --format json
```

Use this to confirm which owned files will be removed and which user data will be preserved.

## 5) Reinstall without data loss

1) Preview uninstall to confirm user data preservation:

```
dominium-setup uninstall-preview --state <install_root>/.dsu/installed_state.dsustate --format json
```

2) Uninstall owned files (user data preserved by policy):

```
dominium-setup uninstall --state <install_root>/.dsu/installed_state.dsustate
```

3) Reinstall from the same manifest:

```
dominium-setup export-invocation --manifest <manifest> --op install --scope <user|system|portable> --out reinstall.dsuinv
dominium-setup plan --manifest <manifest> --invocation reinstall.dsuinv --out reinstall.dsuplan
dominium-setup apply --plan reinstall.dsuplan
```

## 6) Forensic report bundle

```
dominium-setup report --state <install_root>/.dsu/installed_state.dsustate --out report --format json
```

The report bundle includes deterministic inventory, verify, and uninstall previews for support or audit.

## 7) Launcher recovery (installed-state missing/corrupt)

When the launcher refuses to run due to invalid state:

```
dominium-setup verify --state <install_root>/.dsu/installed_state.dsustate --format json
dominium-setup export-invocation --manifest <manifest> --state <install_root>/.dsu/installed_state.dsustate --op repair --out repair.dsuinv
dominium-setup plan --manifest <manifest> --state <install_root>/.dsu/installed_state.dsustate --invocation repair.dsuinv --out repair.dsuplan
dominium-setup apply --plan repair.dsuplan
```

If state cannot be repaired, reinstall using the steps above.