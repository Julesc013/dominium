Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# COMPAT-SEM-3 Retro Audit

## Scope
- Audit current GEO-9 overlay merge conflict behavior.
- Confirm whether current behavior is always deterministic last-wins.
- Identify the lowest-risk profile integration point for conflict policy selection.

## Findings
- Current overlay merge behavior is deterministic and effectively last-wins.
  - `src/geo/overlay/overlay_merge_engine.py` sorts patches by layer ordering plus stable patch fingerprint.
  - Conflicts are not surfaced as first-class derived artifacts today.
- Current merge trust/profile selection already routes through `overlay_policy_id`.
  - `build_default_overlay_manifest(...)` persists `extensions.overlay_policy_id`.
  - `validate_overlay_manifest_trust(...)` resolves and validates that overlay policy from `data/registries/overlay_policy_registry.json`.
- Current conflict handling is implicit.
  - Multiple patches against the same `(object_id, property_path)` are applied in deterministic order.
  - There is no conflict artifact, no strict refusal path, and no prompt-stub remediation surface.
- Current explain tooling has the right insertion point.
  - `tools/geo/tool_explain_property_origin.py` already declares `overlay_conflict_contract_id = "explain.overlay_conflict"`.
  - `explain_property_origin(...)` can be extended to attach conflict notes without changing renderer/UI truth boundaries.

## Integration Direction
- Keep existing `overlay.*` policy IDs as the profile-facing selector.
- Add a separate conflict-policy registry and let each `overlay.*` policy declare its default `overlay_conflict_policy_id`.
- Support explicit override through manifest/session policy surfaces, but preserve `overlay.default -> overlay.conflict.last_wins`.
- Emit deterministic conflict artifacts for audit even when the mode is `last_wins`.
