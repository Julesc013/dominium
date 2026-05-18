# NAME-00 Next Readiness

Status: `READY_FOR_SEMANTIC_LINT_REPAIR_OR_BATCH_A_REFERENCE_REFINEMENT`

## Readiness

| Area | Ready |
| --- | --- |
| DOE-00 | no |
| feature work | no |
| MOVE-BULK B-G apply | no |
| MOVE-BULK B-G refinement | yes |
| post-restructure full proof | no |

## Recommended Order

1. `POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS`
2. `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`
3. `MOVE-BULK-BG-REFINEMENT-00`
4. `MOVE-BULK-02R` through `MOVE-BULK-07R` only after refined gates
5. `MOVE-BULK-08R-FINAL-EXCEPTION-CLOSURE`
6. `POST-RESTRUCTURE-01-FULL-PROOF`
7. `DOE-00`

## Naming Constraints For Next Cleanup

- Do not route anything to `src/`, `source/`, `code/`, `impl/`, `common/`, `shared/`, or `misc/`.
- Do not apply planned internal renames during MOVE-BULK without a reviewed rename scope.
- Preserve contract, package, profile, bundle, ABI, release, and product identity values.
- Keep unclear identity, ABI, runtime, policy, or language ownership deferred.
