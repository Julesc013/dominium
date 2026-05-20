Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# COMMAND-SURFACE-01 Audit

## Status

PASS_WITH_WARNINGS.

## Why

Dominium needs a typed command/result/refusal/evidence spine so CLI, TUI,
headless tools, server/admin surfaces, rendered UI, Workbench, AIDE/Codex, and
tests stop treating private tools or file paths as separate behavior authority.

## Added

- `contracts/command/command_surface.contract.toml`
- `contracts/command/command.schema.json`
- `contracts/command/command_kind.registry.json`
- `contracts/result/result.schema.json`
- `contracts/view/view_surface.contract.toml`
- `contracts/view/view.schema.json`
- `contracts/event/event_surface.contract.toml`
- `contracts/event/event.schema.json`
- `contracts/refusal/refusal_code.registry.json`
- `contracts/refusal/refusal.schema.json`
- `contracts/document/document.schema.json`
- `contracts/evidence/evidence_packet.schema.json`
- `tools/validators/contracts/check_command_surface.py`
- `tests/contract/command_surface/**`
- `docs/architecture/command_view_event_refusal.md`
- `docs/development/command_surface_guidelines.md`

## Initial Registry

Registered 5 provisional commands:

- `dominium.validation.run`
- `dominium.repo.fast_strict.run`
- `dominium.public_surface.validate`
- `dominium.abi.public_headers.validate`
- `dominium.dependency_direction.validate`

Registered 5 provisional command-level refusal codes.

No command is marked stable. No runtime dispatcher, Workbench UI, product
behavior, package runtime, gameplay, renderer, or native GUI behavior was
implemented.

## Proof

- Command validator strict: PASS, 5 commands, 0 findings.
- Command validator fixtures: PASS.
- JSON parse: PASS for 13 created JSON files.
- TOML fallback parse: PASS for 6 TOML files.
- Public surface validator: PASS, 39 surfaces.
- ABI validator: PASS with 2,851 existing warnings.
- Dependency direction validator: FAIL on known existing debt from
  DEPENDENCY-DIRECTION-01; latest staged sample scan checked 16,153 files with
  358 violations and 38 warnings.
- Fast strict: PASS, 32/32 commands, 309.969 seconds.

## Known Warnings

- Command surface law is provisional.
- Runtime dispatch remains future work.
- Workbench integration remains future work.
- Full diagnostic/refusal registries remain later Foundation Lock work.
- Dependency-direction strict debt remains visible and unresolved.
- Full CTest was not run and remains T4 full/release proof.

## Next Task

`DIAGNOSTIC-CODE-REGISTRY-01`.
