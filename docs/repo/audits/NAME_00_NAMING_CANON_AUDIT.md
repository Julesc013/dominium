Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none
Stability: provisional
Task: NAME-00

# NAME-00 Naming Canon Audit

## Result

Status: PASS with transitional warnings.

NAME-00 adds naming law only. It does not move files, delete files, rename files, rewrite imports, rewrite references, create shims, apply move maps, apply salvage maps, retire exceptions, mutate runtime behavior, mutate content identity, or alter semantic contract IDs.

## Authority Read

Current naming and layout authority is derived from:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `AGENTS.md`
- `contracts/repo/layout.contract.toml`
- `contracts/repo/root_allowlist.toml`
- `contracts/repo/layout_exceptions.toml`
- `contracts/distribution/layout.contract.toml`
- `contracts/release/component_matrix.contract.toml`
- `docs/repo/REPO_LAYOUT_TARGET.md`
- `docs/repo/OWNERSHIP_RULES.md`
- `docs/repo/DOMAIN_SPLIT_RULES.md`
- `docs/repo/DISTRIBUTION_LAYOUT_CANON.md`
- `docs/release/COMPONENT_MATRIX.md`
- `docs/repo/root-recycling/ROOT_RECYCLING_RUNBOOK.md`
- `docs/repo/root-recycling/MOVE_BULK_BATCH_SEQUENCE.md`

`docs/restructure/FUTURE_LAYOUT_PROPOSAL.md` is retained as historical planning input. Its `/src` proposal is explicitly superseded by the post-CONVERGE source-root model.

## Deliverables

- `contracts/repo/naming.contract.toml`
- `contracts/repo/naming.schema.json`
- `docs/repo/directory_naming.md`
- `docs/repo/file_naming.md`
- `docs/repo/no_src_source_policy.md`
- `docs/repo/module_layout.md`
- `docs/repo/language_ownership.md`
- `tools/validators/repo/check_no_src_source_dirs.py`
- `tools/validators/repo/check_path_terms.py`
- `tools/validators/repo/check_directory_naming.py`
- `tools/validators/repo/check_file_naming.py`
- `tools/validators/repo/README.md`
- `.aide/reports/NAME-00-*`

## Current Conflict Classification

The known current conflict classes are:

- historical `src`, `source`, and `legacy` pockets under `archive/`;
- transitional `packs/source/**` identity debt under an active bad-root exception;
- active top-level bad roots still excepted by `contracts/repo/layout_exceptions.toml`;
- planned internal rename targets such as `runtime/appshell`, `game/domains`, and `contracts/schemas`;
- Python placement under roots whose final language law is stricter than current implementation state.

These are not immediate NAME-00 blockers because this task is no-apply and the conflicts already existed under layout exceptions or historical archive classification.

## Future MOVE-BULK Effect

Future MOVE-BULK B-G refinement must consume `contracts/repo/naming.contract.toml` before selecting targets.

If a path can safely move, the target must use ownership nouns and the singular/plural grammar. If a path has unclear identity, ABI, runtime, policy, release, or language meaning, it remains deferred.

## Contract And Schema Impact

New contract surface: `dominium.repo.naming.v1`.

No existing semantic contract IDs were changed.

## Redo Snapshot - 2026-05-18

This redo refreshes NAME-00 against current `main` after TEST-PERF-01, semantic lint repair, and MOVE-SCRIPT-00.

- HEAD: `148a9adf95bb678da16784434221c568f7bb96cb`.
- `origin/main`: `148a9adf95bb678da16784434221c568f7bb96cb`.
- Prior NAME-00 commit: `8d7c7dd8e`.
- Current bad-root router inventory: 1,765 tracked files under 23 former bad roots.
- MOVE-SCRIPT-00 dry-run result: 1,593 route candidates, 172 skipped/deferred files, 0 target collisions.
- Files moved by this redo: 0.
- Renames, import rewrites, reference rewrites, shims, exception retirements, generated release outputs: 0.

The increase from the original NAME-00/closure count of 1,764 to the current router inventory of 1,765 is recorded as current evidence, not a naming-law change.

## Primary Questions Answered

