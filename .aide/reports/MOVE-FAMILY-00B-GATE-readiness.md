# MOVE-FAMILY-00B-GATE IDE Manifest Projection Apply Readiness Gate

## Status

- Task ID: MOVE-FAMILY-00B-GATE
- Gate result: PASS_WITH_WARNINGS
- Branch: main
- HEAD: 32dc93947661c98935d1308f7144eab5e78984bf
- origin/main: 32dc93947661c98935d1308f7144eab5e78984bf
- Working tree before gate writes: clean
- Working tree after gate writes: scoped gate evidence only

## Purpose

This gate exists because `ide/manifests/**` is machine-readable IDE projection metadata, not passive documentation. MOVE-FAMILY-00B-PLAN proposed moving the remaining tracked IDE manifest source files into `contracts/projections/ide/**`; this gate verifies the move is scoped, reversible, reference-aware, validator-backed, and sufficient to retire the `ide` source-root exception only after apply proves `git ls-files ide` is empty.

## Planned Moves

| Source | Target | Action | Risk | Notes |
| --- | --- | --- | --- | --- |
| `ide/manifests/projection_manifest.schema.json` | `contracts/projections/ide/projection_manifest.schema.json` | move | medium | Projection manifest schema authority moves to contract/projection ownership. |
| `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json` | `contracts/projections/ide/examples/example_linux_clang_modern_client_gui.projection.json` | move | medium | Authored example moves with schema. |
| `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json` | `contracts/projections/ide/examples/example_win_vc6_win9x_client_gui.projection.json` | move | medium | Authored example moves with schema. |

## Plan Artifacts

| Artifact | Present? | Valid? | Notes |
| --- | --- | --- | --- |
| `.aide/refactors/MOVE-FAMILY-00B.plan.toml` | yes | yes | Draft, not approved, `apply_allowed = false`, three planned moves. |
| `.aide/refactors/MOVE-FAMILY-00B.plan.json` | yes | yes | Exact three planned source files; deferred tracked files 0; blocked files 0. |
| `.aide/refactors/MOVE-FAMILY-00B.ide_manifest_inventory.json` | yes | yes | Three tracked JSON manifest files; no generated or unknown tracked manifest file. |
| `.aide/refactors/MOVE-FAMILY-00B.ide_manifest_ownership.json` | yes | yes | Target owner `contracts/projections/ide`; target creation planned for apply. |
| `.aide/refactors/MOVE-FAMILY-00B.reference_rewrite_plan.json` | yes | yes | Five apply rewrite groups, five review/later groups, historical references preserved. |
| `.aide/refactors/MOVE-FAMILY-00B.validation_plan.json` | yes | yes | Tier 0 validators plus stale-reference and manifest parse checks. |
| `.aide/refactors/MOVE-FAMILY-00B.rollback_plan.json` | yes | yes | Reverse moves, references, exceptions, and target directory cleanup. |
| `.aide/refactors/MOVE-FAMILY-00B.exception_update_plan.json` | yes | yes | Retires `ide` only after `git ls-files ide` is empty and validators pass. |
| `.aide/reports/MOVE-FAMILY-00B-PLAN-review.md` | yes | yes | Reviewer-facing plan summary present. |
| `.aide/reports/MOVE-FAMILY-00B-PLAN-manifest-boundaries.md` | yes | yes | Manifest boundary analysis present. |
| `.aide/reports/MOVE-FAMILY-00B-PLAN-summary.json` | yes | yes | Plan result PASS_WITH_WARNINGS and ready for gate. |

## Reference Rewrite Review

The plan contains five apply rewrite groups:

- `.gitignore`
- `scripts/verify_docs_sanity.py`
- `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md`
- `docs/architecture/PROJECTION_LIFECYCLE.md`
- `docs/architecture/IDE_PROJECTIONS.md`

The plan also records review/later generated-output references in `scripts/ide_gen.sh`, `scripts/ide_gen.bat`, `cmake/ide/IdeProjectionManifest.cmake`, `data/release/preset_and_toolchain_registry.json`, and `tools/aide/select_move_wave.py`. Historical and generated audit references are intentionally not rewritten.

