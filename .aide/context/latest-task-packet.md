# AIDE Latest Task Packet

## PHASE

Foundation Lock - FOUNDATION-CLOSEOUT-01

## GOAL

Verify the Foundation Lock governance spine and decide whether Dominium can proceed to `WORKBENCH-VALIDATION-SLICE-01`.

## WHY

Dominium must not start product work until the Foundation contracts, validators, fast strict proof, repo layout checks, diagnostics, artifacts, capability/refusal, provider, module, replacement, versioning, trust, and portability layers are present and validated.

## CONTEXT_REFS

- `AGENTS.md`
- `docs/repo/FOUNDATION_LOCK.md`
- `.aide/reports/FOUNDATION-CLOSEOUT-01-foundation-matrix.md`
- `.aide/reports/FOUNDATION-CLOSEOUT-01-validation.md`
- `.aide/reports/FOUNDATION-CLOSEOUT-01-fast-strict.md`
- `.aide/reports/FOUNDATION-CLOSEOUT-01-blockers.md`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/FOUNDATION_LOCK.md`
- `docs/repo/audits/**`
- `docs/repo/POST_CONVERGE_NEXT_STEPS.md`
- `docs/repo/POST_RESTRUCTURE_PROOF.md`
- `docs/repo/RESTRUCTURE_REPAIR_STATUS.md`
- narrow validator/doc repairs required to make closeout evidence truthful

## FORBIDDEN_PATHS

- `.git/**`
- `.aide.local/**`
- `.dominium.local/**`
- generated build/projection/release outputs
- Workbench UI, runtime module loading, provider runtime, package runtime, gameplay, renderer, native GUI, release publication, broad rewrites, or new governance subsystems.

## IMPLEMENTATION

- Verified local `main` was clean and aligned with `origin/main`.
- Read the AGENTS/canon/planning doctrine packet before substantive work.
- Ran required Foundation validators and fixtures.
- Repaired the prior portability audit header so RepoX can parse it lawfully.
- Recorded Foundation Lock as blocked by active dependency-direction violations.

## VALIDATION

- PASS: AIDE doctor/validate preflight.
- PASS: required Foundation files are present.
- PASS: most Foundation validators and fixture modes.
- FAIL: dependency-direction strict validator reports 358 violations and 38 warnings.
- PASS: fast strict passes 32 commands in 308.406 seconds.
- NOT RUN: full CTest; remains T4/full-gate debt.

## DECISION

Foundation Lock is not closed. `WORKBENCH-VALIDATION-SLICE-01` is not authorized.

Next task: `FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01`.

## EVIDENCE

- `.aide/reports/FOUNDATION-CLOSEOUT-01-validation.md`
- `.aide/reports/FOUNDATION-CLOSEOUT-01-foundation-matrix.md`
- `.aide/reports/FOUNDATION-CLOSEOUT-01-blockers.md`
- `.aide/reports/FOUNDATION-CLOSEOUT-01-next-readiness.md`
- `.aide/reports/FOUNDATION-CLOSEOUT-01-fast-strict.md`

## NON_GOALS

- No Workbench UI.
- No product feature implementation.
- No runtime module loader.
- No provider runtime.
- No package runtime.
- No broad directory moves.
- No new major governance subsystem.

## ACCEPTANCE

- Foundation files and validators are inventoried.
- Required validators are run and reported honestly.
- Blockers are classified without false green status.
- Next authorized or repair task is explicit.

## OUTPUT_SCHEMA

Return branch, starting HEAD, ending HEAD, origin/main, push status, Foundation Lock decision, layer statuses, fast strict status, RepoX status, smoke/build/full CTest status, generated-output status, warnings, blockers, and next task.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- approx_tokens: 760
- budget_status: PASS
