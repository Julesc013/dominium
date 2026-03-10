Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/contracts/SEMANTIC_CONTRACT_MODEL.md`, and GEO-9 overlay merge.

# Overlay Conflict Policies

## Purpose
- Make overlay conflicts explicit, deterministic, and auditable.
- Keep sandbox/default overlay behavior unchanged unless a profile selects stricter conflict handling.
- Prevent silent ambiguous merges in strict/ranked lineages.

## Conflict Definition
- A conflict exists when two or more property patches target the same `(object_id, property_path)` at the same precedence level.
- Same-precedence conflict detection is semantic, not an ordering failure.
- Deterministic tie-break ordering may still exist, but strict policies must not silently rely on it.

## Policy Modes

### `overlay.conflict.last_wins`
- Apply patches by deterministic layer precedence and stable patch ordering.
- Emit conflict artifacts for every detected same-precedence conflict.
- Preserve current GEO-9 merge result semantics.

### `overlay.conflict.refuse`
- Detect conflicts before applying the conflicting merge group.
- Refuse the merge with `refusal.overlay.conflict`.
- Strict mode must refuse merge instead of silently applying deterministic tie-breaks.
- Emit conflict artifacts and remediation hint:
  - `remedy.overlay.resolve_conflict_or_change_policy`

### `overlay.conflict.prompt_stub`
- Engine behavior is refusal-only for v0.0.0.
- Record conflict artifact rows before refusing the merge.
- Engine implementations must record conflict artifact rows deterministically.
- Strict prompt-stub behavior must `record conflict artifact` rows before surfacing remediation.
- Emit `refusal.overlay.conflict` plus remediation hint:
  - `remedy.overlay.add_explicit_resolver_layer`
- No GUI prompt is introduced in this series.

## Deterministic Ordering
- Conflict enumeration order is:
  - `(object_id, property_path, layer_order, patch_hash)`
- `layer_order` is the canonical GEO-9 layer sort key.
- `patch_hash` is the normalized property patch deterministic fingerprint.

## Profile Binding
- Conflict policy is profile-driven.
- Existing overlay profiles declare a default conflict policy through `data/registries/overlay_policy_registry.json`.
- Current v0.0.0 defaults are:
  - `overlay.default -> overlay.conflict.last_wins`
  - `overlay.rank_strict -> overlay.conflict.refuse`
  - `overlay.lab_freeform -> overlay.conflict.last_wins`
- Explicit per-session or per-manifest override is allowed only through declared policy surfaces.

## Explainability
- Conflict artifacts are derived-only and never mutate Truth.
- `tool.geo.explain_property_origin` must surface `explain.overlay_conflict` notes when the requested property participated in a detected conflict.

## Non-Goals
- No GUI prompt implementation in this series.
- No change to pack trust/signature validation rules.
- No nondeterministic merge fallback.