## Validation Plan Review

The validation plan includes AIDE doctor, validate, test, selftest, tools validate, roots validate, repo validate, latest commit check, strict repo/root/distribution/component validators, docs sanity, build target boundaries, UI shell purity, ABI boundaries, focused RepoX or equivalent if available, moved JSON parse checks, stale `ide/manifests` reference search, generated-output ignored checks, and git diff checks.

Full CTest, full eval, CMake configure/build, package generation, release generation, and product binary execution are not required for this gate or the planned apply unless the apply task expands beyond the approved manifest move scope.

## Rollback Plan Review

Rollback is sufficient for gate approval. It reverses the three file moves, restores `.gitignore` and architecture/docs sanity references, restores the `ide` exception if tracked files return under `ide`, removes empty `contracts/projections/ide/**` directories created only by apply, and reruns Tier 0 plus strict validator checks.

## Exception Update Plan Review

The exception plan may retire only `exceptions.ide_root`, and only after the later apply task proves:

- the three planned moves and reference rewrites were applied;
- `git ls-files ide` returns no tracked files;
- `.gitignore` no longer exposes `ide/manifests/**` as tracked source;
- strict repo/root validators pass;
- remaining `ide/manifests` references are generated-output, historical, or intentionally preserved.

It does not authorize broader root constitution changes.

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
| `git status --short --branch` | PASS | Started clean on `main...origin/main`. |
| `git fetch --all --prune` | PASS | origin/main remained equal to HEAD. |
| `git rev-parse HEAD` | PASS | `32dc93947661c98935d1308f7144eab5e78984bf`. |
| `git rev-parse origin/main` | PASS | `32dc93947661c98935d1308f7144eab5e78984bf`. |
| `git merge-base --is-ancestor origin/main HEAD` | PASS | origin/main is ancestor of HEAD. |
| `git merge-base --is-ancestor HEAD origin/main` | PASS | HEAD is ancestor of origin/main. |
| Plan JSON/TOML invariant inspection | PASS | Exact three planned moves, `apply_allowed = false`, `approval_status = not_approved`. |
| `git ls-files ide` | PASS | Exactly the three expected tracked manifest files. |
| `git ls-files contracts/projections/ide` | PASS | No tracked target collisions. |
| Target path existence checks | PASS | Planned target files do not exist; target path creation is planned for apply. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | AIDE doctor passed. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | AIDE validate passed. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE test passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | AIDE selftest passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | AIDE tools validate passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | AIDE roots validate passed. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | AIDE repo validate passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest commit message passed policy. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result pass; known fallback TOML warnings. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result pass; known fallback TOML warnings. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result pass; known fallback TOML warning. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result pass; known fallback TOML warning. |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity OK. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | Build boundary checks passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity OK. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundary check OK. |
| `python -m json.tool .aide/reports/MOVE-FAMILY-00B-GATE-readiness.json` | PASS | Gate readiness JSON parsed. |
| `git diff --check` | PASS | No whitespace errors in unstaged diff. |
| `git diff --cached --check` | PASS | No staged diff at report creation time. |

## Known Warnings

- `contracts/projections/ide/**` does not exist yet, but the plan explicitly creates it during apply.
- Historical/audit references to old `ide/manifests/**` paths remain by design.
- Generated-output references to `ide/manifests/*.projection.json` remain review/later items because they are generated projection output, not tracked source metadata.
- Strict validators print known TOML fallback-parser warnings while still passing.
- Full CTest, full eval, CMake configure/build, package/release generation, product binary execution, portable projection regeneration, and internal pilot release regeneration were not run by scope.

## Blockers

None.

## Gate Decision

PASS_WITH_WARNINGS. The plan is exact, scoped to three tracked manifest files, keeps apply disabled during the gate, has reviewable reference rewrite groups, has rollback and validation coverage, has no target collisions, and conditions `ide` exception retirement on `git ls-files ide` becoming empty after apply.

## Authorization

MOVE-FAMILY-00B-APPLY may proceed for the three planned IDE manifest moves only. No other move is authorized.
