Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# Overlay Conflict Baseline

## Policy Modes

- `overlay.conflict.last_wins`
  - Default sandbox-compatible policy.
  - Applies deterministic layer precedence and stable patch ordering.
  - Emits `overlay_conflict_artifact` rows for audit and replay proof.
- `overlay.conflict.refuse`
  - Refuses merge with `refusal.overlay.conflict`.
  - Remediation: `remedy.overlay.resolve_conflict_or_change_policy`.
- `overlay.conflict.prompt_stub`
  - Refuses merge with `refusal.overlay.conflict`.
  - Remediation: `remedy.overlay.add_explicit_resolver_layer`.

## Deterministic Conflict Definition

- Conflicts are detected when multiple patches target the same `(object_id, property_path)` at the same `precedence_order`.
- Conflict enumeration is sorted by `(object_id, property_path, layer_order, patch_hash)`.
- Conflict artifacts are derived-only and do not mutate authoritative truth.

## Explain And Proof

- `explain.overlay_conflict` is registered as the explain contract for overlay conflicts.
- `tool_explain_property_origin` now surfaces:
  - `overlay_conflict_policy_id`
  - `overlay_conflict_mode`
  - `overlay_conflict_count`
  - `overlay_conflicts`
  - `conflict_note = explain.overlay_conflict`
- `overlay_proof_surface` and `tool_replay_overlay_merge` now include `overlay_conflict_artifact_hash_chain`.

## Readiness

- Ready for MOD-POLICY-0 trust/capability gating over mod packs.
- Ready for MW-4 and later overlay-heavy packs that need strict refusal instead of silent same-tier resolution.
