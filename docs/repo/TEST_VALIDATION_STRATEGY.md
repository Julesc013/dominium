Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# Test Validation Strategy

Dominium validation is a tiered evidence ladder. Normal development should not use full CTest as the default feedback loop.

## Tiers

| Tier | Purpose | Typical Command |
| --- | --- | --- |
| T0 | Fast AIDE and repository sanity checks | `python scripts/test_tier.py --tier t0` |
| Focused | A known blocker or narrow invariant | `python scripts/test_tier.py --tier focused-repox` |
| Component | Tests related to a touched subsystem | `python scripts/test_impacted.py --from HEAD~1 --run` |
| Timing sample | Small wall-time evidence sample | `python scripts/test_tier.py --tier timing-sample` |
| Full promotion | Complete canonical CTest lane | `python scripts/test_tier.py --tier full-promotion` |

Full promotion remains required before merge, release, or product-proof promotion. It is not the default post-change gate.

## Impact Selection

`tests/validation_tiers.json` maps changed paths to validation tiers. The selector is:

```text
python scripts/test_impacted.py --from HEAD~1
```

Use `--include-worktree` while iterating locally. Use `--run` only when the selected tiers are appropriate for the current task scope.

## CTest Discovery

Canonical CTest discovery requires the verify build tree to be configured:

```text
cmake --preset verify
ctest --preset verify -N
```

TEST-PERF-00 confirmed that discovery can fall to zero when the build tree is stale or missing. After a configure refresh, canonical `verify` discovers 493 tests locally.

## CTest Labels

`dom_add_testx` now writes CTest labels directly when tests are registered. After reconfigure, `ctest --preset verify -N -L smoke` selects the smoke subset.

## Wall-Time Policy

- T0 and impacted tiers are normal post-task validation.
- Component tiers are used for larger or subsystem-specific work.
- Full CTest is retained as a promotion gate.
- Slow tests are classified with timing evidence, not deleted or skipped.
- Product proof, package proof, and release proof remain separate gates.
