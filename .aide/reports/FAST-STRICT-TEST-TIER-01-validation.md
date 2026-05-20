Status: PASS_WITH_WARNINGS
Last Reviewed: 2026-05-20
Task: FAST-STRICT-TEST-TIER-01

# Fast Strict Validation

## Sync

- `git fetch --all --prune`: PASS
- `git rev-parse HEAD`: `625f17344f4fc400d810784bd9d49ceacf91ad99`
- `git rev-parse origin/main`: `625f17344f4fc400d810784bd9d49ceacf91ad99`
- `git merge-base --is-ancestor origin/main HEAD`: PASS
- `git merge-base --is-ancestor HEAD origin/main`: PASS

## Contract And Tooling

- `python -m py_compile tools/test/run_fast_strict.py tools/validators/testing/check_test_tiers.py`: PASS
- `python tools/validators/testing/check_test_tiers.py --repo-root . --strict`: PASS
- `python tools/validators/testing/check_test_tiers.py --repo-root . --json`: PASS
- `python tools/test/run_fast_strict.py --repo-root . --list`: PASS
- `python tools/test/run_fast_strict.py --repo-root . --dry-run`: PASS
- final rerun of `python -m py_compile tools/test/run_fast_strict.py tools/validators/testing/check_test_tiers.py`: PASS
- final rerun of `python tools/validators/testing/check_test_tiers.py --repo-root . --strict`: PASS
- final rerun of `python tools/validators/testing/check_test_tiers.py --repo-root . --json`: PASS
- final rerun of `python tools/test/run_fast_strict.py --repo-root . --list`: PASS

## Artifact Parse And Hygiene

- `python -m json.tool .aide/reports/FAST-STRICT-TEST-TIER-01-results.json`: PASS
- `python -m json.tool .aide/reports/FAST-STRICT-TEST-TIER-01-run.json`: PASS
- `python -m json.tool .aide/reports/FAST-STRICT-TEST-TIER-01-repox-proof-manifest.json`: PASS
- `python -m json.tool .aide/reports/FAST-STRICT-TEST-TIER-01-repox-profile.json`: PASS
- `python -m json.tool contracts/testing/test_tiers.schema.json`: PASS
- `git diff --check`: PASS
- pre-commit `git diff --cached --check`: PASS
- post-commit `py -3 .aide/scripts/aide_lite.py commit check --latest`: FAIL on
  commit-message policy only. The task-specified commit body omitted local
  AIDE-required `## Changelog`, `## Risks`, and `AIDE-Token-Impact` fields.
  The failed commit was not amended because the task forbids amend/reset.

## Normal Gate

Command:

```text
python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/FAST-STRICT-TEST-TIER-01-run.json --md-out .aide/reports/FAST-STRICT-TEST-TIER-01-run.md
```

Result:

- status: PASS
- elapsed seconds: `332.828`
- commands total: 30
- commands passed: 30
- commands failed: 0
- commands skipped: 0

Included proof:

- T0 static/hygiene checks.
- AIDE doctor/validate/test/selftest/tools/roots/repo.
- strict repo/root/distribution/component validators.
- no-src/source, forbidden-root-name, and bad-root absence validators.
- docs sanity, include sanity, build target boundaries, UI shell purity, ABI boundaries.
- RepoX STRICT with generated output redirected to `.aide/reports/**`.
- CMake configure.
- CMake build-only `ALL_BUILD`.
- smoke CTest.

## Not Run

- Full CTest was not run.
- T3 product/projection proof was not run because this task does not touch
  product/projection/release surfaces.
- T4 public-header consumer and focused broad CTest debt lanes were not run as
  part of normal proof.
