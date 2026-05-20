# AIDE Latest Task Packet

## Phase

foundation-lock

## Goal

`FAST-STRICT-TEST-TIER-01`

Define Dominium's normal fast strict development proof gate and keep full CTest
as separate T4 release/full-certification proof.

## Relevant Invariants

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- `docs/planning/GATES_AND_PROOFS.md`

## Allowed Paths

- `contracts/testing/**`
- `docs/testing/**`
- `tools/test/**`
- `tools/validators/testing/**`
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/audits/**`
- narrow status notes in `docs/repo/POST_CONVERGE_NEXT_STEPS.md`,
  `docs/repo/POST_RESTRUCTURE_PROOF.md`, and
  `docs/repo/RESTRUCTURE_REPAIR_STATUS.md`

## Deliverables

- `contracts/testing/test_tiers.contract.toml`
- `contracts/testing/test_tiers.schema.json`
- `tools/test/run_fast_strict.py`
- `tools/validators/testing/check_test_tiers.py`
- `docs/testing/fast_strict_test_tier.md`
- `docs/testing/test_tier_policy.md`
- `.aide/reports/FAST-STRICT-TEST-TIER-01-*`
- `docs/repo/audits/FAST_STRICT_TEST_TIER_01.md`

## Normal Gate

Run:

```text
python tools/test/run_fast_strict.py --repo-root .
```

The normal gate is `fast_strict` = T0 + T1 + T2. It excludes T3
product/projection proof and T4 full/release proof unless a later task selects
them explicitly.

## Validation

- `python -m py_compile tools/test/run_fast_strict.py tools/validators/testing/check_test_tiers.py`
- `python tools/validators/testing/check_test_tiers.py --repo-root . --strict`
- `python tools/validators/testing/check_test_tiers.py --repo-root . --json`
- `python tools/test/run_fast_strict.py --repo-root . --list`
- `python tools/test/run_fast_strict.py --repo-root . --dry-run`
- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/FAST-STRICT-TEST-TIER-01-run.json --md-out .aide/reports/FAST-STRICT-TEST-TIER-01-run.md`
- `git diff --check`

## Current Result

`PASS_WITH_WARNINGS`: the normal fast strict gate passed 30/30 commands in
332.828 seconds. Full CTest was not rerun and remains T4 known debt, with the
previous recorded result of 440/503 passed, 63 failed, and about 3227.41 seconds.

## Non-Goals

- No gameplay, Workbench, renderer, platform, native GUI, worldgen, package
  format, provider, public-surface registry, or release artifact work.
- No deletion or weakening of existing tests.
- No false claim that full CTest is green.

## Next

`PUBLIC-SURFACE-REGISTRY-01`
