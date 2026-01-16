# Performance Budgets (PERF0)

This document defines hard performance targets and regression budgets.
All budgets are measurable and must be tied to PERF3 fixtures.

## Tiers

- Baseline tier (2010 hardware)
- Modern tier (2020 hardware)
- Server tier

## Budgets (authoritative)

### Baseline tier
- Sim tick cost: <= 8.0 ms/tick
- Event queue processing: <= 1.0 ms/tick
- Derived jobs: <= 2.0 ms/frame
- Rendering submit: <= 4.0 ms/frame
- Memory budget: <= 2.0 GB
- IO budget: <= 256 KB/frame

### Modern tier
- Sim tick cost: <= 4.0 ms/tick
- Event queue processing: <= 0.5 ms/tick
- Derived jobs: <= 4.0 ms/frame
- Rendering submit: <= 2.0 ms/frame
- Memory budget: <= 4.0 GB
- IO budget: <= 1.0 MB/frame

### Server tier
- Sim tick cost: <= 6.0 ms/tick
- Event queue processing: <= 0.5 ms/tick
- Derived jobs: <= 1.0 ms/tick
- Rendering submit: <= 0.0 ms (no render)
- Memory budget: <= 8.0 GB
- IO budget: <= 128 KB/tick

## Measurement requirements

Each budget MUST be measured by a PERF3 regression fixture:
- Fixture defines workload and world size.
- Fixture records per-tick and per-frame timing.
- Fixture emits structured results under `run_root/perf/budgets/`.

## Failure artifacts

On violation, emit a report with:
- tier
- budget name
- threshold
- observed value
- fixture name and run parameters
