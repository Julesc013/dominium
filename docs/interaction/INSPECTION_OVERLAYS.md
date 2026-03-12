Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Inspection Overlays

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Model
- Inspection overlays are derived artifacts.
- Snapshot generation is cache-backed and keyed by truth hash anchor + policy context.
- Overlays are emitted into RenderModel `overlay`/`ui` layers only.

## Overlay Types
- Selection/highlight outlines.
- Glyph labels (policy-gated; debug/lab profiles can show IDs).
- Deterministic numeric panels when entitlement/policy permits.

## Caching
- Reuse inspection snapshots when `(target_id, truth_hash_anchor, policy_id)` matches.
- Invalidate on truth-hash change or deterministic eviction policy.
- No continuous recomputation loop while inspecting.

## Degradation
- If inspection budget is insufficient:
  - return macro summary overlay only (counts/bands)
  - preserve deterministic refusal/summary behavior
- Do not introduce lag spikes in place of deterministic degradation.

## Epistemics
- Overlays are bounded by existing perceived channels and epistemic policy.
- No hidden truth fields may be surfaced by overlay generation.
