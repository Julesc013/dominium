# RESTRUCTURE-REPAIR-00 Status

Result: PARTIAL.

Branch: `main`.

Initial HEAD: `0ddc1797c122d720c3cb9363a477c028d8413c49`.

Initial origin/main: `a5e6138fdc44a5231808da43ada1659e97a649dd`.

Sync state: local `main` was ahead of `origin/main`; `origin/main` was an ancestor of local HEAD. No divergence was found.

Safe repairs applied:

- Updated stale AppShell GUI path expectations in scaffold and invariant tests.
- Updated stale client command bridge and action registry paths to `apps/client/core/**`.
- Updated the RepoX run-meta dependency hash test for the current helper signature.
- Fixed ops compatibility JSON smoke output by removing a Python 3.14 `utcnow()` deprecation warning from stdout.
- Updated integration metadata from `app/app_runtime.c` to `runtime/app/app_runtime.c`.
- Removed direct host path literals from TestX fixture sources while keeping the leak fixtures semantically equivalent.
- Updated archive presence contract entries from retired top-level `legacy/` and `tmp/` roots to `archive/legacy/` and `archive/generated/`.
- Updated the focused RepoX archive allowlist to match `archive/legacy/` and `archive/generated/`.
- Added narrow current contract references required by `harden1_docs_contracts` and `scale0_interest_pattern_invariance`.
- Made `slice0_hardcoded_ids` emit deterministic diagnostics on Windows codepages while preserving the failing hardcoded-identifier gate.

Safe repairs not applied:

- No remaining root moves were attempted because Batch B-G ownership and safety gates remain deferred.
- No frozen contract hashes were updated because that is a review-gated contract action.
- No expired overrides were renewed because that would weaken policy without review.
- No determinism replay hashes were accepted or regenerated because replay drift is a semantic blocker.

Current readiness: not ready for DOE-00. Feature implementation remains blocked.
