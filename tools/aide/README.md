# AIDE Tooling Helpers

`tools/aide/` contains AIDE adapters, inventory tools, and migration helpers.
These helpers do not own Dominium product or runtime behavior.

The default posture is non-destructive:

- no moves
- no deletes
- no renames
- no unknown tool execution
- no network or provider calls
- no writes unless an explicit `--out` path is supplied

Existing XStack/AuditX/RepoX/TestX-style tools are wrapped before they are
renamed or retired. Bad long-term names are not a reason to delete useful
validation evidence.

## Wrapper Commands

AIDE-STRUCTURE-02 adds a small wrapper runner for registered AIDE command
contracts:

```powershell
python tools/aide/run_task.py --repo-root . list
python tools/aide/run_task.py --repo-root . describe aide.tools
python tools/aide/run_task.py --repo-root . run aide.tools --dry-run
python tools/aide/run_task.py --repo-root . run aide.tools
```

The runner loads `.aide/tools/command-registry.toml` and the referenced
contract files under `.aide/tools/command-contracts/`. Dry-run mode prints the
underlying command without execution. Normal run mode refuses unknown commands,
commands without `execution_allowed = true`, commands that look mutating when
`apply_allowed = false`, and commands that look network-related when
`network_allowed = false`.

Wrapper commands preserve old tools behind stable AIDE names. They do not move,
rename, delete, or weaken legacy validators.

## Root Recycling Tools

The root recycling helpers are no-apply evidence tools:

- `inventory_root.py` walks one root and records file/directory metadata.
- `classify_files.py` assigns conservative fates and sensitivity flags.
- `scan_references.py` audits raw root path references without rewriting.
- `check_no_raw_root_references.py` reports raw references and only fails in
  strict audit mode.
- `scan_identity_markers.py`, `scan_authority_markers.py`,
  `scan_semantic_markers.py`, and `scan_abi_build_markers.py` record marker
  evidence for sensitive root families.
- `generate_salvage_map.py` creates draft/not-approved/no-apply salvage maps.
- `check_salvage_map.py` validates salvage maps without applying them.
- `reconcile_root_inventories.py` reconciles inventory waves.
- `select_move_wave.py` ranks draft move-planning candidates.

These tools never move, delete, rename, rewrite, approve, or apply files.
