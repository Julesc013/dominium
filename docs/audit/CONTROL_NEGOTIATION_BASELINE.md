Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CONTROL_NEGOTIATION_BASELINE

Status: BASELINE  
Last Updated: 2026-03-01  
Scope: CTRL-3 Negotiation Kernel + Decision Log formalization

## 1) Negotiation Axis Definitions

- `abstraction`: resolves requested abstraction level (`AL0`-`AL4`) against control policy and ranked constraints.
- `view`: resolves requested view policy against allowed view policies and ranked freecam restrictions.
- `epistemic`: resolves requested epistemic scope against allowed epistemic scope policy.
- `fidelity`: resolves requested fidelity (`micro|meso|macro`) against policy, availability, and budget-aware costs.
- `budget`: resolves requested cost units against RS-5 envelope and deterministic fair-share limits.

All axes are processed by `src/control/negotiation/negotiation_kernel.py` with deterministic ordering and no wall-clock inputs.

## 2) Canonical Downgrade Order

Downgrade entries are emitted in fixed order:

1. `abstraction`
2. `view`
3. `epistemic`
4. `fidelity`
5. `budget`

Tie-breaking and batch arbitration are deterministic:

- request ordering: `requester_subject_id`, then `control_intent_id`, then canonical hash
- downgrade ordering: axis rank, then `downgrade_id`

## 3) Budget Arbitration Behavior (RS-5)

- RS-5 envelope is consumed via `max_cost_units_per_tick`, runtime usage state, and fairness state.
- Per-subject fair-share cap is computed deterministically from connected subject set.
- Budget shortfall produces explicit downgrade entry (`axis=budget`, `reason_code=downgrade.budget_insufficient`).
- Optional strict shortfall refusal is supported through negotiation request extensions.

No silent budget fallback is permitted in migrated control paths.

## 4) Domain Migration Summary

Migrated domain downgrade/refusal paths now call the negotiation kernel:

- MAT-7 materialization: `src/materials/materialization/materialization_engine.py`
- MAT-9 inspection fidelity resolution: `src/inspection/inspection_engine.py`
- RS-5 inspection arbitration integration: `tools/xstack/sessionx/process_runtime.py`
- Control plane resolution/logging: `src/control/control_plane_engine.py`

Decision logs are emitted per control resolution under:

- `run_meta/control_decisions/{tick}.json`
- collision fallback: `run_meta/control_decisions/{tick}.{decision_id}.json`

## 5) Decision Log Baseline

Decision logs now include:

- negotiation input/resolved vectors
- downgrade IDs + structured downgrade entries (extensions)
- refusal codes + refusal payload (extensions)
- deterministic fingerprint and stable decision ID
- emitted IDs for intents/commitments/envelopes

UI-facing downgrade/refusal explanations are derived from decision-log artifacts only.

## 6) Extension Points

- MOB micro simulation:
  consume fidelity/budget resolution to gate deterministic micro activation tiers.
- SIG inspection depth:
  bind deeper inspection sections to `epistemic` + `budget` axes via negotiation extensions.
- multiplayer proof bundles:
  include control decision-log hashes and IR verification hashes in ranked proof artifacts.
