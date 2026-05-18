Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none
Plan Status: DRAFT
Approval Status: not_approved
Apply Allowed: false

# MOVE-FAMILY-00B IDE Manifest Contract Projection Plan

## Status

- Task: `MOVE-FAMILY-00B-PLAN`
- Result: `PASS_WITH_WARNINGS`
- Baseline: `BASELINE-00`
- Prior task: `MOVE-FAMILY-00-REFINE-ACTIVE-MODULE-BOUNDARIES`
- Ready for `MOVE-FAMILY-00B-GATE`: true
- Apply authorized: false

## Scope

This plan covers only tracked source metadata under:

```text
ide/manifests/**
```

It does not move files, delete files, rename files, rewrite references, create shims, apply move maps, apply salvage maps, or retire exceptions.

## Baseline

BASELINE-00 freezes RELEASE-00 as the structural regression baseline. Any later apply task must preserve the baseline validation posture and prove generated release/projection/build/local outputs remain ignored and uncommitted.

## Current IDE Manifests

| Path | Format | Role |
| --- | --- | --- |
| `ide/manifests/projection_manifest.schema.json` | JSON Schema | source schema for IDE projection manifests |
| `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json` | JSON | authored Linux clang example manifest |
| `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json` | JSON | authored Win9x VC6 legacy example manifest |

## Ownership Analysis

The tracked schema and examples are projection contract metadata. They are not generated release proof, generated projection proof, or human architecture prose.

The correct planned owner is:

```text
contracts/projection/ide/**
```

This target does not exist yet. A later apply task should introduce it as a scoped contract/projection ownership path under the existing `contracts/` root. It should not create a new top-level root.

## Planned Moves

| Source | Target |
| --- | --- |
| `ide/manifests/projection_manifest.schema.json` | `contracts/projection/ide/projection_manifest.schema.json` |
| `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json` | `contracts/projection/ide/examples/example_linux_clang_modern_client_gui.projection.json` |
| `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json` | `contracts/projection/ide/examples/example_win_vc6_win9x_client_gui.projection.json` |

## Deferred Material

No tracked `ide/manifests/**` source file is deferred by this plan.

Generated manifests may still be emitted under:

```text
ide/manifests/<projection_id>.projection.json
```

Those files are generated projection output and must remain ignored and uncommitted.

## Reference Rewrite Plan

The apply task should update current source references for:

- `.gitignore`
- `scripts/verify_docs_sanity.py`
- `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md`
- `docs/architecture/PROJECTION_LIFECYCLE.md`
- `docs/architecture/IDE_PROJECTIONS.md`

The apply task should not rewrite historical audit evidence. CMake and script references that write generated manifests under `ide/manifests/*.projection.json` may remain if they are classified as generated-output references.

## Validation Plan

The apply task must run:

- AIDE doctor/validate/test/selftest/tools/roots/repo and latest commit check.
- Strict repo/root/distribution/component validators.
- Docs sanity.
- Build target boundaries.
- UI shell purity.
- ABI boundaries.
- Focused RepoX or canonical focused CTest RepoX if available.
- JSON parse for the moved schema and examples.
- Schema or structural validation of examples.
- `git ls-files ide` proof.
- stale-reference scan for `ide/manifests` and `projection_manifest.schema.json`.
- generated-output ignored/staging checks.
- git diff checks.

Full CTest, full eval, CMake configure/build, product binary execution, package/release generation, portable projection regeneration, and internal pilot release regeneration are not required unless the apply task changes generated output producers or release/projection inputs beyond this plan.

## Rollback Plan

Rollback is:

1. Move the three files back to their current `ide/manifests/**` paths.
2. Restore `.gitignore`, docs sanity, and architecture references.
3. Restore the active `ide` layout exception if it was retired.
4. Remove empty `contracts/projection/ide/**` directories if created only by the apply task.
5. Rerun Tier 0 validation and generated-output checks.

## Exception Update Plan

If the later apply task moves all three tracked files and `git ls-files ide` is empty, the `ide` source-layout exception can be retired after validation. Ignored generated `ide/**` output may still exist locally and does not by itself require a source exception.

Do not remove `ide` from root constitution transitional-root history in the same apply unless that broader contract update is explicitly reviewed.

## Readiness For MOVE-FAMILY-00B-GATE

Ready for gate review.

The gate must confirm:

- `contracts/projection/ide/**` is acceptable as a scoped contract ownership path;
- the generated-output path distinction is acceptable;
- the five apply-phase reference rewrite groups are sufficient;
- exception retirement is conditional on `git ls-files ide` becoming empty.

## No Moves/Deletes/Renames Confirmation

MOVE-FAMILY-00B-PLAN made no source-root moves, deletes, renames, reference rewrites, active aliases, compatibility shims, salvage-map applications, move-map applications, or exception retirements.

## MOVE-FAMILY-00B-GATE Note

MOVE-FAMILY-00B-GATE passed with warnings and authorizes only `MOVE-FAMILY-00B-APPLY` for the three planned tracked IDE manifest moves:

- `ide/manifests/projection_manifest.schema.json` -> `contracts/projection/ide/projection_manifest.schema.json`
- `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json` -> `contracts/projection/ide/examples/example_linux_clang_modern_client_gui.projection.json`
- `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json` -> `contracts/projection/ide/examples/example_win_vc6_win9x_client_gui.projection.json`

No other move wave is authorized. The `ide` layout exception may retire only after the apply task proves `git ls-files ide` is empty and validators pass.

## MOVE-FAMILY-00B-APPLY Result

MOVE-FAMILY-00B-APPLY consumed the gate authorization and applied the three planned moves to `contracts/projection/ide/**`.

- Applied moves: 3.
- Applied rewrite groups: 5.
- `git ls-files ide`: empty.
- `ide` source-layout exception: retired after strict validators passed.
- Generated `ide/manifests/*.projection.json` output remains an ignored local-output concern if regenerated later.
- Next task: `MOVE-FAMILY-00B-PROOF - IDE Root Retirement Proof`.

## MOVE-FAMILY-00B-PROOF Result

MOVE-FAMILY-00B-PROOF proved that the plan and apply achieved tracked `ide/` retirement without baseline regression.

- `git ls-files ide`: empty.
- Filesystem `ide/`: absent.
- `ide_root` exception: retired.
- Active stale references to old tracked schema/example source paths: none.
- Remaining old-path references are historical, planning, audit, AIDE evidence, root-recycling history, or generated-output references.
- Next recommended task: `MOVE-FAMILY-00C-PLAN - Active Validation/Meta/Governance Tool Namespace Plan`.
