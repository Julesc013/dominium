Status: DERIVED
Last Reviewed: 2026-02-16
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to canon/glossary v1.0.0, process-only mutation, and deterministic SRZ/session pipeline contracts.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Control Substrate Baseline

## Scope
EB-1 establishes controller/embodiment/representation separation and deterministic control bindings without adding movement, collision, or gameplay semantics.

## Implemented
1. Controller + binding substrate in deterministic runtime state (`controller_assemblies`, `control_bindings`) with optional presence.
2. Process-only control mutation:
- `process.control_bind_camera`
- `process.control_unbind_camera`
- `process.control_possess_agent`
- `process.control_release_agent`
- `process.control_set_view_lens`
3. Control actions and controller capability registries integrated into compile + lockfile flow.
4. Handshake/session status surfaces include deterministic control capability announcements from server profile entitlement policy.
5. SRZ hybrid guardrail for possession routing:
- default policy forbids cross-shard possession
- deterministic refusal `refusal.control.cross_shard_possession_forbidden`
6. RepoX + AuditX rules for control bypass and hardcoded player special-casing.

## Stubbed / Deferred
1. Embodiment primitives (body geometry, collision, locomotion physics).
2. Possession-driven movement effects.
3. Cross-shard possession support (policy currently default-forbidden).
4. Order binding execution for multi-agent command hierarchies (CIV-series follow-up).

## Policy Matrix
1. `observer/lab`:
- Camera control allowed when entitled and law-permitted.
- Possession allowed only when `entitlement.control.possess` is present.
- Lens override requires `entitlement.control.lens_override` and lens law gating.
2. `ranked`:
- Server profile can explicitly disallow possession/lens override entitlements.
- Handshake surfaces allowed control capability booleans.
3. `private`:
- Server profile may allow possession and lens override by entitlement policy.
- Cross-shard possession remains forbidden unless policy extension enables it.

## Refusal Codes
1. `refusal.control.entitlement_missing`
2. `refusal.control.law_forbidden`
3. `refusal.control.target_invalid`
4. `refusal.control.already_possessed`
5. `refusal.control.possession_not_supported`
6. `refusal.control.lens_forbidden`
7. `refusal.control.cross_shard_possession_forbidden`

## Determinism + Regression Coverage
1. `testx.control.no_agents_no_controllers_run_ok`
2. `testx.control.possession_deterministic`
3. `testx.control.possession_refusal_without_entitlement`
4. `testx.control.cross_shard_possession_refusal`
5. `testx.control.lens_override_gated`
6. `testx.repox.negative_invariants_smoke` (includes new control invariants)

## Extension Points (EB-2/EB-3)
1. Bind possession intents to embodiment/body primitives while preserving process-only mutation.
2. Add policy-controlled cross-shard possession handoff protocol.
3. Add order-binding process family for one-to-many control.
4. Expose richer admin/perception views through PerceivedModel-only tooling.
