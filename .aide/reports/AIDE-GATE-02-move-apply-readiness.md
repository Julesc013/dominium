# AIDE-GATE-02 Move Plan Apply Readiness Gate

## Status

- Task ID: AIDE-GATE-02
- Gate result: PASS_WITH_WARNINGS
- Branch: main
- HEAD: eac1ada70adb20a1f5640d7fe79a8f5a2f93c991
- origin/main: ab7362987bcff405cac69d947efb1950cb2f2295
- Working tree status before: clean, local main ahead of origin/main by 1
- Working tree status after: pending final validation and commit

## Purpose

This gate exists to prevent the first real root-recycling move from starting just because a plan exists. It inspects the exact AIDE-MOVE-01 plan, verifies that the planned move is one low-risk documentation file, checks reference awareness, rollback, validation, and exception handling, and authorizes only the next apply task if the plan is reviewable.

## Planned Move

| Source | Target | Action | Risk | Notes |
| --- | --- | --- | --- | --- |
| `ide/README.md` | `docs/architecture/IDE_PROJECTIONS.md` | move | low | One binding IDE projection policy document; no source, runtime, build, package, identity, security, safety, ABI, or manifest file is planned to move. |

## Deferred Material

`ide/manifests/**` remains deferred and untouched. The schema and examples are machine-readable projection metadata with active references and are not part of AIDE-MOVE-01.

## Plan Artifacts

| Artifact | Present? | Valid? | Notes |
| --- | --- | --- | --- |
| `.aide/refactors/AIDE-MOVE-01.plan.toml` | yes | yes | Draft, not approved, apply_allowed=false. |
| `.aide/refactors/AIDE-MOVE-01.plan.json` | yes | yes | One planned move from `ide/README.md` to `docs/architecture/IDE_PROJECTIONS.md`. |
| `.aide/refactors/AIDE-MOVE-01.reference_rewrite_plan.json` | yes | yes | Six apply-phase rewrites plus review/historical entries. |
| `.aide/refactors/AIDE-MOVE-01.validation_plan.json` | yes | yes | Tier 0 validators present. |
| `.aide/refactors/AIDE-MOVE-01.rollback_plan.json` | yes | yes | Reverse move and reference rollback present. |
| `.aide/refactors/AIDE-MOVE-01.exception_update_plan.json` | yes | yes | Narrows `ide/` handling; does not retire the root. |
| `.aide/reports/AIDE-MOVE-01-PLAN-summary.json` | yes | yes | Planned move count is 1; apply remains false. |

## Reference Rewrite Review

The reference plan lists six apply-phase rewrites:

| File | Planned handling |
| --- | --- |
| `.gitignore` | Remove the tracked `!/ide/README.md` exception after the file moves under docs. |
| `scripts/verify_docs_sanity.py` | Update required docs path to `docs/architecture/IDE_PROJECTIONS.md`. |
| `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md` | Update authoritative metadata row from `/ide/README.md` to `/docs/architecture/IDE_PROJECTIONS.md`. |
| `ide/README.md` line 1 | Update heading during move so the document no longer presents itself as the root path. |
| `ide/README.md` line 8 | Update self-reference to the new docs path during move. |
| `tools/aide/select_move_wave.py` | Update selector wording after apply so it does not keep recommending the already-moved README. |

Generated architecture registries are marked review/regeneration, not automatic hand edits. Historical AIDE and audit references are marked no-rewrite.

## Validation Plan Review

The plan includes Tier 0 AIDE doctor, validate, test, selftest, tools validate, roots validate, repo validate, strict repo/root/distribution/component validators, docs sanity, build target boundaries, UI shell purity, ABI boundaries, and git diff checks before and after apply.

## Rollback Plan Review

Rollback is a single reverse move from `docs/architecture/IDE_PROJECTIONS.md` back to `ide/README.md`, plus reverse apply-phase reference rewrites, exception note rollback, and Tier 0 validation after rollback. No shim is planned.

## Exception Update Plan Review

The `ide/README.md` gitignore exception can narrow after apply because the moved target is under `docs/`. The `ide/` root exception remains because `ide/manifests/**` and generated projection outputs remain in place. No exception is retired by this gate.

## No-Apply Invariants

- moves applied? no
- deletes applied? no
- renames applied? no
- references rewritten? no
- active aliases? no
- exceptions retired? no
- product/source/runtime/build behavior changed? no

## Validation Results

| Command | Result | Notes |
| --- | --- | --- |
| Plan JSON/TOML inspection | PASS | All plan files parse; plan remains draft/not-approved/no-apply. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | AIDE doctor passed. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | AIDE validate passed. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE focused tests passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | AIDE selftest passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | AIDE tools validate passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | AIDE roots validate passed. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | AIDE repo validate passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest commit check passed. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict repo layout passed; this Python emitted a non-blocking `tomllib` fallback warning. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict root allowlist passed; this Python emitted a non-blocking `tomllib` fallback warning. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Distribution layout passed; this Python emitted a non-blocking `tomllib` fallback warning. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS_WITH_WARNINGS | Component matrices passed; this Python emitted a non-blocking `tomllib` fallback warning. |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity passed. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | Build boundary check passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity passed. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundary check passed. |
| `git diff --check` | PASS | No whitespace errors. |
| `git diff --cached --check` | PASS | No staged whitespace errors. |

## Known Warnings

- The reference plan has high raw reference complexity because generated AIDE/repo evidence and historical audit artifacts mention `ide/README.md`.
- Generated architecture registry entries are marked review/regeneration for the apply task rather than automatic rewrite.
- The original move plan remains draft/not-approved/no-apply; this gate report, not the plan file, authorizes the next task.
- The `python` executable used for required validator commands emitted non-blocking `tomllib` fallback warnings while returning pass.

## Blockers

None for AIDE-MOVE-01-APPLY. All other move waves remain blocked.

## Gate Decision

PASS_WITH_WARNINGS. The plan is narrow, docs-only, reversible, reference-aware, validator-backed, and keeps `ide/manifests/**` deferred. The warnings are apply-task review items, not blockers for starting the single scoped apply task.

## Authorization

`AIDE-MOVE-01-APPLY may proceed for the single planned move only. No other move is authorized.`
