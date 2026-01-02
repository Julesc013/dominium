# Dominium Setup CLI Reference (v1)

This document applies to the legacy CLI binary `dominium-setup-legacy`.
All references to `dominium-setup` below refer to `dominium-setup-legacy`.

`dominium-setup` is a contract-stable, scriptable control plane over **Setup Core**.
It does not implement install logic; it validates inputs, builds `dsu_invocation` payloads,
calls core APIs, and emits deterministic outputs. The CLI is the reference frontend.

## Global flags (all commands)

- `--deterministic <0|1>`: Default `1`. In deterministic mode, ordering is canonical and timestamps are forced to `0`.
- `--quiet`: Suppresses non-essential human text (JSON output is not suppressed).
- `--json`: Shorthand for `--format json` where a command supports `--format`.

## Exit codes (stable)

- `0`: Success
- `1`: Operation failed (fatal)
- `2`: Verification / integrity issues detected (command executed)
- `3`: Invalid input (args/manifest/state/plan)
- `4`: Unsupported operation (platform/build limitations)
- `5`: Partial success (reserved; avoid)

## Output

- Commands that support JSON output emit a single JSON object on `stdout` using the envelope described in `docs/setup_legacy/CLI_JSON_SCHEMAS.md`.
- Paths in JSON outputs are normalized to `/` separators.
- All numeric values are integers (no floats).
- JSON outputs include `invocation_digest64` when an invocation payload is involved.

## File locations (stable defaults)

- Installed state: `<install_root>/.dsu/installed_state.dsustate`
- Audit log (CLI default): `audit.dsu.log` in the current working directory
- Transaction journal (default): `<install_root>.txn/<journal_id_hex>/.dsu_txn/journal/txn.dsujournal`

## Command surface (locked as v1)

### `dominium-setup version`

Emits the CLI version and schema version.

### `dominium-setup help` / `dominium-setup help <command>`

Deterministic, plain-text help.

### `dominium-setup manifest validate --in <file>`

Validates a manifest file and reports its content digests.

### `dominium-setup manifest dump --in <file> [--out <file>] [--format json]`

Dumps a manifest to canonical JSON. If `--out` is omitted, the manifest JSON is embedded in the JSON envelope.

### `dominium-setup export-invocation --manifest <file> --op <install|upgrade|repair|uninstall> [--state <file>] [--components <csv>] [--exclude <csv>] [--scope <user|system|portable>] [--platform <triple>] [--install-root <path>] [--ui-mode <gui|tui|cli>] [--frontend-id <id>] [--offline] [--allow-prerelease] [--legacy] --out <file>`

Builds a `dsu_invocation` payload from CLI flags and writes the TLV file.
If `--format json` is provided, the canonical JSON form is also emitted.
`--ui-mode` and `--frontend-id` default to `cli` when omitted.

### `dominium-setup resolve --manifest <file> [--state <file>] --invocation <file>`

Validates the manifest/state, resolves requested components into a canonical resolved set, and emits a preview (components + actions).
The invocation payload is required; CLI flags are only used by `export-invocation`.

Selector semantics (invocation construction):

- `--components`: Install exactly these components plus dependencies (no default selection).
- `--exclude`: Remove components from the selection; if this breaks dependencies, the command fails.

Scope semantics (invocation construction):

- `--scope` is required for `install`/`upgrade` unless the manifest permits exactly one scope.
- For `repair`/`uninstall`, scope is inferred from state when possible.

### `dominium-setup plan --manifest <file> [--state <file>] --invocation <file> --out <planfile>`

Calls core APIs in-order: validate manifest → load state (optional) → resolve → plan → write plan file.
The invocation payload is required and recorded in the plan digest.

The plan file embeds:

- manifest digest
- resolved-set digest
- operation
- scope
- invocation digest
- plan format version

### `dominium-setup apply --plan <planfile> [--dry-run]`

Applies a plan file. The CLI never infers a manifest/state for apply; it uses the plan file only.

When applying, Setup Core validates the plan file (header, version, checksum, internal coherence).

### `dominium-setup apply-invocation --manifest <file> [--state <file>] --invocation <file> --out <planfile> [--dry-run]`

Convenience flow: resolve + plan + apply using a single invocation payload.
Equivalent to `plan` followed by `apply` with the same invocation.

### `dominium-setup verify --state <file> [--format json|txt]`

Verifies filesystem integrity against the installed state.

- Exit code `0`: verified OK
- Exit code `2`: verification issues (missing/modified/extra/errors)

### `dominium-setup list-installed --state <file> [--format json|txt]`

Lists installed components from the installed state.
Alias: `dominium-setup list --state <file> [--format json|txt]`.

### `dominium-setup report --state <file> --out <dir> [--format json|txt]`

Writes a deterministic report bundle to `--out`:

- `inventory.<ext>`
- `touched_paths.<ext>`
- `uninstall_preview.<ext>`
- `verify.<ext>`
- `corruption_assessment.<ext>`

Exit code is `2` when `verify` detects integrity issues.

### `dominium-setup uninstall-preview --state <file> [--components <csv>] [--format json|txt]`

Previews uninstall effects (owned files, preserved user files) for all components or the specified subset.

### `dominium-setup platform-register --state <file>`

Invokes platform adapter registrations using intents stored in the installed state.
JSON output is a minimal object (see `docs/setup_legacy/CLI_JSON_SCHEMAS.md`).

### `dominium-setup platform-unregister --state <file>`

Invokes platform adapter unregistration using intents stored in the installed state.
JSON output is a minimal object (see `docs/setup_legacy/CLI_JSON_SCHEMAS.md`).

### `dominium-setup rollback --journal <file> [--dry-run]`

Replays a transaction journal rollback. Intended for recovery after a failed/partial apply.

### `dominium-setup export-log --log <file> --out <file> --format json|txt`

Exports a `.dsulog` file to:

- JSON (`--format json`): stable schema (see `docs/setup_legacy/AUDIT_LOG_FORMAT.md`)
- Text (`--format txt`): deterministic TSV

## Adapter/internal commands (not listed in help)

These commands are used by platform adapters and test harnesses. JSON output uses minimal objects (no envelope).

### `dominium-setup dry-run --plan <planfile> --log <file>`

Executes a plan in dry-run mode and writes an audit log to `--log` without mutating files.

### `dominium-setup install --plan <planfile> [--log <file>] [--dry-run]`

Applies a plan file and writes an audit log (`--log`, default `audit.dsu.log`). Uses the transaction engine; `--dry-run` simulates the apply.

### `dominium-setup uninstall --state <file> [--log <file>] [--dry-run]`

Uninstalls using the installed state file and writes an audit log (`--log`, default `audit.dsu.log`). Uses the transaction engine; `--dry-run` simulates the uninstall.

## See also

- `docs/setup_legacy/CLI_JSON_SCHEMAS.md`
- `docs/setup_legacy/AUDIT_LOG_FORMAT.md`
