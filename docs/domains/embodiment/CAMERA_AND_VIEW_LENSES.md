Status: DERIVED
Last Reviewed: 2026-02-16
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to process-only mutation, Observation Kernel epistemic filtering, and multiplayer policy registries.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Camera And View Lenses

## Purpose
Define a canonical camera/view contract that works for observer, spectator, embodied, and unembodied targets without granting extra truth access.

## Camera Model

1. Camera is a TruthModel assembly (`camera_assemblies`).
2. Camera binding is process-only mutation.
3. Camera state may exist with zero agents and zero bodies.
4. Representation remains RenderModel-only; camera state does not directly encode mesh or animation details.

## View Modes

1. `view.first_person`
2. `view.third_person`
3. `view.free`
4. `view.follow`

Each mode is selected from `view_mode_registry` and enforced through law + entitlement checks.

## Binding Contract

1. `process.camera_bind_target`
2. `process.camera_unbind_target`
3. `process.camera_set_view_mode`
4. `process.camera_set_lens`

No direct UI or renderer mutation is allowed.

## Camera Without Agents

1. If no agents exist, camera assemblies remain valid and may use `view.free` where policy allows.
2. If target binding references an unavailable target, deterministic refusal is emitted.
3. Session boot remains valid with no controller and no possession bindings.

## Epistemic/Lens Rules

1. Camera mode selects a view behavior only; it never elevates epistemic privileges.
2. Lenses and channels are still filtered by:
   - LawProfile
   - AuthorityContext
   - EpistemicPolicy
3. Observer truth views require explicit entitlement and watermark channel emission.

## Watermark Requirement

1. Observer truth-capable view modes/lenses must emit `ch.watermark.observer_mode`.
2. Watermark is a PerceivedModel channel, not a rendering side-channel.
3. Missing required watermark is a refusal condition.

## Multiplayer Safety

1. Lockstep: camera intents replicate as deterministic process intents.
2. Server-authoritative: camera state changes execute on server processes and replicate via Perceived deltas.
3. SRZ hybrid: camera routing follows shard ownership and policy-gated cross-shard follow rules.
4. TruthModel payloads are never transmitted for camera/view features.

## Refusal Surface

1. `refusal.view.mode_forbidden`
2. `refusal.view.requires_embodiment`
3. `refusal.view.target_invalid`
4. `refusal.view.entitlement_missing`
5. `refusal.view.watermark_required`
6. `refusal.view.cross_shard_follow_forbidden`

## Determinism Requirements

1. Binding replacement and conflict handling rules are deterministic.
2. View mode and lens validation depend only on canonical inputs (registries, law, authority, policies, state).
3. Replay of identical camera intents yields identical hash anchors.
