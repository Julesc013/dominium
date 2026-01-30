# Architecture Changelog (CLEAN1)

Status: evolving.
Scope: architecture-level changes and stabilization summary.

## CLEAN-1 (January 29, 2026)

Summary of newly frozen or reaffirmed surfaces:

- Canonical contract location is `docs/architecture/`.
- Repository intent and directory ownership are documented.
- Schema stability classifications are explicit.
- Performance metrics and proof surfaces are formalized.
- Frozen contracts now have hash guards to prevent accidental drift.

Surfaces that remain intentionally flexible:

- Execution details that do not alter contract semantics.
- Tooling and presentation layers (read-only and UI surfaces).
- Content packs and modding workflows (data-only, extension-preserving).

Pointers to major contract families:

- FAB: `docs/architecture/FABRICATION_MODEL.md`
- SHIP: `docs/distribution/PACK_TAXONOMY.md`
- SCALE: `docs/architecture/SCALING_MODEL.md`
- MMO: `docs/architecture/MMO_COMPATIBILITY.md`

Suggested tag: `arch-stable-1`

## TERRAIN0 (January 30, 2026)

Rationale
- Lock a single canonical terrain/matter truth model before implementation.
- Provide schema anchors and TestX guards for future terrain work.

Invariant Impact
- Reinforces Process-only mutation (PROC0) and deterministic ordering (DET0).
- Adds terrain-specific guardrails for collapse/expand and epistemic safety.

Migration Plan
- None. New schemas and contracts are additive and unused by runtime.

Epoch Bump
- None. No sim-affecting behavior was changed.

CI Update
- Add TestX contract guard for terrain contracts and fixtures.
- Add invariant scan for terrain authority violations.
