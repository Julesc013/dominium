# Distributed Simulation Model (MMO0)

Status: binding.
Scope: deterministic, auditable distribution of a single logical universe
across multiple authoritative shards.

## Core principle

> The universe is logically single.
> It may be physically distributed.
> Distribution must not change outcomes.

Distribution, sharding, replication, and messaging are implementation details
under this invariant. Any distributed execution must be a semantics-preserving
projection of the same deterministic simulation used in single-shard mode.

## Canonical definitions

- Universe
  - A single logical history defined by WorldDefinition, capability baselines,
    and deterministic event logs.

- Shard
  - An authoritative simulator for a bounded set of domains.
  - A shard advances time for the domains it owns.
  - A shard is not a different engine. It runs the same deterministic code.

- Domain ownership
  - Each domain volume (topology node or bounded set) is owned by exactly one
    shard at a time.
  - Ownership transfers are explicit, occur only at commit boundaries, and are
    logged and replayable.

Each domain is owned by exactly one shard at a time.

- Cross-shard log
  - Append-only message logs mediate cross-shard interaction.
  - Messages do not mutate state by themselves. They are inputs to admission.

## Distributed determinism requirements

All shards MUST:

- run the same deterministic engine code paths
- obey the same budgets and refusal semantics
- apply state transitions only at commit boundaries
- emit deterministic events suitable for save/replay

Distributed execution MUST NOT:

- introduce wall-clock dependence into authoritative outcomes
- assume trusted clients or hidden authority
- relax determinism for throughput
- create alternate semantics for multiplayer vs singleplayer

Double ownership of a domain is forbidden. Double ownership creates
non-deterministic conflicts and breaks auditability.

## Relationship to scaling and macro time

The distributed model composes with SCALE-0 through SCALE-3:

- Fidelity tiers remain scheduling and representation policies over the same
  primitives.
- Macro capsules remain the lawful representation of collapsed domains.
- Budgets and admission control remain the only lawful mechanism to bound work.
- Cross-shard messages must preserve invariants and tolerances.

## Enforcement intent

This document defines the invariant surface that later MMO runtime and network
prompts must obey. Any implementation that changes outcomes compared to the
single-shard model is incorrect.

Multiplayer and singleplayer MUST use the same deterministic code paths.

## Related invariants

- MMO0-UNIVERSE-012
- MMO0-OWNERSHIP-013
- MMO0-TIME-016
- MMO0-COMPAT-018

## See also

- `docs/arch/SCALING_MODEL.md`
- `docs/arch/CROSS_SHARD_LOG.md`
- `docs/arch/DISTRIBUTED_TIME_MODEL.md`
- `docs/arch/MMO_COMPATIBILITY.md`
