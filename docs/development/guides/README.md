Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

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


- Dependency boundaries: `docs/development/guides/DEPENDENCIES.md`





## Policy / Standards


- Determinism canon: `docs/reference/specs/SPEC_DETERMINISM.md`


- Execution law: `docs/architecture/EXECUTION_MODEL.md`


- Law gates: `docs/architecture/LAW_ENFORCEMENT_POINTS.md`


- Authority canon: `docs/architecture/AUTHORITY_MODEL.md`


- Style guide: `docs/development/guides/STYLE.md`


- Build enforcement: `docs/architecture/ARCH_BUILD_ENFORCEMENT.md`





## Build / Release


- Build overview: `docs/development/guides/BUILD_OVERVIEW.md`


- Building and tests: `docs/development/guides/BUILDING.md`


- Build matrix: `docs/testing/ci/BUILD_MATRIX.md`


- Dist layout: `docs/development/guides/BUILD_DIST.md`, `docs/development/guides/build_output.md`


- Release process: `docs/development/guides/RELEASE_NOTES_PROCESS.md`,


  `docs/development/guides/release/RELEASE_READINESS_CHECKLIST.md`





## Application / Platform / Render


- App runtime docs: `docs/apps/README.md`


- Platform runtime docs: `docs/runtime/platform/README.md`


- Renderer docs: `docs/runtime/render/README.md`





## Specs and schemas


- Spec index: `docs/reference/specs/SPEC_INDEX.md`


- Execution, existence, domain, travel, time, authority: `schema/*/README.md`


- Core contracts: `docs/reference/specs/CONTRACTS.md`





## Deprecated paths (moved)


The following legacy paths appear in older notes but are no longer canonical:


- Deprecated: `docs/architecture/DIRECTORY_CONTEXT.md` -> `docs/architecture/DIRECTORY_CONTEXT.md`


- Deprecated: `docs/architecture/ARCHITECTURE.md` -> `docs/architecture/ARCHITECTURE.md`


- Deprecated: `docs/development/guides/DEPENDENCIES.md` -> `docs/development/guides/DEPENDENCIES.md`


- Deprecated: `docs/reference/specs/CONTRACTS.md` -> `docs/reference/specs/CONTRACTS.md`


- Deprecated: `docs/reference/specs/SPEC_*.md` -> `docs/reference/specs/SPEC_*.md`





These moves reflect the split between architecture (`docs/architecture/`), guides


(`docs/development/guides/`), specs (`docs/reference/specs/`), and schemas (`schema/`).
