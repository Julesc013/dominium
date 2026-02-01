Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# CIV4 Multi-Scale Civilisation and Logistics

This document defines CIV4 scale domains, transitions, and long-range logistics.
All processing is deterministic and event-driven, with no global physics
simulation.

## Core components

- Scale domains (`schema/scale/SPEC_SCALE_DOMAINS.md`)
  - Local through universal domains with warp limits and fidelity caps.
- Interplanetary logistics (`schema/scale/SPEC_INTERPLANETARY_LOGISTICS.md`)
  - Shipment flows scheduled by ACT time.
- Interstellar logistics (`schema/scale/SPEC_INTERSTELLAR_LOGISTICS.md`)
  - Long-range flows with deterministic travel time.
- Scale time warp (`schema/scale/SPEC_SCALE_TIME_WARP.md`)
  - Interest-aware warp limits per domain.

## Event-driven transitions

- Domain transitions are scheduled events, not per-tick updates.
- Arrivals refine only when interest exists.
- Batch vs step equivalence is required.

## Interest binding

- Local interest may pin higher-domain objects (routes, ships).
- Macro interest does not force micro simulation.
- Escalation is explicit and deterministic.

## Epistemic constraints

- Distant events are known only through reports and diffusion.
- UI shows uncertainty and delays; no omniscient dashboards.

## CI enforcement

The following IDs in `docs/CI_ENFORCEMENT_MATRIX.md` cover CIV4:

- CIV4-FLOW-DET-001
- CIV4-BATCH-001
- CIV4-INT-001
- CIV4-WARP-001
- CIV4-HANDOFF-001
