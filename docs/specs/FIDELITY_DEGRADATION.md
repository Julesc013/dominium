Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Fidelity Degradation Policy (PERF0)

This document defines the deterministic fidelity degradation ladder.
Degradation MUST be graceful and MUST NOT affect authoritative simulation.

## Scope

Applies to presentation and derived systems only.
Authoritative simulation MUST be unaffected by fidelity changes.

## Degradation ladder (mandatory)

1) Placeholder
2) Coarse
3) Medium
4) Full

Transitions MUST be monotonic per asset until full fidelity is reached.

## Degradation rules

- Degradation MUST never block.
- Degradation MUST never change sim semantics.
- Partial visual completeness is allowed.
- Missing assets MUST fall back to deterministic placeholders.

## Forbidden behaviors

- Despawning visible entities without provenance.
- Pausing simulation to wait for assets.
- Visual-driven changes to simulation outcomes.
- Resetting state as a performance workaround.

## UI presentation rules

- UI MUST explicitly indicate degraded fidelity.
- UI MUST NOT misrepresent placeholder content as authoritative.
- UI MUST log degradation state transitions for diagnostics.

## Failure artifacts

On violation, emit a report under `run_root/perf/fidelity/`:
- asset id and fidelity tier
- reason for degradation
- frame/tick identifiers