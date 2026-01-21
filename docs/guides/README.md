# Documentation Index

This repository splits canonical architecture, schemas, and guides across
distinct directories. Start with `docs/arch/` before diving into guides.

## Start here (required)
- Project landing: `README.md`
- Canon identity: `docs/arch/WHAT_THIS_IS.md`
- Non-goals: `docs/arch/WHAT_THIS_IS_NOT.md`
- Canonical system map: `docs/arch/CANONICAL_SYSTEM_MAP.md`
- Hard invariants: `docs/arch/INVARIANTS.md`
- Constitution + change protocol: `docs/arch/ARCH0_CONSTITUTION.md`,
  `docs/arch/CHANGE_PROTOCOL.md`
- Layout contract: `docs/arch/DIRECTORY_CONTEXT.md`
- Architecture layers: `docs/arch/ARCHITECTURE.md`,
  `docs/arch/ARCHITECTURE_LAYERS.md`
- Component roles: `docs/arch/COMPONENTS.md`
- Dependency boundaries: `docs/guides/DEPENDENCIES.md`

## Policy / Standards
- Determinism canon: `docs/specs/SPEC_DETERMINISM.md`
- Execution law: `docs/arch/EXECUTION_MODEL.md`
- Law gates: `docs/arch/LAW_ENFORCEMENT_POINTS.md`
- Authority canon: `docs/arch/AUTHORITY_MODEL.md`
- Style guide: `docs/guides/STYLE.md`
- Build enforcement: `docs/arch/ARCH_BUILD_ENFORCEMENT.md`

## Build / Release
- Build overview: `docs/guides/BUILD_OVERVIEW.md`
- Building and tests: `docs/guides/BUILDING.md`
- Build matrix: `docs/ci/BUILD_MATRIX.md`
- Dist layout: `docs/guides/BUILD_DIST.md`, `docs/guides/build_output.md`
- Release process: `docs/guides/RELEASE_NOTES_PROCESS.md`,
  `docs/guides/release/RELEASE_READINESS_CHECKLIST.md`

## Specs and schemas
- Spec index: `docs/specs/SPEC_INDEX.md`
- Execution, existence, domain, travel, time, authority: `schema/*/README.md`
- Core contracts: `docs/specs/CONTRACTS.md`

## Deprecated paths (moved)
The following legacy paths appear in older notes but are no longer canonical:
- Deprecated: `docs/arch/DIRECTORY_CONTEXT.md` -> `docs/arch/DIRECTORY_CONTEXT.md`
- Deprecated: `docs/arch/ARCHITECTURE.md` -> `docs/arch/ARCHITECTURE.md`
- Deprecated: `docs/guides/DEPENDENCIES.md` -> `docs/guides/DEPENDENCIES.md`
- Deprecated: `docs/specs/CONTRACTS.md` -> `docs/specs/CONTRACTS.md`
- Deprecated: `docs/SPEC_*.md` -> `docs/specs/SPEC_*.md`

These moves reflect the split between architecture (`docs/arch/`), guides
(`docs/guides/`), specs (`docs/specs/`), and schemas (`schema/`).
