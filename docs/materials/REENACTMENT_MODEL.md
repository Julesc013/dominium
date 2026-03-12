Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, and `docs/materials/NOTHING_JUST_HAPPENS.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Reenactment Model (MAT-8)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose
Define deterministic commitment+event driven reenactment as a derived simulation layer that explains macro/meso outcomes without requiring global micro simulation.

## Canonical Inputs
Reenactment generation consumes:
- ordered event stream indices,
- linked commitments,
- batch lineage references,
- requested target and tick range,
- deterministic budget/fidelity policy.

## Derived-Only Contract
- Reenactment never mutates canonical TruthModel.
- Reenactment artifacts are cacheable derived artifacts keyed by deterministic input hash.
- Any replay sandbox execution is isolated from authoritative state.

## Fidelity Levels
- `macro`: summarized timeline (milestones, totals, outcomes).
- `meso`: step-by-step process timeline (commitments, manifests, project steps, maintenance actions).
- `micro`: allowed only when policy and budget permit ROI-bounded deterministic refinement.

If budget is insufficient, deterministic degradation applies: `micro -> meso -> macro`.

## Deterministic Seed Derivation
- Reenactment seed basis: `H(target_id, tick_range, inputs_hash, desired_fidelity)`.
- Any stochastic refinement must use named streams rooted in this seed basis.
- Identical inputs must produce identical timeline hashes.

## Epistemic Gating
- Detail visibility is law/authority gated.
- Unauthorized observers receive quantized or redacted timeline fields.
- Reenactment output must never reveal hidden truth not permitted by active lens/law.

## Ranked/Proof Integration
- Reenactment artifacts are optional derived proof supplements.
- Strict servers may require commitment/event hash consistency checks.
- Claimed events that fail ledger/hash consistency are flagged by anti-cheat/audit pipelines.
