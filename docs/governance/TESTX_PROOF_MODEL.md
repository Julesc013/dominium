Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none
Stability: stable
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# TestX Proof Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Scope

- TestX is the runtime proof layer for RepoX policy claims.
- RepoX emits required proofs into `build/proof_manifests/repox_proof_manifest.json`.
- TestX consumes this manifest and fails if required proofs are missing.

## Proof Manifest Contract

- Producer: `scripts/ci/check_repox_rules.py`.
- Consumer: `tests/invariant/proof_manifest_tests.py`.
- Manifest includes:
  - `required_capability_checks`
  - `required_refusal_codes`
  - `required_invariants`
  - `required_tests`
  - `focused_test_subset`
  - `available_testx_tests`

## Runtime Proof Expectations

- Capability claims must be proven by command execution tests, not metadata-only scans.
- Refusal code claims must be proven by deterministic refusal paths.
- Process-only mutation claims must be proven by process guard + invariant tests.
- Anti-cheat and epistemic claims must be proven by renderer and freecam contract tests.
- Packaging claims must be proven by pack/verify/index determinism tests and
  install projection digest tests.
- Rollback claims must be proven by lockfile re-projection equivalence.

## Failure Semantics

- Missing proof manifest fields are blocking failures.
- Missing required tests are blocking failures.
- RepoX/TestX disagreement on required proofs is a blocking failure.
- Package integrity mismatch or projection nondeterminism is a blocking failure.
