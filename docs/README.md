# Documentation Index

This directory contains the authoritative design specs and policy documents for
Domino (engine) and Dominium (product layer).

## Start Here
- Project landing page: `../README.md`
- Directory/layout contract (authoritative): `docs/DIRECTORY_CONTEXT.md`
- Architecture and layering: `docs/ARCHITECTURE.md` (see also `docs/OVERVIEW_ARCHITECTURE.md`)
- Component roles and outputs: `docs/COMPONENTS.md`
- API contract conventions: `docs/CONTRACTS.md`
- Dependency boundaries: `docs/DEPENDENCIES.md`

## Policy / Standards
- Language/toolchain constraints: `docs/LANGUAGE_POLICY.md`
- Coding/commenting style: `docs/STYLE.md`
- Determinism rules + regressions: `docs/SPEC_DETERMINISM.md`, `docs/DETERMINISM_REGRESSION_RULES.md`

## Build / Release
- Build topology overview: `docs/BUILD_OVERVIEW.md`
- Building and tests: `docs/BUILDING.md`
- Supported build matrix: `docs/BUILD_MATRIX.md`
- Dist layout and outputs: `docs/BUILD_DIST.md`, `docs/build_output.md`
- Release notes process: `docs/RELEASE_NOTES_PROCESS.md`
- Core data build pipeline: `docs/COREDATA_BUILD.md`

## Specs (Subsystem Design)
Specs are named `docs/SPEC_*.md` and are the canonical home for subsystem
invariants, layering, extension recipes, and (when applicable) determinism and
versioning rules.

Recommended entry points:
- Determinism + SIM: `docs/SPEC_DETERMINISM.md`, `docs/SPEC_SIM_SCHEDULER.md`, `docs/SPEC_ACTIONS.md`
- Placement/structure: `docs/SPEC_POSE_AND_ANCHORS.md`, `docs/SPEC_TRANS_STRUCT_DECOR.md`
- Products: `docs/SPEC_PRODUCTS.md`, `docs/SPEC_GAME_PRODUCT.md`, `docs/SPEC_LAUNCHER.md`,
  `docs/SPEC_SETUP_CORE.md`, `docs/SPEC_SETUP_CLI.md`
- Universe model + spacetime: `docs/SPEC_UNIVERSE_MODEL.md`, `docs/SPEC_SPACETIME.md`,
  `docs/SPEC_REFERENCE_FRAMES.md`, `docs/SPEC_ORBITS_TIMEWARP.md`, `docs/SPEC_CALENDARS.md`
- Universe portability + migrations: `docs/SPEC_UNIVERSE_BUNDLE.md`, `docs/SPEC_MIGRATIONS.md`
- Core data packs + authoring: `docs/SPEC_CORE_DATA.md`, `docs/SPEC_COSMO_CORE_DATA.md`,
  `docs/SPEC_MECHANICS_PROFILES.md`, `docs/SPEC_CORE_DATA_PIPELINE.md`
- Renderer conformance: `docs/SPEC_DGFX_IR_VERSIONING.md`, `docs/SPEC_BACKEND_CONFORMANCE.md`
- Epistemic UI: `docs/SPEC_EPISTEMIC_INTERFACE.md`, `docs/SPEC_UI_CAPABILITIES.md`,
  `docs/SPEC_UI_WIDGETS.md`, `docs/SPEC_UI_PROJECTIONS.md`
- Economy and ledgers: `docs/SPEC_LEDGER.md`, `docs/SPEC_ASSETS_INSTRUMENTS.md`,
  `docs/SPEC_CONTRACTS.md`, `docs/SPEC_MARKETS.md`, `docs/SPEC_MONEY_STANDARDS.md`
