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
