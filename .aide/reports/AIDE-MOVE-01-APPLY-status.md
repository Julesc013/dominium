# AIDE-MOVE-01-APPLY Status

## Status

- Task ID: AIDE-MOVE-01-APPLY
- Result: PASS_WITH_WARNINGS
- Branch: main
- HEAD before apply: 8e03222fa4ed11ea3cf95429f361507745ea7bb0
- origin/main observed before apply: 8e03222fa4ed11ea3cf95429f361507745ea7bb0
- Sync warning: the prompt expected origin/main at ab7362987bcff405cac69d947efb1950cb2f2295, but local origin/main already pointed at the AIDE-GATE-02 commit. No fetch, pull, rebase, reset, or push was run.

## Move Applied

`ide/README.md` was moved to `docs/architecture/IDE_PROJECTIONS.md` with `git mv`.

## Reference Rewrites Applied

Applied 6 of 6 planned apply-phase rewrites:

- Removed the stale `.gitignore` exception for `!/ide/README.md`.
- Updated `scripts/verify_docs_sanity.py`.
- Updated `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md`.
- Updated the moved document title.
- Updated the moved document self-reference.
- Updated `tools/aide/select_move_wave.py` selection wording.

## Deferred Material

`ide/manifests/**` remains present and untouched.

## Exception Handling

The `ide/` root exception was not retired. `ide/` still remains for `ide/manifests/**` and future generated projection outputs.

## Validation Summary

AIDE doctor, validate, test, selftest, tools validate, roots validate, repo validate, commit check, strict repo/root/distribution/component validators, docs sanity, build boundary, UI shell purity, ABI boundary, stale reference search, and `git diff --check` passed.

## Next Recommendation

`AIDE-GATE-03 - Post-Move Proof and Next Wave Readiness Gate`.
