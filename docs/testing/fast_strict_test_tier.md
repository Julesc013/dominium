Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none

# Fast Strict Test Tier

`fast_strict` is Dominium's normal development proof gate after the canonical
repo cleanup. It exists because full CTest is too slow and still carries broad
full-gate debt, but routine work still needs a strict, meaningful proof loop.

## Command

Run from the repository root:

```text
python tools/test/run_fast_strict.py --repo-root .
```

Equivalent explicit form:

```text
python tools/test/run_fast_strict.py --repo-root . --gate fast_strict
```

For full evidence collection during diagnostics:

```text
python tools/test/run_fast_strict.py --repo-root . --gate fast_strict --continue-on-fail
```

## Included Tiers

`fast_strict` runs:

- T0 static format and repo hygiene
- T1 strict repo and contract hygiene
- T2 build and smoke proof

It does not run T3 product/projection proof or T4 full/release/trust proof.
Within T2, the CMake build step uses the verify preset with `ALL_BUILD` so the
normal gate builds once and then runs explicit bounded CTest selections. This
keeps build proof and test proof visible as separate evidence instead of
letting the build preset invoke `verify_fast` and then running CTest again.
T1 also validates the active C17/C++17 language baseline and the macOS 10.9
C++17 restricted library subset.

## Pass Definition

The gate passes only when every required T0, T1, and T2 command passes.

Acceptable warnings are limited to commands explicitly marked optional in
`contracts/testing/test_tiers.contract.toml`. Optional warnings are still
recorded in JSON and Markdown evidence.

Missing required commands fail the gate. Missing optional commands are recorded
as warnings only when the contract says they are optional.

## Evidence

By default the runner writes:

- `.aide/reports/FAST-STRICT-TEST-TIER-01-run.json`
- `.aide/reports/FAST-STRICT-TEST-TIER-01-run.md`

Task-specific runs may write named evidence under `.aide/reports/**`.

## Why Full CTest Is Separate

Full CTest remains important, but it is a release/trust/certification lane. It
is not the everyday edit-loop gate because current evidence shows it is slower
than the normal development budget and still has broad debt outside the
bounded fast/smoke proof surface.

This separation does not hide failures:

- full CTest remains listed in T4
- full CTest remains blocking for full certification
- known full-gate debt is tracked separately
- tests are not deleted or demoted to make `fast_strict` green

## When To Run Release Or Full Gates

Run `release_candidate` before product, projection, release, trust-bearing,
compatibility, or public-surface promotion:

```text
python tools/test/run_fast_strict.py --repo-root . --gate release_candidate
```

`release_candidate` is kept as a compatibility alias. The canonical release
gate command is:

```text
python tools/test/run_fast_strict.py --repo-root . --gate release
```

Run `full` for full certification, large replacement work, broad compatibility
changes, and release/trust closeout:

```text
python tools/test/run_fast_strict.py --repo-root . --gate full
```

## AIDE And Codex Use

Codex and AIDE should treat `fast_strict` as the default proof loop for
Foundation Lock tasks unless the task explicitly requires release or full
certification proof.

## Adding Checks

Add a check to the lowest tier where it is fast, stable, and required for that
tier's purpose. If a check is slow, broad, or currently failing due historical
debt, place it in T3 or T4 and document the debt instead of silently weakening
the normal gate.

Feature work remains bounded until `FOUNDATION-CLOSEOUT-01`. A green
`fast_strict` result enables the next Foundation Lock task; it does not broadly
authorize gameplay, Workbench, renderer, native GUI, worldgen, fabrication, or
civilization implementation.
