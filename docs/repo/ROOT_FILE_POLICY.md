Status: PROVISIONAL
Phase: CONVERGE-03
Supersedes: none
Superseded By: none
Stability: provisional

# Root File Policy

The repository root is a coordination surface, not a general source directory. Root-level sprawl hides ownership, weakens mechanical validation, and causes future agents to bind work to convenient paths instead of canonical owners.

`contracts/repo/root_allowlist.toml` is the machine-readable allowlist for root-level entries. `contracts/repo/layout.contract.toml` remains the broader source-layout convergence authority.

CONVERGE-03 records root files, metadata directories, generated roots, and transitional directories in `tools/migration/root_inventory.json` and `tools/migration/root_move_map.json`. Those files are planning evidence only and do not authorize moves.

## Allowed Metadata Directories

Allowed metadata/config roots are declared in `contracts/repo/root_allowlist.toml` and include:

- `.github/`
- `.vscode/`
- `.aide/`
- `.codex/`
- `.aide.local.example/`

Other dot roots require explicit contract classification.

Metadata directories are included in the root inventory with `classification = "metadata"` and `migration_action = "retain_metadata"`.

## Allowed Root Files

Allowed root files are declared in the allowlist contract and include governance, project, build, license, security, contribution, README, and version identity files:

- `AGENTS.md`
- `CLAUDE.md`
- `CMakeLists.txt`
- `CMakePresets.json`
- `CONTRIBUTING.md`
- `DOMINIUM.md`
- `GOVERNANCE.md`
- `LICENSE`
- `LICENSE.md`
- `MODDING.md`
- `README.md`
- `SECURITY.md`
- `VERSION_CLIENT`
- `VERSION_ENGINE`
- `VERSION_GAME`
- `VERSION_LAUNCHER`
- `VERSION_SERVER`
- `VERSION_SETUP`
- `VERSION_SUITE`
- `VERSION_TOOLS`
- `VERSION_*`

The contract may also allow specific existing project files such as changelogs or tool metadata. Additional `VERSION_*` files should be reviewed and added deliberately.

Allowed root files are included in the root inventory with `classification = "allowed_file"` and `migration_action = "retain_file"`. Root-level files that are not allowed by contract are classified as review items rather than silently promoted.

## Forbidden New Root Patterns

Do not add new root-level product, domain, schema, runtime-adapter, or generated-output folders. New work should bind to the existing contract targets:

- product entrypoints under `apps/`
- domain implementation under `game/domains/`
- schemas and registries under `contracts/`
- runtime adapters under `runtime/`
- generated output only under explicitly governed output roots

## Generated Roots

Generated roots are evidence or output, not source ownership. `build/`, `out/`, `dist/`, and `artifacts/` must not become canonical source roots merely because tooling emits them.

The move map records generated roots with generated/output handling and review notes. It does not delete them.

## `dist/`

`dist/` is a distribution/build projection unless a stronger release contract explicitly says otherwise. It is not the source repo layout and must not define source ownership.

## `build/` And `out/`

`build/` and `out/` are generated build outputs. They should not be relied on for canonical source, schema, contract, or product ownership.

## `repo/`

The existing root-level `repo/` must be classified and migrated later by ownership. Do not add new authority there. Future material should prefer `contracts/repo/`, `docs/repo/`, or `tools/migration/` depending on whether it is machine-readable contract, human documentation, or migration tooling.

In CONVERGE-03, `repo/` remains transitional and review-sensitive. It is not a destination for new source-layout authority.

## Version And Project Policy Files

`VERSION_*` files are allowed root identity files. README, license, security, contributing, governance, and agent instruction files may remain at root when they represent repository-wide coordination.

## Validator Policy

Both root validators are audit-only by default:

- `python tools/validators/check_repo_layout.py --repo-root .`
- `python tools/validators/check_root_allowlist.py --repo-root .`

Strict modes are explicit and may fail until convergence removes or classifies transitional roots:

- `python tools/validators/check_repo_layout.py --repo-root . --strict`
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`
