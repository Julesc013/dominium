Status: CANONICAL
Last Reviewed: 2026-02-26
Version: 1.0.0
Scope: MAT-8 deterministic reenactment model

# Reenactment Model

## Definition

Reenactment is a derived simulation/view artifact generated from canonical records.

Inputs:

- event stream index,
- commitments,
- batch lineage,
- deterministic policy and budget context.

Outputs:

- replayable timeline artifacts at requested fidelity (`macro`, `meso`, `micro` when allowed).

## Non-Mutation Rule

Reenactment never mutates canonical truth.

- It is a derived observer tool.
- It can be cached and compacted.
- It cannot rewrite authoritative state.

## Deterministic Reseeding

All reenactment generation must use deterministic seeds only.

Baseline seed derivation:

- `H(target_id, tick_range, inputs_hash, pack_lock_hash)`

No wall-clock inputs, nondeterministic RNG, or platform-order dependence are allowed.

## Fidelity and Degradation

Requested fidelity is best-effort under deterministic budgets.

- `macro`: summarized timeline outputs.
- `meso`: step/schedule timeline with commitment and manifest links.
- `micro`: only when ROI/performance budget and law permit; otherwise deterministic degrade to `meso` then `macro`.

## Invariants Preserved

Reenactment must preserve and expose verifiable continuity for:

- event ordering,
- commitment linkage,
- batch lineage continuity,
- conservation ledger references.

## Epistemic Gating

Reenactment detail visibility is law/lens/authority gated.

- Unauthorized users must not gain hidden truth through reenactment.
- Ranked policy may redact details while preserving reason codes and deterministic fingerprints.

## Compaction Compatibility

Reenactment sources may be compacted under RS-3 policies if invariant continuity is preserved.

- Inputs hash must remain stable for equivalent retained canonical history.
- Reenactment artifacts are reproducible from retained checkpoints + logs + lineage summaries.
