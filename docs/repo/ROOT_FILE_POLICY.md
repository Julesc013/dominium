Status: PROVISIONAL
Phase: CONVERGE-08
Supersedes: none
Superseded By: none
Stability: provisional

# Root File Policy

The repository root is a coordination surface, not a general source directory. Root-level sprawl hides ownership, weakens mechanical validation, and causes future agents to bind work to convenient paths instead of canonical owners.

`contracts/repo/root_allowlist.toml` is the machine-readable allowlist for root-level entries. `contracts/repo/layout.contract.toml` remains the broader source-layout convergence authority.

CONVERGE-03 recorded root files, metadata directories, generated roots, and transitional directories in `tools/migration/root_inventory.json` and `tools/migration/root_move_map.json`. CONVERGE-05 updated those artifacts after the archive-family move. CONVERGE-06 updated them after schema root convergence. CONVERGE-07 updated them after runtime/AppShell convergence. CONVERGE-08 updated them after product entrypoint convergence. Those files are planning evidence only and do not authorize unrelated moves.

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

Root-level `schema/` and `schemas/` are retired after CONVERGE-06. New schemas, schema projections, validation schemas, and registry schemas belong under `contracts/schemas/` or another explicit `contracts/` class directory.

Do not add a new root-level `compat/`, `registry/`, or `registries/` authority. Existing `compat/` remains a review root because it contains implementation and shim code. Future compatibility law belongs under `contracts/compatibility/` after file-level split. Future registry contracts belong under `contracts/registries/`.

Lock artifacts and lock contracts must not be confused. `contracts/locks/` is for deterministic lockfile schemas and contract definitions. Concrete lock artifacts belong to install/runtime projections such as `store/locks/`; process and IPC locks belong under `runtime/locks/`; setup/update/rollback state belongs under `ops/transactions/`.

Generated schema outputs require explicit generated-output policy before they are committed or treated as source authority.

Root-level `app/`, `appshell/`, `ui/`, and `diag/` are retired after CONVERGE-07. New runtime-facing AppShell, app-runtime, UI, diagnostic, platform, render, input, audio, network, storage, IPC, logging, supervisor, CLI/TUI, or mode-selection source must live under `runtime/<subroot>/`.

Do not add new root-level `platform/`, `render/`, `input/`, `audio/`, `network/`, `storage/`, or `diagnostics/` roots. Existing `net/`, `control/`, and `core/` remain review roots because they are mixed; do not add new authority there.

Generated runtime output belongs in install/runtime projection roots, not in source repo root and not in source `runtime/`.

Root-level `client/`, `server/`, `setup/`, and `launcher/` are retired after CONVERGE-08. New product entrypoint source must live under `apps/<product>/`. Developer tools remain under `tools/`; shipped product tools require explicit classification before using `apps/tools/`.

Root-level domain folders moved in CONVERGE-09 are retired aliases. Do not add new top-level folders such as `geo/`, `chem/`, `worldgen/`, `materials/`, `field/`, `fields/`, `process/`, `signals/`, `mobility/`, or similar domain roots. Use `game/domains/`, `contracts/`, `content/domain-data/`, `docs/domains/`, and `tests/` according to file ownership.

If a temporary root-level domain redirect is ever required, it must contain only a minimal non-authoritative README or shim, be recorded in the move map, and identify the target ownership locations. CONVERGE-09 retained no root-level domain compatibility redirects.

## Generated Roots

Generated roots are evidence or output, not source ownership. `build/`, `out/`, `dist/`, and `artifacts/` must not become canonical source roots merely because tooling emits them.

POST-CONVERGE-01 removed ignored, untracked `.xstack_cache/`, `build/`, and `out/` generated/cache roots. `artifacts/` and `dist/` remain active review exceptions because they contain tracked provenance or distribution-projection files.

## Archive-Family Roots

Do not create new root-level archive-family directories. Use the canonical archive classes instead:

- `archive/historical/`
- `archive/legacy/`
- `archive/quarantine/`
- `archive/superseded/`
- `archive/generated/`

Root-level `attic/`, `legacy/`, and `quarantine/` were retired in CONVERGE-05. If a future tool needs to quarantine material, it must place it under `archive/quarantine/` or a later explicit quarantine contract.

## `dist/`

