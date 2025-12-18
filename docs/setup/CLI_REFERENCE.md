# Dominium Setup CLI Reference (v1)

`dominium-setup` is a contract-stable, scriptable control plane over **Setup Core**.
It does not implement install logic; it validates inputs, calls core APIs, and emits deterministic outputs.

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

- Commands that support JSON output emit a single JSON object on `stdout` using the envelope described in `docs/setup/CLI_JSON_SCHEMAS.md`.
- Paths in JSON outputs are normalized to `/` separators.
- All numeric values are integers (no floats).

## Command surface (locked as v1)

### `dominium-setup version`

Emits the CLI version and schema version.

### `dominium-setup help` / `dominium-setup help <command>`

Deterministic, plain-text help.

### `dominium-setup manifest validate --in <file>`

Validates a manifest file and reports its content digests.

### `dominium-setup manifest dump --in <file> [--out <file>] [--format json]`

Dumps a manifest to canonical JSON. If `--out` is omitted, the manifest JSON is embedded in the JSON envelope.

### `dominium-setup resolve --manifest <file> [--state <file>] --op <install|upgrade|repair|uninstall> [--components <csv>] [--exclude <csv>] [--scope <user|system|portable>]`

Validates the manifest/state, resolves requested components into a canonical resolved set, and emits a preview (components + actions).

Selector semantics:

- `--components`: Install exactly these components plus dependencies (no default selection).
- `--exclude`: Remove components from the selection; if this breaks dependencies, the command fails.

Scope semantics:

- `--scope` is required for `install`/`upgrade` unless the manifest permits exactly one scope.
- For `repair`/`uninstall`, scope is inferred from state when possible.

### `dominium-setup plan --manifest <file> [--state <file>] --op <install|upgrade|repair|uninstall> [--components <csv>] [--exclude <csv>] [--scope <user|system|portable>] --out <planfile>`

Calls core APIs in-order: validate manifest → load state (optional) → resolve → plan → write plan file.

The plan file embeds:

- manifest digest
- resolved-set digest
- operation
- scope
- plan format version

### `dominium-setup apply --plan <planfile> [--dry-run]`

Applies a plan file. The CLI never infers a manifest/state for apply; it uses the plan file only.

When applying, Setup Core validates the plan file (header, version, checksum, internal coherence).

### `dominium-setup verify --state <file> [--format json|txt]`

Verifies filesystem integrity against the installed state.

- Exit code `0`: verified OK
- Exit code `2`: verification issues (missing/modified/extra/errors)

### `dominium-setup list --state <file> [--format json|txt]`

Lists installed components from the installed state.

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

### `dominium-setup rollback --journal <file> [--dry-run]`

Replays a transaction journal rollback. Intended for recovery after a failed/partial apply.

### `dominium-setup export-log --log <file> --out <file> --format json|txt`

Exports a `.dsulog` file to:

- JSON (`--format json`): stable schema (see `docs/setup/AUDIT_LOG_FORMAT.md`)
- Text (`--format txt`): deterministic TSV

