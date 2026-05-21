# AIDE Latest Task Packet

## PHASE

foundation-hardening - PORTABILITY-ARCH-POLICY-02

## GOAL

Define, validate, document, and fast-strict integrate Dominium's 64-bit native architecture policy.

## WHY

Dominium mainline full-native products need an explicit architecture law so legacy 32-bit and vintage compatibility lanes do not govern the mainline. Public ABI and persisted formats must remain pointer-width independent.

## CONTEXT_REFS

- `docs/repo/FOUNDATION_LOCK.md`
- `docs/repo/audits/PORTABILITY_ARCH_POLICY_02.md`
- `.aide/reports/PORTABILITY-ARCH-POLICY-02-validation.md`
- `.aide/reports/PORTABILITY-ARCH-POLICY-02-readiness.md`
- `.aide/reports/PORTABILITY-ARCH-POLICY-02-fast-strict.md`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

- `contracts/platform/**`
- `contracts/public_surface/**`
- `contracts/diagnostics/**`
- `contracts/refusal/**`
- `contracts/capability/**`
- `contracts/testing/test_tiers.contract.toml`
- `tools/validators/platform/**`
- `tests/contract/architecture_policy/**`
- `docs/architecture/**`
- `docs/development/**`
- `docs/build/**`
- `docs/release/**`
- `docs/repo/**`
- `.aide/context/**`
- `.aide/reports/**`
- `.aide/queue/current.toml`
- `.aide/ledgers/migration_ledger.jsonl`

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.dominium.local/**`
- build output roots
- Workbench/product feature implementation outside architecture-policy scope

## IMPLEMENTATION

- Added architecture policy contracts, tier registry, pointer-width schema, endian policy, and architecture claim schema.
- Added `tools/validators/platform/check_architecture_policy.py`.
- Added architecture policy fixtures.
- Updated portability rows with architecture tiers, word-size policy, and endian policy.
- Registered public surfaces, diagnostics, refusals, and capabilities.
- Added architecture validator to fast strict.

## VALIDATION

- architecture policy strict/json/fixtures/inventory: PASS.
- portability matrix strict/json/fixtures: PASS.
- dependency-direction strict: PASS, `0` violations, `68` warnings.
- AIDE doctor/validate/test/selftest/tools/roots/repo: PASS after packet repair.
- RepoX STRICT: PASS with stale AuditX warning.
- FAST strict: PASS, `33` commands, `296.553` seconds.
- CMake configure/build and smoke CTest: PASS through FAST strict.
- full CTest: NOT RUN, T4/full-gate debt.

## COMMITS

Create an audit-grade architecture policy commit after final fast strict remains green.

## EVIDENCE

- `docs/repo/audits/PORTABILITY_ARCH_POLICY_02.md`
- `.aide/reports/PORTABILITY-ARCH-POLICY-02-*`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`

## NON_GOALS

- Do not implement `WORKBENCH-VALIDATION-SLICE-01` in this task.
- Do not implement Workbench UI, gameplay, renderer expansion, native GUI, runtime module loading, package/provider runtime, or release publication.
- Do not run full CTest unless a targeted blocker requires it.

## ACCEPTANCE

- Architecture policy is PASS_WITH_WARNINGS.
- Foundation Lock remains PASS_WITH_WARNINGS.
- `WORKBENCH-VALIDATION-SLICE-01` remains authorized as the next narrow governed product slice.
- Broad feature work remains blocked.
- Worktree is clean after commit.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `COMMITS`, `VALIDATION`, `PUSH`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 4218
- approx_tokens: 1055
- budget_status: PASS
- warnings:
  - none
