Status: DRAFT
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

## Batch Safety Rule

No batch may fail wholesale because one file is unsafe. Apply prompts must apply safe subsets, skip unsafe items, and report skipped paths exactly.

## Closure Rule

Batch H may run only after prior batches finish and must prove:

- `git ls-files <bad-root>` is empty for every retired root.
- layout exceptions are retired or still justified.
- temporary shims have either been retired or are still explicitly allowlisted.
- strict validators, focused/full proof lanes, portable projection proof, product boot proof, and internal pilot release proof meet the required tier.
