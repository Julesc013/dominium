Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# BASELINE-00 Release Structural Regression Baseline

## Status

- Result: PASS_WITH_WARNINGS
- Branch: `main`
- HEAD before: `0b631fc5f09f3d927a54e8312976b926d111a72e`
- HEAD after evidence write before commit: `0b631fc5f09f3d927a54e8312976b926d111a72e`
- origin/main: `0b631fc5f09f3d927a54e8312976b926d111a72e`
- Worktree before: clean except ignored `.aide.local/` and `.dominium.local/`
- Worktree after: scoped baseline docs, reports, context, and ledger changes

## Scope

BASELINE-00 froze RELEASE-00 as the structural regression baseline for MOVE-FAMILY cleanup waves. It did not move files, delete files, rename files, rewrite references, apply move maps, apply salvage maps, create active aliases, retire layout exceptions, publish release artifacts, create tags, create installers, upload artifacts, commit generated output, or change product/runtime/source behavior.

## RELEASE-00 Inputs

RELEASE-00 staged and validated a local ignored internal pilot release proof root:

```text
.dominium.local/releases/internal-pilot-0
```

The release consumes the portable projection input:

```text
.dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium
```

The proof root includes required release and projection manifests, provenance, `manifest/checksums.sha256` with 4718 entries, proof reports, warning ledger, runbook, rollback notes, and native product binaries for setup, launcher, client, server, and tools.

The strict internal pilot validator passed in RELEASE-00 evidence and is rerun by BASELINE-00 when the local release root exists.

## Baseline Commands

Future MOVE-FAMILY tasks must use the command tiers recorded in:

- `docs/repo/STRUCTURAL_REGRESSION_BASELINE.md`
- `docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md`
- `.aide/reports/BASELINE-00-required-regression-commands.md`
- `.aide/reports/BASELINE-00-structural-regression-baseline.json`

## Local Generated Output Status

| Root | Present | Ignored | Tracked |
| --- | --- | --- | --- |
| `.dominium.local/releases/internal-pilot-0` | yes | yes, `.gitignore:41:/.dominium.local/` | no |
| `.dominium.local/projections/post-converge-12/` | yes | yes, `.gitignore:41:/.dominium.local/` | no |
| `.dominium.local/build/` | yes | yes, `.gitignore:41:/.dominium.local/` | no |
| `.aide.local/` | yes | yes, `.gitignore:268:.aide.local/` | no |

## Known Warnings

- Full promotion CTest was not run.
- Full eval was not run.
- No public release, GitHub release, tag, upload, installer, package publication, or generated package output was created.
- A prior full `cmake --build --preset verify` verification phase timed out after producing native binaries.
- Generated release/projection/build/AIDE-local outputs remain local ignored evidence and must not be committed.
- Release staging manifest provenance records stager-time commits earlier than the BASELINE-00 freeze HEAD; this is documented and expected.

## Blocking Rules

Future move-family apply/proof work blocks on any unclassified failure of its required tier, any generated output committed or staged, any unauthorized root move/delete/rename/alias, any missing required release/projection proof when required by risk class, any new top-level root without authority, or any worsening of known warnings without explicit disposition.

## Next Task

```text
MOVE-FAMILY-00-PLAN - Governance, Meta, Performance, Validation, and IDE Cleanup Plan
```
