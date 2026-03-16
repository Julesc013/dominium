Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Communication Channels Overview

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: Canon-Consistent (ED-2 baseline)  
Version: 1.0.0  
Last Updated: 2026-02-16

## Scope
Define deterministic diegetic communication scaffolding without introducing full signal physics.

## Current Channel
- `instr.radio_text` emits/consumes structured message artifacts.

## Message Model
Message artifacts are schema-bound and tick-indexed:
1. `message_id`
2. `author_subject_id`
3. `created_tick`
4. `channel_id` (`msg.radio` or `msg.notebook`)
5. bounded `payload`
6. optional `signature`

## Delivery Model (ED-2)
1. Deterministic local delivery table.
2. Optional deterministic tick delay by policy table.
3. No wall-clock or network jitter dependency.
4. No RF propagation/occlusion physics yet.

## Authority And Entitlements
1. Send command: `diegetic.radio.send_text`
2. Receive command: `diegetic.radio.receive`
3. Required entitlement: `entitlement.diegetic.radio_use`

## Refusals
1. `refusal.diegetic.radio_forbidden`
2. `refusal.diegetic.message_too_large`

## Forward Path
Later domain work can replace transport semantics with full signals-domain propagation while preserving:
1. message schema
2. deterministic ordering
3. refusal contract surface