1. Current naming authority is the post-CONVERGE root/layout contract stack plus `contracts/repo/naming.contract.toml`; older layout proposals are historical unless explicitly promoted by current authority.
2. Old docs still mention `/src`, `source`, and old layout names, but those mentions are historical, archive, audit, or superseded planning material. The old `/src` proposal is not active source layout authority.
3. Current tracked path conflicts are warning-class and recorded in `.aide/reports/NAME-00-path-conflicts.*`.
4. Immediate NAME-00 blockers: none.
5. Allowed transitional debt: active layout exceptions for the 23 former bad roots, archive/history terms, planned internal rename paths, `packs/source/**` content-identity debt, and existing language-placement debt.
6. Future MOVE-BULK refinement should use ownership targets from `contracts/repo/naming.contract.toml` and MOVE-SCRIPT-00 route evidence; unclear identity, ABI, runtime, authority, policy, import, or naming-risk files remain deferred.
7. Existing strict repo/root/distribution/component validators remain blocking. NAME-00 validators enforce no new unexcepted forbidden roots while classifying existing debt.
8. Warning-only initial validators: path terms, directory case, file case, planned internal renames, and current language placement.
9. Future planned migrations only: `runtime/appshell -> runtime/shell`, `game/domains -> game/domain`, `content/domain-data -> content/domains`, and singular contract category targets.
10. The next route/bulk cleanup prompt must consume both the naming contract and `MOVE-SCRIPT-00` dry-run ledgers before any B-G apply authorization.

## Current Conflict Counts

Current NAME-00 validator summaries:

| Surface | Findings | Warnings | Blockers | Notes |
| --- | ---: | ---: | ---: | --- |
| no `src`/`source`/`sources` dirs | 106 | 13 | 0 | `packs/source/**` warnings plus archive/history info |
| forbidden path terms | 1,450 | 78 | 0 | most findings are archive/history info |
| directory naming | 418 | 39 | 0 | mostly archive/evidence info; uppercase/hyphen warnings remain |
| file naming | 5,361 | 4,307 | 0 | mostly existing uppercase docs and historical/evidence files |
| language ownership | 4 summarized classes | 4 | 0 | existing Python placement debt and bad-root Python debt |

No current conflict is accepted as final architecture. They are classified so later cleanup can distinguish real blockers from historical or transitional material.

## Immediate Blocker Decision

NAME-00 remains `PASS_WITH_WARNINGS`.

The warnings do not authorize feature work, DOE-00, or B-G apply work. They only prove that naming law is now explicit and machine-readable enough for the next refinement gate.

## MOVE-BULK B-G Impact

MOVE-BULK B-G refinement must now combine:

- `contracts/repo/naming.contract.toml`;
- `docs/repo/directory_naming.md`;
- `docs/repo/file_naming.md`;
- `docs/repo/language_ownership.md`;
- `tools/migration/bad_root_routing_rules.json`;
- `.aide/reports/MOVE-SCRIPT-00-routing-preview.json`;
- `.aide/reports/MOVE-SCRIPT-00-skipped-ledger.json`;
- `.aide/reports/MOVE-SCRIPT-00-batch-plan.json`.

The refinement gate may authorize only proven safe subsets. It must not apply planned internal renames as a side effect, must not route to `src`/`source`/generic buckets, and must keep skipped/deferred files explicit.

## Redo Validation

This redo validation reuses and refreshes the current NAME-00 checks:

- AIDE doctor/validate/test/selftest/tools/roots/repo: pass, with the existing review-packet missing-reference warning on `validate`.
- strict repo/root/distribution/component validators: pass.
- NAME-00 validators: pass with warnings and zero blockers.
- supplemental docs/build/UI/ABI checks: pass.
- Python compile for the four NAME-00 validators: pass.
- JSON parse for NAME-00 schema/report JSON: pass.
- `git diff --check`: pass.

Full CTest, full eval, CMake configure/build, product boot, package generation, release generation, tags, and GitHub release operations were not run by scope.

## Next Task

The current downstream task is:

```text
MOVE-BULK-BG-REFINEMENT-00 - Re-Gate Deferred B-G Cleanup
```

DOE-00 and feature work remain blocked until the remaining root debt is refined/applied/proven and post-restructure proof is rerun.
