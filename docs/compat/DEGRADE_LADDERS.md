Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md`, `docs/compat/NEGOTIATION_HANDSHAKES.md`, `schema/compat/degrade_ladder.schema`, and `schema/compat/fallback_map.schema`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Degrade Ladders

## Purpose
- Define explicit deterministic graceful-degradation behavior for product interoperability.
- Prevent silent feature disablement.
- Ensure degraded behavior is recorded, explainable, and replay-safe.

## Degrade Rule Format
Each degrade rule binds:
- `missing_capability_id`
- `fallback_action`
  - `disable_feature`
  - `substitute_stub`
  - `downgrade_mode`
  - `switch_to_read_only`
  - `refuse_connection`
- `user_message_key`
- deterministic metadata

Rules are declared per product in `data/registries/degrade_ladder_registry.json`.
Shared capability fallback chains are declared in `data/registries/capability_fallback_registry.json`.

## Deterministic Application
Rules are applied in stable order:
1. required-capability failures
2. contract mismatch handling
3. optional-capability degradation sorted by `capability_id`
4. within a capability, lowest `priority`, then `rule_id`

The first applicable rule wins for a capability.
Unknown capabilities remain inert and ignored deterministically.

## Visibility
Negotiation results must record:
- disabled capabilities and reasons
- substituted capabilities and targets
- enforced compatibility mode
- explicit degrade-plan rows

Products must surface this through deterministic CLI/TUI/reporting surfaces such as:
- `compat status`
- handshake/session logs
- proof bundles
- explain keys:
  - `explain.compat_degraded`
  - `explain.compat_read_only`
  - `explain.feature_disabled`

## Standard Fallbacks
- `cap.ui.rendered` may degrade to `cap.ui.tui`, then `cap.ui.cli`
- `cap.geo.atlas_unwrap` may degrade to `cap.geo.ortho_map_lens`
- `cap.logic.compiled_automaton` may degrade to `cap.logic.l1_eval`
- `cap.logic.debug_analyzer` may be disabled when not shared
- semantic-contract mismatch may switch to `compat.read_only`

## Strictness
- Strict compatibility modes may refuse instead of degrading.
- Read-only fallback is lawful only when the negotiated mode binds mutation law to observation-only authority.
- Silent feature disablement is forbidden.

## Runtime Enforcement
- Disabled capabilities must refuse with explicit explanation.
- Substituted capabilities must route to the declared stub or fallback mode.
- Degradation must not alter simulation semantics beyond declared compatibility restrictions.

## Non-Goals
- No per-platform fallback branches.
- No wall-clock or nondeterministic degrade decisions.
- No implicit feature hiding outside the negotiation record.
