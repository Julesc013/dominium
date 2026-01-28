# Documentation Index

This repository splits canonical architecture, schemas, and guides across
distinct directories. Start with `docs/architecture/` before diving into guides.

## Start here (required)
- Project landing: `README.md`
- Canon identity: `docs/architecture/WHAT_THIS_IS.md`
- Non-goals: `docs/architecture/WHAT_THIS_IS_NOT.md`
- Canonical system map: `docs/architecture/CANONICAL_SYSTEM_MAP.md`
- Hard invariants: `docs/architecture/INVARIANTS.md`
- Constitution + change protocol: `docs/architecture/ARCH0_CONSTITUTION.md`,
  `docs/architecture/CHANGE_PROTOCOL.md`
- Layout contract: `docs/architecture/DIRECTORY_CONTEXT.md`
- Architecture layers: `docs/architecture/ARCHITECTURE.md`,
  `docs/architecture/ARCHITECTURE_LAYERS.md`
- Component roles: `docs/architecture/COMPONENTS.md`
- Dependency boundaries: `docs/guides/DEPENDENCIES.md`

## Policy / Standards
- Determinism canon: `docs/specs/SPEC_DETERMINISM.md`
- Execution law: `docs/architecture/EXECUTION_MODEL.md`
- Law gates: `docs/architecture/LAW_ENFORCEMENT_POINTS.md`
- Authority canon: `docs/architecture/AUTHORITY_MODEL.md`
- Style guide: `docs/guides/STYLE.md`
- Build enforcement: `docs/architecture/ARCH_BUILD_ENFORCEMENT.md`

## Build / Release
- Build overview: `docs/guides/BUILD_OVERVIEW.md`
- Building and tests: `docs/guides/BUILDING.md`
- Build matrix: `docs/ci/BUILD_MATRIX.md`
- Dist layout: `docs/guides/BUILD_DIST.md`, `docs/guides/build_output.md`
- Release process: `docs/guides/RELEASE_NOTES_PROCESS.md`,
  `docs/guides/release/RELEASE_READINESS_CHECKLIST.md`

## Application / Platform / Render
- App runtime docs: `docs/app/README.md`
- Platform runtime docs: `docs/platform/README.md`
- Renderer docs: `docs/render/README.md`

## Specs and schemas
- Spec index: `docs/specs/SPEC_INDEX.md`
- Execution, existence, domain, travel, time, authority: `schema/*/README.md`
- Core contracts: `docs/specs/CONTRACTS.md`

## Deprecated paths (moved)
The following legacy paths appear in older notes but are no longer canonical:
- Deprecated: `docs/architecture/DIRECTORY_CONTEXT.md` -> `docs/architecture/DIRECTORY_CONTEXT.md`
- Deprecated: `docs/architecture/ARCHITECTURE.md` -> `docs/architecture/ARCHITECTURE.md`
- Deprecated: `docs/guides/DEPENDENCIES.md` -> `docs/guides/DEPENDENCIES.md`
- Deprecated: `docs/specs/CONTRACTS.md` -> `docs/specs/CONTRACTS.md`
- Deprecated: `docs/SPEC_*.md` -> `docs/specs/SPEC_*.md`

These moves reflect the split between architecture (`docs/architecture/`), guides
(`docs/guides/`), specs (`docs/specs/`), and schemas (`schema/`).
