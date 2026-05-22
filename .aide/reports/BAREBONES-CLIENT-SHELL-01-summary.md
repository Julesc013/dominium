# BAREBONES-CLIENT-SHELL-01 Summary

Status: PASS_WITH_WARNINGS
Date: 2026-05-22

## Summary

Added a narrow no-content client survival-floor proof. The client now exposes barebones `--diag` and `--verify` CLI paths beside existing help/version/status behavior, and the command/result/refusal/capability contracts record that CLI/headless status is available while gameplay, rendered UI, package runtime, provider runtime, module loading, and world/save runtime remain unavailable.

## Changed Surfaces

- `apps/client/main_client.c`
- `contracts/command/client_barebones_input.schema.json`
- `contracts/result/client_barebones_result.schema.json`
- `contracts/command/command_surface.contract.toml`
- `contracts/capability/capability.registry.json`
- `contracts/diagnostics/diagnostic_code.registry.json`
- `contracts/refusal/refusal_code.registry.json`
- `contracts/public_surface/public_surface.contract.toml`
- `tests/app/client_barebones_shell_tests.py`
- `tests/contract/app/fixtures/valid_client_barebones_descriptor.json`
- `tests/contract/client/fixtures/*`
- `docs/architecture/barebones_client_shell.md`
- `docs/development/barebones_client_shell.md`
- `docs/repo/audits/BAREBONES_CLIENT_SHELL_01.md`

## Command IDs

- `dominium.client.status.v1`
- `dominium.client.diag.v1`
- `dominium.client.verify.v1`

## Known Warnings

- Full CTest remains `NOT_RUN_T4_DEBT`.
- Dependency-direction strict remains PASS with 68 known warnings and 0 violations.
- AIDE validate retains known review-reference warnings.
- RepoX reports the known stale AuditX output warning.
- Client gameplay, rendered UI, package runtime, provider runtime, module loader, world/save runtime, and release support remain unavailable.

## Validation

- `py -3 tests/app/client_barebones_shell_tests.py`
- Contract validators for app descriptors, command surface, diagnostics, capability/refusal, artifact identity, provider model, module descriptors, Workbench workspaces, composition, replay proof, package mount, public surface, component matrix, portability matrix, and dependency direction
- General scripts for docs sanity, build target boundaries, UI shell purity, and ABI boundaries
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/BAREBONES-CLIENT-SHELL-01-fast-strict.json --md-out .aide/reports/BAREBONES-CLIENT-SHELL-01-fast-strict.md`

## Non-Goals Preserved

No playable client, renderer, rendered GUI, native GUI, package runtime, provider runtime, runtime module loader, world/save runtime, release publication, or broad AppShell implementation was added.

## Next

`PRODUCT-SPINE-REVIEW-01`
