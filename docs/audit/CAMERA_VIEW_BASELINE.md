Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-16
Scope: EB-4 camera binding + view lens baseline (epistemic-safe, multiplayer-safe)
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Camera View Baseline

## Implemented Scope

1. Camera is treated as a TruthModel assembly with process-only mutation paths:
   - `process.camera_bind_target`
   - `process.camera_unbind_target`
   - `process.camera_set_view_mode`
   - `process.camera_set_lens`
2. View mode validation is registry-driven through `view_mode_registry`.
3. Observer truth-capable camera modes require watermark entitlement checks.
4. SRZ hybrid cross-shard spectator follow is policy-gated and deterministic.

## View Mode Matrix

1. `view.first_person.player`
   - Requires embodiment: `true`
   - Typical lens set: diegetic only
2. `view.third_person.player`
   - Requires embodiment: `true`
   - Typical lens set: diegetic only
3. `view.follow.spectator`
   - Requires embodiment: `false`
   - Cross-shard follow allowed only when `control_policy.allow_cross_shard_follow=true`
4. `view.free.lab`
   - Requires embodiment: `false`
   - Generally available for lab/private policy profiles
5. `view.free.observer_truth`
   - Requires embodiment: `false`
   - Requires observer entitlement + watermark policy

## Entitlement Requirements

1. Camera binding/view mode:
   - `entitlement.control.camera`
2. Spectator follow:
   - `entitlement.view.spectator`
   - `entitlement.view.follow`
3. Lens override:
   - `entitlement.control.lens_override`
4. Observer truth-capable watermark mode:
   - `entitlement.observer.truth`

## Policy Differences

1. Private server default (`server.policy.private.default`)
   - Allows free modes and cross-shard follow.
2. Ranked strict (`server.policy.ranked.strict`)
   - Restricts allowed view modes to player/spectator follow set.
   - Free camera modes refused by policy.
   - Cross-shard follow disabled by policy.

## Refusal Codes Used

1. `refusal.view.mode_forbidden`
2. `refusal.view.requires_embodiment`
3. `refusal.view.target_invalid`
4. `refusal.view.entitlement_missing`
5. `refusal.view.watermark_required`
6. `refusal.view.cross_shard_follow_forbidden`

## Determinism Coverage

1. Camera bind/view process replay determinism test asserts stable hash anchors.
2. Cross-shard follow allow/deny behavior is deterministic for identical inputs.
3. Ranked free-view policy refusal is deterministic.

## Limitations / Deferred

1. No client prediction or rollback in camera flow.
2. No advanced camera effects (shake, smoothing, VR) in this baseline.
3. No animation coupling; representation remains RenderModel-only.

## Forward Extensions

1. Camera effects as pack-driven policies.
2. Additional spectator patterns with explicit entitlements.
3. Extended watermark policy variants for tournaments and education profiles.
