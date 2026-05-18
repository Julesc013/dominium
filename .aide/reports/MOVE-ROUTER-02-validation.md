# MOVE-ROUTER-02 Validation

Status: PARTIAL
Generated: 2026-05-18

## Passed

- `git diff --check`: PASS.
- `python -m py_compile tools/xstack/core/plan.py tests/integration/exploration_scale_guard_tests.py`: PASS.
- `python tests/integration/test_gate_fast_strict_full_profiles.py --repo-root . --case full_shards_groups`: PASS.
- `cmake --preset verify`: PASS.
- `python tools/validators/repo/check_bad_root_absence.py --repo-root . --json`: PASS; tracked bad-root file count is 0.
- `python tools/validators/repo/check_no_src_source_dirs.py --repo-root .`: PASS_WITH_WARNINGS; warnings are historical/archive findings.
- `python tools/validators/repo/check_forbidden_root_names.py --repo-root .`: PASS_WITH_WARNINGS; blocker count is 0.
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`: PASS.
- `python tools/validators/check_repo_layout.py --repo-root . --strict`: PASS.

## Partial Or Failed

- `cmake --build --preset verify`: PARTIAL.
  - Compilation completed far enough to run the integrated fast/smoke CTest set.
  - 57/57 fast/smoke tests passed in the build output.
  - The broader portability/TestX phase failed with 140 failures out of 344 tests.
- Focused RepoX is not green because current ruleset discovery still references `repo/repox/rulesets` instead of `contracts/repo/repox/rulesets`.
- Full proof was not claimed.

## Not Run In Closeout

- Full CTest outside the build-triggered suite.
- Projection generation.
- Release generation.
- Product boot proof.
- Internal pilot proof.
- Public release, tags, uploads, or installer work.

## Validation Interpretation

MOVE-ROUTER-02 is a valid partial repair boundary. It preserves the routed
structure and records exact remaining blocker classes for the next pass.

## Post-Commit Check

The first closeout commit completed, then `py -3 .aide/scripts/aide_lite.py commit check --latest`
reported commit-message policy failures for missing `## Changelog` and
`AIDE-Token-Impact`. The commit was not amended because the task forbids
amending. This follow-up evidence records the check result and closes with a
policy-compliant latest commit.

The second closeout evidence commit also failed commit-message policy because
its changelog prefixes were lowercase free-form labels rather than the
policy-defined category prefixes. The final closeout commit uses policy
categories such as `Internal:` and `Docs:`.
