Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# AIDE-MOVE-01 First Low-Risk Move Plan

## Status

- Status: draft
- Approval status: not_approved
- Apply allowed: false
- Candidate selected: yes

## Scope

This task plans the first low-risk AIDE move wave. It does not move files, delete files, rename files, rewrite references, approve maps, apply maps, create aliases, or retire exceptions.

## Candidate Selected

`ide/README.md` is selected as the first move candidate. The target home is `docs/architecture/IDE_PROJECTIONS.md`.

## Why This Candidate

AIDE-ROOT-06 selected the `ide` root as the lowest-risk first move candidate. AIDE-MOVE-01-PLAN narrows that candidate to one documentation file because `ide/manifests/**` is authoritative machine-readable projection metadata with active script, CMake, release, and architecture references.

## Files/Subtrees Planned

| Source | Target | Action | Risk |
| --- | --- | --- | --- |
| `ide/README.md` | `docs/architecture/IDE_PROJECTIONS.md` | move | low |

## Target Homes

The target path is under existing architecture documentation. The path does not currently exist, so no collision is expected.

## Reference Rewrite Plan

Apply-phase rewrites are planned for:

- `.gitignore`
- `scripts/verify_docs_sanity.py`
- `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md`
- the moved document content
- `tools/aide/select_move_wave.py`

Generated architecture registries and historical audit/AIDE evidence require review or preservation, not blind rewriting.

## Validation Plan

Tier 0 validation is required before and after apply: AIDE doctor/validate/test/selftest, tools/roots/repo validate, strict repo/root/distribution/component validators, docs sanity, build target boundaries, UI shell purity, ABI boundaries, and git diff checks.

## Rollback Plan

Rollback reverses the move, restores apply-phase reference rewrites, and reruns Tier 0 validation. No shim is planned.

## Exception Update Plan

The `ide/README.md` gitignore exception can be narrowed after apply. The `ide/` root exception remains because `ide/manifests/**` and generated projection outputs remain in place. No exception retirement is planned.

## Blockers

- AIDE-GATE-02 has not approved apply readiness.
- No approved move map exists.
- No approved salvage map exists.
- Binding authority transfer for the README requires gate review.

## No Moves/Deletes/Renames Confirmation

No moves, deletes, renames, reference rewrites, path aliases, shims, salvage maps, move maps, or exception updates were applied by this task.

## Next Task

`AIDE-GATE-02 - Move Plan Apply Readiness Gate`.
