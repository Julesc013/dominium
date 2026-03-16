Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to Observation Kernel, LawProfile, AuthorityContext, Lens, EpistemicPolicy, and RetentionPolicy.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Epistemics Over Network Baseline

## Scope

This baseline records the MP-6 contract status for multiplayer epistemics and diegetic readiness across implemented replication paths.

## Policy Matrix

| Policy / Profile | Channel Surface | Truth Overlay | Non-Diegetic Channels | Retention |
| --- | --- | --- | --- | --- |
| `ep.policy.observer_truth` | broad + observer overlays | allowed when entitled | allowed when law/entitlement permit | `ep.retention.session_basic` |
| `ep.policy.lab_broad` | broad lab tooling channels | denied unless explicitly allowed by channel list | allowed when law/entitlement permit | `ep.retention.session_basic` |
| `ep.policy.player_diegetic` | diegetic-first channels | forbidden | forbidden by default | `ep.retention.session_basic` |
| `ep.policy.spectator_limited` | limited navigation/time channels | forbidden | limited | `ep.retention.none` |

## Channel Registry Summary

Primary channels enforced by deterministic filter pipeline:

1. Diegetic: `ch.diegetic.compass`, `ch.diegetic.clock`, `ch.diegetic.altimeter`, `ch.diegetic.radio`, `ch.diegetic.map_local`
2. Core: `ch.core.time`, `ch.core.navigation`, `ch.core.sites`, `ch.core.entities`, `ch.core.process_log`, `ch.core.performance`, `ch.camera.state`
3. Non-diegetic lab: `ch.nondiegetic.nav`, `ch.nondiegetic.entity_inspector`, `ch.nondiegetic.performance_monitor`
4. Observer-only overlays: `ch.truth.overlay.terrain_height`, `ch.truth.overlay.anchor_hash`

Registries:

1. `data/registries/epistemic_policy_registry.json`
2. `data/registries/retention_policy_registry.json`
3. `data/registries/perception_interest_policy_registry.json`

## Diegetic Instrument Availability

Pack:

1. `packs/core/pack.core.diegetic_instruments/pack.json`

Assemblies:

1. `instrument.compass`
2. `instrument.clock`
3. `instrument.altimeter`
4. `instrument.radio`

Deterministic update process:

1. `process.instrument_tick`

Network transport behavior:

1. Outbound perceived deltas include instrument channel payloads only when channels are allowed by `Lens + LawProfile + AuthorityContext + EpistemicPolicy`.
2. Forbidden channels refuse deterministically with `refusal.ep.channel_forbidden`.

## Precision Rules

Deterministic quantization is enforced in Observation Kernel:

1. Distance metric: Manhattan distance from `camera_viewpoint.position_mm`.
2. Rule selection: first `max_distance_mm` match sorted by `(max_distance_mm, rule_id)`.
3. Quantization:
   - `position_quantization_mm`
   - `orientation_quantization_mdeg`
4. No nondeterministic floating behavior in canonical perceived hashes.

## No-Leak Guarantees

Controls:

1. Observation Kernel derives all peer-visible state (`Truth -> Perceived`).
2. Net modules emit `net_perceived_delta` artifacts and hashes, not Truth payloads.
3. RepoX invariants:
   - `INV-NET-PERCEIVED-ONLY`
   - `INV-NO-TRUTH-OVER-NET`
   - `INV-EPISTEMIC-POLICY-REQUIRED`
   - `INV-DIEGETIC-DEFAULTS-SURVIVAL` (placeholder warn-level)
4. AuditX analyzers:
   - `E7_EPISTEMIC_LEAK_SMELL`
   - `E8_PRECISION_LEAK_SMELL`

## Determinism and No-Leak Test Coverage

1. `testx.net.epistemic_filter_determinism`
2. `testx.net.no_truth_leak_over_net`
3. `testx.net.channel_forbidden_refusal`
4. `testx.net.precision_quantization_rules`
5. `testx.net.diegetic_instruments_present`
6. `testx.net.interest_policy_determinism`

## Extension Points

1. Embodiment-specific diegetic channels (future prompt; no current avatar semantics).
2. Expanded retention policies and decay models.
3. Inference policies as explicit deterministic registry modules.
4. Additional anti-cheat epistemic checks in ranked server policy packs.
