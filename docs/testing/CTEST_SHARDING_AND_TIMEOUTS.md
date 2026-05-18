Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# CTest Sharding And Timeouts

## Label Policy

| Label | Meaning | Local expectation |
| --- | --- | --- |
| `smoke` | Product/workflow smoke coverage | Green under 300 seconds |
| `fast` | Fast CTest lane, currently the smoke set | Green under 300 seconds |
| `audit` | AuditX CTest shard | Green under 1200 seconds |
| `auditx` | Compatibility label for the AuditX shard | Green under 1200 seconds |
| `slow` | Bounded slow tests | Not part of normal fast feedback |
| `nightly` | Slow/nightly promotion lane | Not part of normal fast feedback |
| `portability` | Broad portable TestX coverage | Component shard, not fast by default |
| `buildmeta` | Build/release metadata tests | Component shard |
| `testx` | Default TestX-owned CTest label | Broad selector only |

`full` is not a CTest label. Full means the unfiltered `verify` CTest preset.

## Commands

Focused RepoX:

```powershell
ctest --preset verify -R inv_repox_rules --output-on-failure --timeout 300
```

Smoke:

```powershell
ctest --preset verify -L smoke --output-on-failure --timeout 300
```

Fast:

```powershell
ctest --preset verify -L fast --output-on-failure --timeout 300
```

Tooling without the heavy AuditX shard:

```powershell
python scripts/test_tier.py --tier component-tools
```

AuditX:

```powershell
ctest --preset verify -L audit --output-on-failure --timeout 1200
```

Slow/nightly:

```powershell
ctest --preset verify -L slow --output-on-failure --timeout 1200
ctest --preset verify -L nightly --output-on-failure --timeout 1200
```

Full promotion:

```powershell
ctest --preset verify --output-on-failure
```

Full promotion is not expected to be green until `slice0_hardcoded_ids` and `slice1_hardcoded_constants` are remediated.

## Timeout Policy

- 300 seconds is the local limit for smoke, fast, and focused feedback lanes.
- 1200 seconds is the current bounded timeout for AuditX slow/nightly CTest shards.
- A slow timeout is acceptable only when the test remains mandatory in an explicit slow shard.
- A timeout may not be used to convert a real failure into a warning.
- Full CTest may be run locally or in CI/nightly, but current results must be interpreted with the known semantic lint blockers.

## Interpretation

A non-run full CTest is acceptable only when the sharded evidence is current and the reason full is not green is named. After TEST-PERF-01, that reason is semantic lint debt, not AuditX wall-time opacity.
