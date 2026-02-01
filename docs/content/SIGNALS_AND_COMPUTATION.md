Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Signals and Computation (SIGNAL0)

This document explains the data-first signal and computation model. It is not
an electronics simulator and does not require micro-time physics.

## What this is (and is not)

This model treats computation as information transformation over time under
constraints, noise, latency, and power budgets. It explicitly avoids:

- SPICE or transistor-level simulation
- per-nanosecond ticking
- continuous differential solvers

Signals are sampled discretely and evolve only via Processes.

## Creativity preserved

Mods can express:

- digital logic (gates, latches, counters, state machines)
- analog pipelines (filters, integrators, amplifiers)
- mixed-signal bridges (ADC/DAC, sensors, relays)
- networks (routing, interception, jamming)

All of this is data-driven through signals, interfaces, and process families.

## Scale preserved

Signals are bounded and sampled. Latency and noise are explicit envelopes.
Collapse/expand uses macro capsules with summarized distributions and RNG stream
cursors to keep simulation deterministic at scale.

## Extending via data

Add or extend:

- new signal fields in `data/packs/*/data/signals.json`
- new signal interfaces (compatibility rules are data)
- process families for transformation, modulation, and filtering
- standards and instruments to govern accuracy

All identifiers must be reverse-DNS and stable, and all numeric values must
carry unit annotations per `docs/architecture/UNIT_SYSTEM_POLICY.md`.