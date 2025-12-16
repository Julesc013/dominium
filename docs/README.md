# Documentation Index

This directory contains the authoritative design specs and policy documents for
Domino (engine) and Dominium (product layer).

## Start Here
- Project overview and entry-point spec links: `README.md`
- Directory/layout contract (authoritative): `docs/DIRECTORY_CONTEXT.md`
- Architecture and layering: `docs/ARCHITECTURE.md` (see also `docs/OVERVIEW_ARCHITECTURE.md`)
- API contract conventions: `docs/CONTRACTS.md`

## Policy / Standards
- Language/toolchain constraints: `docs/LANGUAGE_POLICY.md`
- Coding/commenting style: `docs/STYLE.md`
- Determinism rules + regressions: `docs/SPEC_DETERMINISM.md`, `docs/DETERMINISM_REGRESSION_RULES.md`
- Dependency boundaries: `docs/DEPENDENCIES.md`

## Build / Release
- Building and tests: `docs/BUILDING.md`
- Supported build matrix: `docs/BUILD_MATRIX.md`
- Release notes process: `docs/RELEASE_NOTES_PROCESS.md`

## Specs (Subsystem Design)
Specs are named `docs/SPEC_*.md` and are the canonical home for subsystem
invariants, layering, extension recipes, and (when applicable) determinism and
versioning rules.

Recommended entry points:
- Determinism + SIM: `docs/SPEC_DETERMINISM.md`, `docs/SPEC_SIM_SCHEDULER.md`, `docs/SPEC_ACTIONS.md`
- Placement/structure: `docs/SPEC_POSE_AND_ANCHORS.md`, `docs/SPEC_TRANS_STRUCT_DECOR.md`
- Products: `docs/SPEC_PRODUCTS.md`, `docs/SPEC_GAME_PRODUCT.md`, `docs/SPEC_LAUNCHER.md`, `docs/SPEC_SETUP_CORE.md`

