# Diegetic Instruments Baseline

Status: DERIVED  
Date: 2026-02-16  
Scope: ED-2/4 deterministic diegetic instrument ecosystem

## Implemented Instrument Types
- `instr.compass`
- `instr.clock`
- `instr.altimeter`
- `instr.map_local`
- `instr.notebook`
- `instr.radio_text`
- `instr.rangefinder` (stub registry entry only)

## Channel Mapping
- `instr.compass` -> `ch.diegetic.compass`
- `instr.clock` -> `ch.diegetic.clock`
- `instr.altimeter` -> `ch.diegetic.altimeter`
- `instr.map_local` -> `ch.diegetic.map_local`
- `instr.notebook` -> `ch.diegetic.notebook`
- `instr.radio_text` -> `ch.diegetic.radio_text`

## Deterministic Runtime Contract
- Instrument outputs are derived from `Perceived.now` + `Perceived.memory` through `src/diegetics/instrument_kernel.py`.
- Observation path recomputes diegetic instrument channels after memory update and before final perceived hash emission.
- Notebook/radio message artifacts are bounded and deterministically ordered.
- Map-local is memory-derived and non-omniscient by construction.

## Multiplayer Behavior
- Lockstep: diegetic outputs are deterministic for identical perceived inputs.
- Server-authoritative: clients compute diegetic outputs locally from server-governed perceived inputs and memory policy.
- SRZ hybrid: same perceived/memory contract applies per-client after policy/lens filtering.
- No TruthModel payload transmission is required for diegetic instrument channels.

## RepoX / AuditX / TestX Coverage
- RepoX invariants:
  - `INV-INSTRUMENTS-PERCEIVED-ONLY`
  - `INV-DIEGETIC-CHANNELS-REGISTRY-DRIVEN`
- AuditX analyzers:
  - `E24_INSTRUMENT_TRUTH_LEAK_SMELL`
  - `E25_OMNISCIENT_MAP_SMELL`
- TestX:
  - `testx.diegetics.map_non_omniscient`
  - `testx.diegetics.instrument_determinism`
  - `testx.diegetics.notebook_write_entitlement`
  - `testx.diegetics.radio_delivery_deterministic`
  - `testx.diegetics.instruments_no_truth_access`

## Known Limitations
- `instr.radio_text` is deterministic message scaffolding only (no signal propagation physics yet).
- `instr.rangefinder` is declared as registry stub and not surfaced in non-stub runtime channel set.
- No inventory/crafting semantics are attached to instrument carrier state in this phase.

## Extension Points
- Domain sensor channels (`radiation`, `heat`, `signals`) can be added by extending `instrument_type_registry`.
- Calibration model evolution routes through `calibration_model_registry`.
- Multiplayer anti-cheat can consume notebook/radio spam telemetry without changing diegetic contract semantics.
