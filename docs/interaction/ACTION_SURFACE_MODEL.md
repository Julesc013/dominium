Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# ActionSurface Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: Constitutional (ACT-1)
Version: 1.0.0

## Purpose
ActionSurface is the universal interaction primitive for assemblies and parts. It is data-defined metadata that maps perceived semantic surfaces to lawful process intents.

## A) ActionSurface
- An ActionSurface is a semantic interaction point attached to an Assembly semantic row or AG node metadata in PerceivedModel.
- Each surface declares:
  - `surface_type_id`
  - `compatible_tool_tags`
  - `allowed_process_ids`
  - `parameter_schema_id` (optional)
  - `constraints` (optional)
- ActionSurfaces are pack-driven metadata. Runtime must remain valid when no surfaces are declared.

## B) No Hardcoding Rule
- Engine and client interaction code must not special-case world items by literal identity (for example: "bolt", "tree", "door").
- Surface behavior resolves only from registries + surface metadata + law/authority context.

## C) Process-Only Mutation
- ActionSurface interaction never mutates TruthModel directly.
- ActionSurface resolution and affordance generation produce derived metadata and intent envelopes.
- Authoritative mutation happens only through deterministic process execution.

## D) Deterministic IDs
- `surface_id` is deterministic and derived from:
  - `H(parent_semantic_id, local_surface_index)`
- `local_surface_index` is assigned from deterministic surface ordering for the selected parent semantic target.

## E) Epistemic Gating
- Surfaces are filtered by visibility policy, law constraints, lens channels, and authority entitlements.
- Hidden or forbidden surfaces must not leak into Perceived interaction affordances.
- Outside allowed visibility scope, no surface-specific detail is exposed.

## F) Tool Compatibility Stub
- Tool assemblies declare `tool_tags` (for example: `tool_tag.fastening`, `tool_tag.operating`).
- ActionSurface resolution compares held tool tags against `compatible_tool_tags`.
- Incompatible surfaces remain discoverable only as disabled affordances with deterministic reason code `refusal.tool.incompatible`.

## Determinism/Invariant Notes
- Surface lists are ordered deterministically by `surface_id`.
- Affordances derived from surfaces are ordered deterministically by `(surface_id, process_id, affordance_id)`.
- Tool incompatibility is represented as deterministic disabled affordance metadata using refusal reason `refusal.tool.incompatible`.
