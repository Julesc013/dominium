Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# MODULE-COMPOSITION-LAW-01 Audit

Result: PASS_WITH_WARNINGS, pending final commit and post-commit checks.

## Why

Dominium needs modules, Workbench workspaces, and app compositions to be
declared by stable contracts instead of inferred from folders, UI wiring, or
executable names. This prevents `module` from becoming a junk-drawer term and
keeps Workbench from becoming product authority.

## Added

- `contracts/module/**`
- `contracts/workbench/**`
- `contracts/app/**`
- `tools/validators/contracts/check_module_descriptors.py`
- `tools/validators/contracts/check_workbench_workspaces.py`
- `tools/validators/contracts/check_app_descriptors.py`
- `tests/contract/module/**`
- `tests/contract/workbench/**`
- `tests/contract/app/**`
- `docs/architecture/module_composition_law.md`
- `docs/architecture/workbench_workspace_model.md`
- `docs/architecture/app_composition_model.md`
- `docs/development/module_development_guidelines.md`
- `docs/development/workbench_module_guidelines.md`

## Registry Changes

- module kinds registered: 12
- public surface registry updated with module, Workbench, app, validator, and fixture surfaces
- diagnostics registry updated with 8 provisional module/workspace/app codes
- capability registry updated with 4 provisional module/workspace/app capabilities

## Inventory

The initial descriptive inventory scanned 17,896 tracked files per validator:

- Module inventory classified 1,208 candidates.
- Workbench inventory classified 194 candidates.
- App inventory classified 882 candidates.

Current app, Workbench, runtime, pack, and tool files are not migrated by this
task.

## Proof

- Module descriptor validator strict mode passes.
- Workbench workspace validator strict mode passes.
- App descriptor validator strict mode passes.
- Fixture modes pass: 6 module fixtures, 5 Workbench fixtures, and 4 app fixtures.
- Diagnostics, capability/refusal, provider, command-surface, public-surface,
  schema/protocol, artifact, and ABI checks pass.
- Dependency-direction validator still reports known existing debt.
- Fast strict passes: 32/32 commands in 315.25 seconds.

## Known Limitations

- Module/workspace/app law is provisional.
- Runtime module loader is not implemented.
- Workbench UI and App Composer are not implemented.
- Pack-provided module activation and trust runtime are not implemented.
- Existing dependency-direction debt remains visible.
- Full CTest is not run; it remains T4 full/release proof.

Next task: `REPLACEMENT-PROTOCOL-01`.
