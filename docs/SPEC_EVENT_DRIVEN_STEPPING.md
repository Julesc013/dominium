# SPEC_EVENT_DRIVEN_STEPPING — Event-Driven Macro Stepping Canon

Status: draft
Version: 1

## Purpose
Define the canonical Event-Driven Macro Stepping system: the deterministic scheduling
model by which large-scale simulation advances only when events are due — never by
scanning or ticking the entire universe.

This spec is documentation-only. It introduces no runtime logic.

## Core axioms (locked)
1) Macro simulation advances only via scheduled events.
2) No macro state is updated without an event trigger.
3) Every macro object exposes next_due_tick.
4) Event execution order is deterministic.
5) Processing events in batch equals processing step-by-step.
6) Events may schedule future events.
7) Removing interest may delay but never reorder events.
8) Event execution never fabricates state.
9) Macro stepping integrates with fidelity projection.
10) Macro stepping integrates with time warp.

## Definitions

### Macro object
Any aggregated entity whose state is not micro-simulated. Examples:
- population cohort
- city aggregate
- national treasury
- production system
- contract
- ephemeris provider

### Event
A deterministic state transition scheduled at an ACT tick. Contains:
- event_id
- target object
- trigger_tick (ACT)
- deterministic ordering key
- payload/parameters

### Next_due_tick
The earliest ACT tick at which a macro object requires processing. Stored explicitly.

### Event queue
A deterministic priority queue ordered by:
- trigger_tick
- stable secondary key

## Event execution model (mandatory)

Pseudo-code:

  WHILE (next_event.trigger_tick <= ACT_target):
      execute(next_event)
      update target object state
      compute new next_due_tick
      enqueue any new events

No event is skipped. No event is processed early.

## Batch vs step invariance (mandatory)
Executing N events one-by-one produces the same result as executing them in a single
batch up to ACT_target. Time warp may batch events aggressively, but results must be
identical.

This invariant underpins:
- fast-forward
- offline progression
- MMO catch-up
- replay

## Domains that must use macro events
Macro stepping applies to:
- population (births, deaths, aging thresholds)
- economy (interest, rent, wages, contract maturities)
- production systems (batch completion)
- logistics (shipment arrival)
- governance (elections, law changes)
- diplomacy (treaty expiration)
- ephemerides (precomputed transitions)
- time-based doctrines and policies

Micro-level simulation is exempt and handled separately.

## Interaction with interest sets
- Interest affects fidelity, not event scheduling.
- Macro events execute even if a region is COLD or LATENT.
- Loss of interest may delay refinement or collapse micro state but MUST NOT cancel
  scheduled events.

## Engine vs game responsibilities

Engine (Domino, C89/C90) MAY:
- provide deterministic priority queues
- provide ACT advancement helpers
- provide canonical ordering primitives

Engine MUST NOT:
- create events
- interpret event meaning
- manage macro objects

Game (Dominium, C++98) MUST:
- schedule macro events
- execute event handlers
- maintain next_due_tick per macro object
- integrate with fidelity projection and interest sets

## Engine hooks (implementation notes)
Engine provides deterministic scheduling primitives only:
- time event queue (priority by trigger_tick, stable secondary key)
- peek/pop and cancellation helpers
- batch processing helper for events due <= target ACT

Engine does not interpret event meaning or mutate macro objects.
Game provides the event handlers and updates next_due_tick per macro object.

## Performance requirements
- O(log n) enqueue/dequeue
- no per-tick scans
- event queues bounded by active objects
- memory proportional to number of scheduled events, not universe size

## Prohibitions (enforced)
- "Tick every city"
- "Update all populations"
- fixed-interval macro loops
- per-frame macro updates
- hidden timers

## Examples (mandatory)

### 1) Single farm on Earth, 10,000 defined planets
Only local micro sim and a few macro events run. Event queue contains farm production
and a small set of system-level events; distant systems remain latent but still have
scheduled macro events when due.

### 2) Million-year fast-forward
Birth/death and contract maturity events fire in deterministic order. No intermediate
ticking occurs; batch execution yields the same result as step-by-step.

### 3) MMO server pause/resume
Server resumes at ACT_target and processes due events in batch. Results match a
continuous run because batch invariance holds.

### 4) Logistics shipment across system
Shipment arrival event fires at trigger_tick even if the destination region is latent.
Fidelity remains macro until interest rises.

## ASCII diagram

  [ Macro Objects ] -> [ Event Queue ] -> [ Execution ] -> [ Updated Macro State ]
                             ^                               |
                             +----------- schedule ----------+

## References
- Interest sets: `docs/SPEC_INTEREST_SETS.md`
- Fidelity projection: `docs/SPEC_FIDELITY_PROJECTION.md`
- Provenance: `docs/SPEC_PROVENANCE.md`
- Time system: `docs/SPEC_TIME_CORE.md`

## Test and validation requirements (spec-only)
Implementations must provide:
- batch vs step equivalence tests
- event ordering determinism tests
- time warp correctness tests
- MMO catch-up tests
- event starvation tests
