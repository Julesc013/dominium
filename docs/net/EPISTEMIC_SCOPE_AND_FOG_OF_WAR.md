Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-15
Compatibility: Bound to AuthorityContext, LawProfile, Lens, and Observation Kernel deterministic contracts.

# Epistemic Scope and Fog of War

## Purpose
Define deterministic multiplayer epistemics so clients receive only lawful PerceivedModel channels.

## Implementation Status
Epistemic memory is implemented with deterministic retention/decay/eviction and store-hash auditing.

## Canonical Inputs

1. `AuthorityContext.epistemic_scope`
2. `LawProfile.epistemic_policy_id`
3. `Lens` channel requirements
4. `EpistemicPolicy` + `RetentionPolicy`

Perceived derivation contract:

`TruthModel x Lens x LawProfile x AuthorityContext x EpistemicPolicy -> PerceivedModel`

## EpistemicPolicy IDs

1. `ep.policy.observer_truth`
2. `ep.policy.player_diegetic`
3. `ep.policy.spectator_limited`
4. `ep.policy.lab_broad`

Policies are data-defined under:

- `data/registries/epistemic_policy_registry.json`
- `data/registries/retention_policy_registry.json`

## Deterministic Fog of War

1. Fog is not a UI trick.
2. Fog is a deterministic filter over PerceivedModel channels and precision.
3. Memory is policy-governed:
   - `perceived.now`: current filtered observation
   - `perceived.memory`: retained observations (if retention allows)
4. Eviction must follow deterministic ordering and deterministic capacity limits.

## No-Leak Rules

1. Network transport payloads are PerceivedModel artifacts only.
2. TruthModel serialization over network is forbidden.
3. Hidden channels remain absent (not masked by placeholders) unless policy permits channel summaries.

## Refusal Codes

1. `refusal.ep.channel_forbidden`
2. `refusal.ep.entitlement_missing`
3. `refusal.ep.policy_missing`

## Cross-References

- `docs/net/EPISTEMICS_OVER_NETWORK.md`
- `docs/net/DIEGETIC_CHANNELS_OVER_NETWORK.md`
- `docs/contracts/authority_context.md`
- `docs/contracts/law_profile.md`
