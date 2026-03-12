Status: DRAFT
Last Reviewed: 2026-03-12
Scope: ARCH-AUDIT-0 retro audit
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`

# ARCH-AUDIT-0 Retro Audit

## Purpose
Establish the existing governance surfaces that already protect architectural purity, then add a single deterministic audit layer that can report on them consistently before release.

## Existing RepoX Checks
- Renderer/truth isolation already exists through RepoX render-boundary checks and representation invariants.
- Determinism governance already exists through no-wallclock, named-RNG, replay, smoke, stress, cross-platform, META-STABILITY, and TIME-ANCHOR invariants.
- Release governance already depends on proof anchors, pack locks, contract pins, and deterministic replay surfaces.

## Existing AuditX Checks
- Renderer truth leak analyzers already exist, notably `E50_RENDERER_TRUTH_LEAK_SMELL`.
- Wall-clock analyzers already exist in multiple families, including `E229`, `E402`, `E404`, `E425`, `E427`, and `E431`.
- META-STABILITY analyzers already exist through `E449`, `E450`, and `E451`.
- TIME-ANCHOR mixed-width enforcement already exists through `E452`.
- Several domain-specific nondeterminism analyzers already cover overlay merge, worldgen RNG, bundle ordering, and replay drift.

## Existing Proof And Replay Checks
- MVP smoke and stress gates already pin proof anchors, negotiation records, pack locks, replay bundle hashes, and derived view fingerprints.
- Cross-platform and TIME-ANCHOR gates already verify anchor hash agreement, contract pins, compaction boundaries, and replay equivalence.
- GEO/EARTH replay tooling already verifies overlay merge, sky, illumination, water, tide, climate, and related derived-view artifacts.

## Danger Zones
- Moon phase shortcuts: any shortcut that stores lunar presentation state in Truth instead of deriving it from canonical astronomy inputs.
- Sky state stored: any Truth schema or canonical record that stores sky gradients, star rows, or other sky-view payloads.
- Water visuals stored: any canonical state that stores water render colors, foam, reflections, or renderer-facing water state.
- Shadow state stored: any canonical state that stores shadow buffers, shadow maps, or renderer-only lighting intermediates.
- Duplicated negotiation logic: multiple authoritative implementations of the same compatibility negotiation semantics.
- Duplicated overlay merge logic: multiple authoritative implementations of overlay merge conflict resolution or effective object synthesis.

## Safest Insertion Point
- Add a deterministic tool-level audit under `tools/audit/`.
- Reuse the same scan primitives from RepoX and new AuditX analyzers so the constitution, report, smells, and release invariant all read from one source of meaning.
- Keep the scan static and offline; runtime code must not depend on the audit tool.

## Initial Stable Expectations
- Stable semantics are already pinned through semantic contract bundles, CAP-NEG compatibility records, overlay merge contract docs, META-STABILITY stable entries, and TIME-ANCHOR doctrine.
- ARCH-AUDIT-0 should treat presentation-in-truth leaks and missing contract/stability pins as blocking.
- Reviewed approximation or ordering advisories may be recorded as explicit known exceptions for ARCH-AUDIT-1 if they are already visible and deterministic.
