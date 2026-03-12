Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Diegetic Instrument Doctrine

Status: Canon-Consistent (ED-2 baseline)  
Version: 1.0.0  
Last Updated: 2026-02-16

## Purpose
Define deterministic diegetic instruments as Assembly-driven observation transforms. Instruments expose lawful perception channels and never bypass epistemic policy.

## Core Rules
1. Instruments are Assemblies in `UniverseState.instrument_assemblies`.
2. Instruments may be attached to a carrier (`carrier_agent_id`) or anchored to a station (`station_site_id`).
3. Instrument updates consume only `Perceived.now` and `Perceived.memory` channels allowed by:
   - `LawProfile`
   - `AuthorityContext`
   - `Lens`
   - `EpistemicPolicy`
4. Instruments never read `TruthModel` directly.
5. Instrument outputs are emitted as diegetic channels in `PerceivedModel`.
6. HUD presentation is render-only. If a value appears on HUD, it must come from a lawful diegetic channel.

## Determinism Invariants
1. Instrument update ordering is deterministic by `(instrument_id, instrument_type_id)`.
2. No wall-clock time in instrument logic. Tick-driven only.
3. All bounded collections (messages, notes, map rows) are stable-sorted.
4. Identical perceived inputs produce identical instrument outputs.

## Runtime Compatibility
1. Works with zero agents and zero instruments.
2. Works with embodied and unembodied agents.
3. Works under lockstep, authoritative, and SRZ-hybrid policies because it is perception-derived.

## Refusal Semantics
Deterministic refusal codes for instrument operations:
- `refusal.diegetic.radio_forbidden`
- `refusal.diegetic.message_too_large`
- `refusal.control.entitlement_missing`
- `refusal.ep.channel_forbidden`
- `refusal.ep.policy_missing`

## Non-Goals
1. No inventory/crafting semantics.
2. No omniscient or truth-bypassing instruments.
3. No full signals physics in this phase.
