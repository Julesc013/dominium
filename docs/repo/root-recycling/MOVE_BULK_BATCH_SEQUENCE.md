Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# MOVE-BULK Batch Sequence

## Purpose

This sequence replaces dozens of micro-plans with a small set of gated bulk migration waves. The sequence is still no-apply until a gate authorizes exact scope.

## Recommended Order

1. `MOVE-BULK-00-GATE - Global Bad-Root Migration Gate`
2. `MOVE-BULK-A-APPLY - Apply docs/evidence/archive-only moves`
3. `MOVE-BULK-A-PROOF - Prove Batch A and refresh root exceptions`
4. `MOVE-BULK-B-GATE/APPLY/PROOF - Templates, models, and modding`
5. `MOVE-BULK-C-GATE/APPLY/PROOF - Content identity, packs, profiles, bundles`
6. `MOVE-BULK-D-GATE/APPLY/PROOF - Authority, policy, specs, updates`
7. `MOVE-BULK-E-GATE/APPLY/PROOF - Active tools and shim migrations`
8. `MOVE-BULK-F-GATE/APPLY/PROOF - Runtime, core, control, net`
9. `MOVE-BULK-G-GATE/APPLY/PROOF - Libraries and ABI/build surfaces`
10. `MOVE-BULK-H-CLOSEOUT - Exception, shim, inventory, and full proof closure`

## First Apply Candidate

Batch A is the first candidate because it contains only docs, audit/evidence, historical, generated-retained, and log material under `data/`.

Batch A must still pass a gate before apply. The gate should verify no active source/tool references depend on the old paths selected for the safe subset.

## MOVE-BULK-00-GATE Authorization

MOVE-BULK-00-GATE authorizes:

```text
MOVE-BULK-01-APPLY-DOCS-ARCHIVE
```

Scope is limited to Batch A docs/evidence/archive-only safe-subset handling. Batches B through G remain deferred, and Batch H remains blocked until prior batches apply and prove cleanly.

## Batch Safety Rule

No batch may fail wholesale because one file is unsafe. Apply prompts must apply safe subsets, skip unsafe items, and report skipped paths exactly.

## Closure Rule

Batch H may run only after prior batches finish and must prove:

- `git ls-files <bad-root>` is empty for every retired root.
- layout exceptions are retired or still justified.
- temporary shims have either been retired or are still explicitly allowlisted.
- strict validators, focused/full proof lanes, portable projection proof, product boot proof, and internal pilot release proof meet the required tier.

## MOVE-BULK-01 Outcome

`MOVE-BULK-01-APPLY-DOCS-ARCHIVE` applied only the safe subset of Batch A.

- Applied: 26 files.
- Skipped: 283 files with active/current exact references.
- Reference rewrites: 0.
- Exception retirements: 0.

The next batch remains gated. Do not treat this partial Batch A apply as authorization for Batch B, C, D, E, F, G, or H.

<!-- MOVE-BULK-08-CLOSURE -->

## MOVE-BULK-08 Final Exception Closure

MOVE-BULK-08 records a partial closure snapshot rather than a clean final closeout.

- Remaining tracked bad-root files: 1764.
- Roots still tracked: 23.
- Roots retired or empty: ide.
- Exceptions retired or narrowed by closure: 0.
- New shims created by closure: 0.
- Ready for `POST-RESTRUCTURE-00-FULL-PROOF`: no.
- Recommended next task: `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`, or the next explicit batch gate.

<!-- POST-RESTRUCTURE-00-BLOCKED -->

## POST-RESTRUCTURE-00 Blocked Proof Note

POST-RESTRUCTURE-00 did not run the full proof chain because MOVE-BULK-08 closure says full proof is not ready.

- Remaining former bad-root files: 1764.
- Deferred batches: B-G.
- Blocked batch: H.
- Ready for DOE-00: no.
- Next recommended task: `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`.
