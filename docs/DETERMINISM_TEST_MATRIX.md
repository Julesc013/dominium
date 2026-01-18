# Determinism Test Matrix (DET0)

This document defines the canonical determinism test matrix and execution coverage.
All listed combinations are REQUIRED unless explicitly marked as future.
Any mismatch in required hashes is a merge-blocking failure.

## Scope

This matrix applies to authoritative simulation paths in engine and game, and to server-auth runs.
It assumes a single ACT time model, event-driven stepping, and lockstep plus server-authoritative parity.

## Axes

### A) Execution mode
- Singleplayer (loopback server-auth)
- Local MP lockstep
- Server-auth client/server
- Server-auth MMO shard (future)

### B) Step strategy
- Step-by-step (1 tick at a time)
- Batch (N ticks at a time)
- Event-driven jump to next_due_tick

### C) Hardware/Backend variance
- Different CPUs (same OS)
- Different render backends (visual divergence allowed)
- Different OS (where supported)

### D) Fidelity tier
- Macro only
- Meso
- Micro bubble
- Focus

## Required hash match rules

For each axis combination, the following hashes MUST match unless noted:
- HASH_SIM_CORE
- HASH_SIM_ECON
- HASH_SIM_INFO
- HASH_SIM_TIME
- HASH_SIM_WORLD

The following hash is non-gating and may diverge:
- HASH_PRESENTATION

## Matrix (authoritative combinations)

Each row is a required matrix cell. If a row is marked "future", it is planned but non-blocking until enabled.

| Exec mode | Step strategy | Hardware/Backend variance | Fidelity tier | Required hashes | Allowed divergence | Fixtures |
| --- | --- | --- | --- | --- | --- | --- |
| Singleplayer (loopback) | Step-by-step | Same CPU/OS | Macro | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Minimal Earth-only, Death/Estate, Birth/Lineage, Remains/Salvage, CIV0a Survival |
| Singleplayer (loopback) | Batch (N) | Same CPU/OS | Macro | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Minimal Earth-only, Warp |
| Singleplayer (loopback) | Event-driven jump | Same CPU/OS | Macro | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Minimal Earth-only |
| Local MP lockstep | Step-by-step | Same CPU/OS | Macro | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Sol-only |
| Local MP lockstep | Batch (N) | Same CPU/OS | Macro | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Sol-only, Warp |
| Server-auth client/server | Step-by-step | Same CPU/OS | Macro | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Market contract |
| Server-auth client/server | Event-driven jump | Same CPU/OS | Macro | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Info/comm |
| Singleplayer (loopback) | Step-by-step | Different CPUs | Macro | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Minimal Earth-only |
| Local MP lockstep | Step-by-step | Different CPUs | Macro | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Sol-only |
| Server-auth client/server | Step-by-step | Different CPUs | Macro | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Market contract |
| Singleplayer (loopback) | Step-by-step | Different render backends | Macro | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Minimal Earth-only |
| Local MP lockstep | Step-by-step | Different render backends | Macro | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Sol-only |
| Server-auth client/server | Step-by-step | Different render backends | Macro | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Market contract |
| Singleplayer (loopback) | Step-by-step | Different OS | Macro | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Minimal Earth-only |
| Local MP lockstep | Step-by-step | Different OS | Macro | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Sol-only |
| Server-auth client/server | Step-by-step | Different OS | Macro | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Market contract |
| Server-auth MMO shard (future) | Step-by-step | Different CPUs | Macro | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | 10k systems latent |
| Singleplayer (loopback) | Step-by-step | Same CPU/OS | Meso | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Sensor |
| Singleplayer (loopback) | Step-by-step | Same CPU/OS | Micro bubble | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Sensor |
| Singleplayer (loopback) | Step-by-step | Same CPU/OS | Focus | SIM_CORE, SIM_ECON, SIM_INFO, SIM_TIME, SIM_WORLD | Presentation only | Sensor |

## Fixtures (required)

All fixtures are required and MUST be versioned and stable. Minimal data packs are listed per fixture.

- Minimal Earth-only scenario
  - Data packs: core/astro, core/biomes, core/time, core/economy (minimal)
- Sol-only scenario
  - Data packs: core/astro (Sol set), core/time, core/world
- 10k systems latent scenario (macro only)
  - Data packs: core/astro (generated), core/time, core/world (macro)
- Market contract scenario (ledger obligations)
  - Data packs: core/economy, core/markets, core/contracts
- Info/comm scenario (delayed message)
  - Data packs: core/info, core/comm, core/time
- Warp scenario (TW batch stepping)
  - Data packs: core/time, core/sim, core/world
- Sensor scenario (degraded info)
  - Data packs: core/sensors, core/info, core/time
- Death/Estate scenario (LIFE2 pipeline)
  - Data packs: core/time, core/economy (ledger core), core/life (death/estate)
- Birth/Lineage scenario (LIFE3 pipeline)
  - Data packs: core/time, core/life (birth/lineage), core/resources (minimal)
- Remains/Salvage scenario (LIFE4 pipeline)
  - Data packs: core/time, core/life (remains/salvage), core/economy (ledger core)
- CIV0a Survival scenario (cohort needs/consumption)
  - Data packs: core/time, core/civ (cohorts/needs minimal)

## Required artifacts on failure

Any failure MUST emit a desync bundle containing:
- ACT at failure
- Partition hashes (all SIM_* partitions)
- Input event log
- Event queue snapshot
- Partition hash diff report

## Prohibitions

- No determinism gate may be downgraded or disabled without explicit governance approval.
- No flake tolerance is allowed for determinism failures.
- Partial-state comparisons are FORBIDDEN unless the partition is defined in
  `docs/DETERMINISM_HASH_PARTITIONS.md`.
