Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# LIFE Remains & Salvage Guide (LIFE4)

This document explains the deterministic, event-driven remains and salvage
pipeline implemented in LIFE4. It is a developer guide, not gameplay design.

## Non-negotiable rules
- Remains MUST persist deterministically after death; no silent deletion.
- Remains decay MUST be event-driven; no global scans.
- Salvage MUST be rights-mediated and ledger-backed; no loot tables.
- Epistemic knowledge MUST gate salvage; no omniscient UI or tools.
- Collapse/refine MUST preserve counts and provenance hashes.

## Canonical data flow
1) Death pipeline creates:
   - post-death rights record
   - remains record
2) Remains are registered with the decay scheduler.
3) Observation hooks emit a death/remains notice for epistemic systems.
4) Salvage claims resolve deterministically via rights order.
5) Accepted salvage produces ledger transactions and provenance records.

## Rights resolution order
Resolution is deterministic and MUST follow this order:
1) Explicit contract
2) Estate executor (if authorized and not locked)
3) Jurisdiction default (if allowed)
4) Finder policy (if allowed)
5) Refusal

Any deviation is a determinism failure (see LIFE-REM-RIGHTS-001).

## Event-driven decay
- Each remains record has `next_due_tick`.
- `life_remains_decay_scheduler` processes only due remains.
- Decay progression MUST be batch vs step equivalent.

## Epistemic gating
- Salvage actions MUST check epistemic knowledge of remains.
- If knowledge is missing, claims MUST refuse with a stable refusal code.

## Fidelity and collapse/refine
- Collapsed remains are aggregated with provenance summary hashes.
- Refinement MUST preserve counts and provenance hashes.
- Visible remains MUST NOT disappear without a fidelity transition.

## Tests and CI gates
Required tests are in `dominium_life_remains`:
- deterministic remains creation (LIFE-REM-DET-001)
- decay schedule invariance (LIFE-REM-DECAY-001)
- rights resolution order (LIFE-REM-RIGHTS-001)
- ledger conservation (LIFE-REM-LEDGER-001)
- epistemic gating (LIFE-REM-EPIS-001)
- collapse/refine count + provenance preservation (LIFE-REM-COUNT-001)

## Common fixes
- Refusal: `INSUFFICIENT_EPISTEMIC_KNOWLEDGE`
  - Ensure observation hooks generate knowledge records for the actor.
- Ledger conservation failure
  - Verify salvage uses ledger transactions only; do not mutate balances directly.
- Decay determinism failure
  - Use ACT ticks and due-event scheduling; avoid wall-clock or per-frame ticking.