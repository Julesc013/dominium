Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-15
Compatibility: Bound to Observation Kernel, lens gating, and process-only mutation.

# Diegetic Channels Over Network

## Purpose
Define diegetic-first multiplayer perception transport so instruments are Assemblies and readings are Perceived channels.

## Diegetic Instruments

1. `instrument.compass`
2. `instrument.clock`
3. `instrument.altimeter`
4. `instrument.radio`

Instrument readings are produced by deterministic process execution (`process.instrument_tick`) and exposed via PerceivedModel channels.

## Channel Contract

Minimum diegetic channels:

1. `ch.diegetic.compass`
2. `ch.diegetic.clock`
3. `ch.diegetic.altimeter`
4. `ch.diegetic.radio`

Non-diegetic and observer channels remain separate and law-gated.

## Transport Rules

1. Server computes PerceivedModel for each peer from lawful context.
2. Outgoing deltas include channel-filtered data only.
3. No direct truth payloads are transmitted for instrument channels.

## Camera/View Interaction

1. Camera view modes affect selection of relevant perceived channels, not channel permissions.
2. Camera mode never grants channels that are forbidden by LawProfile, EpistemicPolicy, or entitlements.
3. Observer truth-capable views must emit `ch.watermark.observer_mode`.
4. Ranked/strict server profiles may refuse free observer-style camera modes through registry policy.

## Determinism Requirements

1. Channel ordering is stable and registry-driven.
2. Quantization rules are deterministic and policy-defined.
3. Same truth inputs produce the same perceived channel payload hash.

## Cross-References

- `docs/net/EPISTEMIC_SCOPE_AND_FOG_OF_WAR.md`
- `docs/net/EPISTEMICS_OVER_NETWORK.md`
- `docs/architecture/truth_perceived_render.md`
