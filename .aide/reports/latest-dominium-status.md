# Latest Dominium Status

Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

## Current Position

Focused RepoX is clean after the residual closeout remediation. Direct RepoX and canonical CTest focused `inv_repox_rules` both pass with zero recorded RepoX warnings and zero RepoX failures.

Native product command-surface smoke was run locally against `out/build/vs2026/verify/bin/` for `setup.exe`, `launcher.exe`, `client.exe`, `server.exe`, and `tools.exe`. Each returned exit code 0 for `--help`, `--version`, `--status`, and `--smoke`.

Canonical CTest discovery reports 493 tests, and `ctest --preset verify -L smoke --output-on-failure --timeout 300` passes 57/57. The full promotion build/test lane still needs wall-time partitioning: a prior `cmake --build --preset verify` run timed out during verification after producing the native binaries.

A local ignored portable projection root has been generated and validated:

```text
.dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium
```

`tools/validators/check_portable_projection.py` reports `proof_status: proven` with no blockers. The generated projection `bin/` contains the five native product binaries and portable wrappers.

RELEASE-00 internal pilot preparation may proceed with warnings. Public package/release generation, installer generation, and full promotion CTest remain not run.

## Next Recommended Task

`RELEASE-00 - Internal Pilot Release 0`, with `TEST-PERF-01 - CTest Sharding and Slow-Test Baseline` as the parallel validation-speed follow-up.
