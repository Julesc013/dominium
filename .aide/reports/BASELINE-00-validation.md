# BASELINE-00 Validation

Status: DERIVED
Last Reviewed: 2026-05-17

## Intake And Sync

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | PASS | Started on `main`; clean before AIDE task-packet regeneration except ignored local roots. |
| `git remote -v` | PASS | `origin` points at `https://github.com/Julesc013/dominium.git`. |
| `git fetch --all --prune` | PASS | Remote refs fetched. |
| `git rev-parse HEAD` | PASS | `0b631fc5f09f3d927a54e8312976b926d111a72e`. |
| `git rev-parse origin/main` | PASS | `0b631fc5f09f3d927a54e8312976b926d111a72e`. |
| `git log -3 --oneline` | PASS | Latest commits include `0b631fc5`, `ad8397221`, `c7d0a1a1`. |
| `git merge-base --is-ancestor origin/main HEAD` | PASS | `origin/main` is ancestor of HEAD. |
| `git merge-base --is-ancestor HEAD origin/main` | PASS | HEAD is ancestor of `origin/main`; refs equal. |

## Doctrine And Proof Intake

| Input | Result | Notes |
| --- | --- | --- |
| Canon/governance packet | PASS | Consulted constitution, glossary, authority, snapshot, merged state, gates, extend-not-replace, semantic ownership, planning, and reality/planning registry surfaces. |
| RELEASE-00 proof docs | PASS | RELEASE-00 result is `PASS_WITH_WARNINGS`; no blockers remain. |
| POST-CONVERGE proof docs | PASS | Native, product boot, and portable projection closeout updates support RELEASE-00 proof with warnings. |
| Current warning disposition | PASS | Operational warnings remain recorded. |

## Generated Output Checks

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --ignored .dominium.local .aide.local` | PASS | `.dominium.local/` and `.aide.local/` are ignored. |
| `git check-ignore -v .dominium.local/releases/internal-pilot-0` | PASS | Ignored by `.gitignore:41:/.dominium.local/`. |
| `git check-ignore -v .dominium.local/projections/post-converge-12` | PASS | Ignored by `.gitignore:41:/.dominium.local/`. |
| `git check-ignore -v .aide.local` | PASS | Ignored by `.gitignore:268:.aide.local/`. |
| `git ls-files .dominium.local .aide.local` | PASS | No tracked paths. |
| Release root inventory | PASS | 4719 files; 4718 checksum entries; required manifests, proof reports, docs, and binaries present. |

## Validation Sweep

| Command | Result | Notes |
| --- | --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | First post-edit run failed because the review packet was missing required section headers; restored the headers and reran successfully. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | First post-edit run found the same review-packet section issue; rerun passed after the fix. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | Internal AIDE test set passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | Internal AIDE selftest set passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | Tool inventory/wrapping validation passed; no provider/model calls, network calls, unknown tool execution, deletion, rename, or migration. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | Root recycling validation passed; file moves, deletes, and reference rewrites are false. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | Repo intelligence validation passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest pre-existing commit message passed policy before the BASELINE-00 commit. |
| `py -3 .aide/scripts/aide_lite.py commit check --message <BASELINE-00 message>` | PASS | Commit message validated after correcting changelog category prefixes to the required `Added:`/`Changed:` form. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS | Strict pass with expected fallback TOML parser warnings and existing exceptions. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS | Strict pass with expected fallback TOML parser warnings and existing exceptions. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS | Strict pass; missing roots/projections none; warnings none. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS | Strict pass; missing sections/statuses/evidence none; warnings none. |
| `python tools/validators/check_internal_pilot_release.py --repo-root . --release-root .dominium.local/releases/internal-pilot-0 --strict` | PASS | Internal pilot validation passed; 4718 checksum entries. |
| `python tools/validators/check_portable_projection.py --repo-root . --projection-root .dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium --strict` | PASS | Portable projection audit reports `proof_status: proven`; blockers none. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` | PASS | 1/1 passed; real time 234.15 seconds. |
| `ctest --preset verify -L smoke --output-on-failure --timeout 300` | PASS | 57/57 passed; real time 60.33 seconds. |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity OK. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | Build boundary checks passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity OK. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundary check OK. |
| `python -m json.tool` on BASELINE-00 and RELEASE-00 JSON reports | PASS | JSON parsed. |
| JSONL parse for `.aide/ledgers/migration_ledger.jsonl` | PASS | Every ledger line parsed with `ConvertFrom-Json`. |
| `git status --short --ignored .dominium.local .aide.local` | PASS | `.aide.local/` and `.dominium.local/` remain ignored. |
| `git ls-files .dominium.local .aide.local` | PASS | No generated/local paths are tracked. |
| `git diff --check` | PASS | No whitespace errors. |
| `git diff --cached --check` | PASS | No staged whitespace errors before commit. |
| staged file review | PASS | Staged files are limited to BASELINE-00 docs, AIDE reports/context/ledger, release status docs, and root-recycling docs. |

## Side Effects Reverted

`py -3 .aide/scripts/aide_lite.py roots validate` refreshed `tools/migration/root_inventory.json` and `tools/migration/root_move_map.json` timestamps/head fields as a validation side effect. Those paths are outside BASELINE-00 write scope, and the move-map surface must not be changed by this task, so the side-effect diff was reverted before staging.

## Not Run

- Full CTest was not run.
- Full eval was not run.
- Public package generation, release publication, tag creation, upload, installer build, product gameplay scenarios, and move/apply commands were not run.
