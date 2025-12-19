# Security Model (Setup Core)

Setup Core is a deterministic, offline-first install engine. It assumes local, trusted binaries but treats **inputs** (manifest, plan, state) as untrusted and validates them strictly.

## Trust boundaries

- **Trusted**: `dominium-setup` binary + adapters shipped with the build.
- **Untrusted**: manifest files, plan files, installed-state files, audit logs, and user-provided paths.

## Enforcement points

- Manifest load: validates TLV schema, IDs, required fields (`docs/setup/MANIFEST_SCHEMA.md`).
- Plan load: validates header/version/checksum and internal coherence.
- State load: validates install roots, component/file paths, and digest fields.
- Transaction engine: rejects absolute paths and path traversal; verifies staged file hashes before commit.
- Verify/uninstall: never follows symlinks out of declared install roots.

## Prohibitions (locked)

- No network calls during install/verify/uninstall/rollback.
- No execution of payload code during install (pure file operations).
- No writes outside the selected install roots or transaction root.
- No implicit elevation: adapters must explicitly request elevation.

## CLI commands (exact)

- Validate manifest:
  - `dominium-setup manifest validate --in <path-to.dsumanifest> --format json --deterministic 1`
- Validate plan:
  - `dominium-setup apply --plan <planfile> --dry-run --deterministic 1`
- Verify integrity:
  - `dominium-setup verify --state <install_root>/.dsu/installed_state.dsustate --format json --deterministic 1`

Exit codes follow `docs/setup/CLI_REFERENCE.md`.

## See also

- `docs/setup/MANIFEST_SCHEMA.md`
- `docs/setup/INSTALLED_STATE_SCHEMA.md`
- `docs/setup/TRANSACTION_ENGINE.md`