`dist/` is a distribution/build projection unless a stronger release contract explicitly says otherwise. It is not the source repo layout and must not define source ownership.

## `build/` And `out/`

`build/` and `out/` are generated build outputs. They should remain ignored local output and absent from the source checkout unless a future reviewed task explicitly requires tracked provenance elsewhere.

## `repo/`

The existing root-level `repo/` must be classified and migrated later by ownership. Do not add new authority there. Future material should prefer `contracts/repo/`, `docs/repo/`, or `tools/migration/` depending on whether it is machine-readable contract, human documentation, or migration tooling.

In CONVERGE-03, `repo/` remains transitional and review-sensitive. It is not a destination for new source-layout authority.

## Distribution Projection Roots

Source root policy does not authorize runtime, install, media, package cache, staging, save-store, or package export roots at the repository root.

Distribution projections are governed by `contracts/distribution/layout.contract.toml`. `dist/` is generated release/build output unless an explicit stronger exception says otherwise. Package caches, staging directories, runtime stores, media payloads, save stores, and rollback transaction roots are projections, not source repository ownership roots.

## Version And Project Policy Files

`VERSION_*` files are allowed root identity files. README, license, security, contributing, governance, and agent instruction files may remain at root when they represent repository-wide coordination.

## Validator Policy

Both root validators are audit-only by default:

- `python tools/validators/check_repo_layout.py --repo-root .`
- `python tools/validators/check_root_allowlist.py --repo-root .`

Strict modes are explicit and may fail until convergence removes or classifies transitional roots:

- `python tools/validators/check_repo_layout.py --repo-root . --strict`
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`

## CONVERGE-10 Enforcement Note

After CONVERGE-10, root files and root directories not covered by `contracts/repo/layout.contract.toml`, `contracts/repo/root_allowlist.toml`, or `contracts/repo/layout_exceptions.toml` fail strict validation.

Generated roots require explicit generated policy or an active exception. After POST-CONVERGE-01, only `dist/` and `artifacts/` remain active generated or generated-adjacent exceptions; `.xstack_cache/`, `build/`, and `out/` are retired generated/cache exceptions and must not regrow as source authority.

After POST-CONVERGE-02, the root package marker `__init__.py` and root `labs/` directory are retired. The three `tool_ui_*.cmd` files remain explicit compatibility shims for documented developer workflow and must continue to resolve canonical tools through `scripts/dev/tool_shim.py`.

After POST-CONVERGE-03, content/package/profile/bundle review did not retire additional roots. `data/`, `packs/`, `profiles/`, `bundles/`, `modding/`, `models/`, and `templates/` remain explicit active exceptions because each is mixed, identity-sensitive, implementation-backed, or protected-reference-backed. New authored content should use `content/` ownership roots instead of adding new root-level content directories.

After POST-CONVERGE-04, high-risk contract/security/update review did not retire additional roots. `compat/`, `lib/`, `libs/`, `locks/`, `repo/`, `safety/`, `security/`, `specs/`, and `updates/` remain explicit active exceptions because they are implementation-backed, build/ABI-sensitive, identity-sensitive, generated-feed-backed, or protected semantics surfaces. New pure contracts should use `contracts/`, release/update recipes should use reviewed `release/` ownership, and no new root-level compatibility, security, safety, spec, lock, repo, or update authority should be added.

After POST-CONVERGE-05, `core/`, `control/`, and `net/` remain explicit active protected review exceptions. New deterministic substrate should normally land under `engine/` when universal or `game/domains/` when domain-specific; new control or network contracts should land under `contracts/`; new runtime adapters should land under reviewed runtime ownership; new human explanation should land under `docs/`. Do not add new root-level core/control/net authority.

No broad wildcard exceptions are allowed without a reviewed task. Add one exception per root, file, or tightly scoped pattern, and include a reason, target or review target, risk, and retirement phase.

`VERSION_*` files remain allowed root identity files through the root allowlist pattern and explicit known file list. New non-version root files require allowlist review or an exception.

## CONVERGE-12 Final Cross-Links

Final audit: `docs/repo/audits/CONVERGE_12_FINAL_AUDIT.md`.

Post-converge work plan: `docs/repo/POST_CONVERGE_NEXT_STEPS.md`.

New root files or directories after CONVERGE-12 must be added through the layout contracts, root allowlist, component/distribution contracts where relevant, or a specific temporary exception.
