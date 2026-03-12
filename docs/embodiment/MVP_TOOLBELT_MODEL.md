Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# MVP Toolbelt Model

This document freezes the EMB-1 MVP toolbelt contract for Dominium v0.0.0.

It is subordinate to:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`
- `docs/embodiment/EMBODIMENT_BASELINE.md`
- `docs/worldgen/REFINEMENT_PIPELINE_MODEL.md`

## Relevant Invariants

- `docs/canon/constitution_v1.md` `A1` Determinism is primary
- `docs/canon/constitution_v1.md` `A2` Process-only mutation
- `docs/canon/constitution_v1.md` `A3` Law-gated authority
- `docs/canon/constitution_v1.md` `A7` Observer-renderer-truth separation
- `docs/canon/constitution_v1.md` `A10` Explicit degradation and refusal
- `docs/canon/constitution_v1.md` `E2` Deterministic ordering
- `docs/canon/constitution_v1.md` `E6` Replay equivalence

## 1. Scope

EMB-1 defines the MVP embodiment toolbelt as capability affordances, not inventory items.

EMB-1 includes:

- terrain edit tool affordances for mine, fill, and bounded cut operations
- scanner tool affordances for derived field, hydrology, and provenance summaries
- logic probe and bounded logic analyzer affordances
- teleport tool integration with the MW-4 refinement pipeline
- CLI, TUI, and rendered-client command exposure

EMB-1 does not include:

- inventory ownership
- crafting
- item transfer
- unlawful authority bypass
- direct truth reads from scanners or UI tools

## 2. Tool Categories

Canonical tool capability rows are:

- `tool.terrain_edit`
- `tool.scanner_basic`
- `tool.logic_probe`
- `tool.logic_analyzer`
- `tool.teleport`

These are capability affordances, not owned items.
Later itemization may bind these affordances to inventory objects without changing EMB-1 command semantics.

## 3. Terrain Edit Tool

Terrain editing exposes three task families:

- `task.mine_at_cursor(volume)`
- `task.fill_at_cursor(volume, material_stub)`
- `task.cut_trench(path_stub)`

Rules:

- target GEO cell keys are derived deterministically from the active selection or provided path stub
- terrain edits call only:
  - `process.geometry_remove`
  - `process.geometry_add`
  - `process.geometry_cut`
- authority, entitlement, and budget checks occur before process planning
- refusal outcomes remain explicit and auditable

Terrain edits are canonical mutation requests.
No UI or tool may mutate terrain state directly.

## 4. Scanner Tool

The scanner emits a derived observation artifact only.

Scanner summaries may include:

- tile key and position reference
- elevation proxy
- material, biome, and ocean/river/lake flags
- hydrology flow target and river flag
- temperature and daylight
- wind vector
- tide height proxy
- pollution concentration when present
- overlay provenance summary when an explain result is supplied

Rules:

- scanner output may only be built from inspection snapshots, field summaries, and explain/provenance artifacts
- scanner precision and availability are profile, entitlement, and access-policy driven
- unknown or unavailable channels degrade explicitly rather than leaking truth

## 5. Logic Probe And Analyzer

The logic probe tool plans a lawful `process.logic_probe`.

The logic analyzer tool plans a bounded trace session through:

- `process.logic_trace_start`
- `process.logic_trace_tick`
- `process.logic_trace_end`

Rules:

- logic access remains epistemic gated
- analyzer sessions must stay bounded in duration
- compute pressure may refuse or shorten derived analyzer sessions explicitly

## 6. Teleport Tool

The teleport tool wraps the MW-4 refinement-aware teleport planner.

Rules:

- teleport requests refinement before movement
- Earth-surface targets may request L3 surface refinement for the destination view extent
- deterministic random-target selection uses the named UI RNG stream already defined for teleport

Teleport continues to mutate position only through lawful movement/camera processes.

## 7. Entitlements And Law

Tool use is granted by `AuthorityContext` and constrained by `LawProfile`.

Canonical EMB-1 entitlements are:

- `ent.tool.terrain_edit`
- `ent.tool.scan`
- `ent.tool.logic_probe`
- `ent.tool.logic_trace`
- `ent.tool.teleport`

Rules:

- capabilities permit attempts, not guaranteed success
- process-level law gates remain authoritative even if a tool surface is visible
- exception-capable profiles must log their use through existing exception and provenance paths

## 8. Diegetic And Admin Variants

EMB-1 stays profile driven.

Examples:

- scanner may be diegetic with coarse precision or limited range
- full provenance or logic trace access may require elevated observer/operator entitlements
- freecam and inspect remain profile gated under EMB-0 and UX-0 rules

No hardcoded runtime mode branch may be introduced for tool behavior.

## 9. Determinism And Replay

Rules:

- tool planning order is deterministic
- scan artifacts are derived and compactable
- terrain edits remain canonical process requests
- logic traces remain bounded and replayable
- teleport plans remain deterministic for identical inputs

EMB-1 must replay equivalently for identical tool sessions and lawful inputs.
