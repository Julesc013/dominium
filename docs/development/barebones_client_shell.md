Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional
Task: BAREBONES-CLIENT-SHELL-01

# Barebones Client Shell Slice

`BAREBONES-CLIENT-SHELL-01` adds a narrow no-content proof for the client product. It is a recovery and diagnostic floor, not a playable client.

## Surfaces

- Command registry entries: `dominium.client.status.v1`, `dominium.client.diag.v1`, `dominium.client.verify.v1`
- Input schema: `contracts/command/client_barebones_input.schema.json`
- Result schema: `contracts/result/client_barebones_result.schema.json`
- App descriptor fixture: `tests/contract/app/fixtures/valid_client_barebones_descriptor.json`
- Result fixtures: `tests/contract/client/fixtures/`
- Entrypoint support: `apps/client/main_client.c` exposes `--diag` and `--verify` beside existing help/version/status paths

## Validation

Run the focused proof with:

```text
py -3 tests/apps/client_barebones_shell_tests.py
```

Then run the related contract validators:

```text
python tools/validators/contracts/check_app_descriptors.py --repo-root . --strict
python tools/validators/contracts/check_command_surface.py --repo-root . --strict
python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict
python tools/validators/contracts/check_capability_refusal.py --repo-root . --strict
```

Fast strict remains the broader product-spine gate when touched inputs require it.

## Boundaries

This slice must not be used as evidence that the client is playable, rendered, package-backed, provider-backed, module-loaded, release-supported, or world/save capable. Those surfaces remain unavailable and must continue to emit typed refusals until separate reviewed tasks implement them.
