Status: CANONICAL
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none

# TestX Architecture

## Scope

TestX is the behavioral proof layer for Dominium. It validates invariant compliance, determinism envelopes, workspace isolation, and regression locks using deterministic test execution contracts.

## Suite Stratification

TestX uses three formal suites defined in `data/registries/testx_suites.json`:

- `testx_fast`: manifest-driven selective suite for rapid validation.
- `testx_verify`: full verification lane for invariants, regressions, and determinism coverage.
- `testx_dist`: distribution-oriented lane (verify coverage + packaging compatibility coverage).

`scripts/dev/gate.py` maps modes to suites:

- `gate dev` -> `testx_fast`
- `gate verify` -> `testx_verify`
- `gate dist` -> `testx_dist`

## Manifest-Driven Selection

RepoX emits `docs/audit/proof_manifest.json`. The manifest contains:

- `changed_paths`
- `impacted_subsystems`
- `impacted_invariants`
- `required_test_tags`

`scripts/dev/testx_proof_engine.py` consumes the manifest and selects tests by intersecting required tags with suite registry tag mappings. If the manifest is missing, fast mode falls back to registry defaults.

## Determinism Envelopes

TestX includes dedicated envelope checks for:

- thread-count variance
- SRZ partition variance
- budget/fidelity selection variance
- named RNG stream stability

Envelope checks are non-semantic proofs that canonical outputs remain stable under allowed execution variance.

## Derived Artifact Contract

Determinism checks operate on canonical artifacts only. TestX ignores RUN_META artifacts during canonical hash comparisons and validates that canonical artifacts do not carry timestamp/run-meta keys.

## Workspace Isolation Proof

TestX validates that workspace-scoped outputs remain isolated under `out/build/<WS_ID>/` and `dist/ws/<WS_ID>/`, and that gate policy commands avoid hardcoded global output paths.

## Regression Lock Philosophy

Historical blocker classes are encoded as explicit regression tests under `tests/regression/historical_blockers/`. Each blocker family has a stable, repeatable proof that failure classes cannot silently recur.
