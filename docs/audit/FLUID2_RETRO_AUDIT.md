Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# FLUID2 Retro Consistency Audit

Status: BASELINE
Last Updated: 2026-03-04
Scope: FLUID-2 containment, burst, leak, and INT coupling hardening.

## 1) Direct Interior Mass Mutation Audit

Scanned runtime mutation surfaces under:

- `src/fluid/`
- `src/interior/`
- `tools/xstack/sessionx/`

Findings:

- INT compartment updates remain centered in `src/interior/compartment_flow_engine.py`.
- No FLUID containment runtime previously existed to mediate burst/leak mass transfer.
- Existing FLUID-1 engine updates tank mass directly inside solver loop and does not expose process-level leak/burst pathways yet.

Migration note:

- FLUID-2 introduces explicit process helpers (`process.burst_event`, `process.start_leak`, `process.leak_tick`) that emit deterministic transfer events and coupling rows instead of hidden mutation.

## 2) Burst Logic Audit

Findings:

- FLUID-1 had overpressure detection with relief event logging.
- No deterministic burst event type/state schema existed.
- No explicit failure policy registry existed to differentiate relief-first vs strict-burst behavior.

Migration note:

- Add explicit pressure-vessel thresholds and failure policy registries.
- Route burst outcomes through safety/process artifacts and explain contracts.

## 3) Tank Mutation Boundaries

Findings:

- Tank state mutation currently happens in FLUID solver internals.
- No reusable process helper existed for leak-driven mass removal.

Migration note:

- Add process helpers to centralize deterministic tank decrement rules and event emission.
- Keep solver deterministic ordering by `graph_id -> node_id -> edge_id -> leak target`.

## 4) Coupling Boundary to INT

Findings:

- Coupling contract already exists (`FLUID -> INT` leak/flood model binding).
- No concrete FLUID runtime emission row for interior flooding hooks.

Migration note:

- Emit deterministic interior coupling rows from leak process (`interior_coupling_rows`) containing transferred mass and flood hazard delta.
- Keep INT as interior-scale owner; FLUID emits coupling artifacts only.

## 5) Summary

Retro audit confirms FLUID-2 can be introduced without canon conflict if:

- all containment failures are process/safety mediated,
- leak transfer stays FlowSystem-accounted,
- interior coupling remains artifact-driven and deterministic,
- failure cascades are explicitly bounded and logged.
