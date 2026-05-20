# AIDE Latest Task Packet

## PHASE

Foundation Lock - PORTABILITY-MATRIX-01

## GOAL

Define Dominium's platform, architecture, toolchain, ABI, renderer, package,
runtime, product mode, and release evidence portability matrix without adding
build targets, CI lanes, provider/runtime behavior, renderer behavior, package
runtime, Workbench UI, or release outputs.

## WHY

Portability claims must be matrix-backed and evidence-backed. Planned,
research, experimental, and provisional rows must not become support claims by
folder presence, preset presence, installed toolchain presence, or prose.

## CONTEXT_REFS

- `AGENTS.md`
- `contracts/platform/**`
- `contracts/build/**`
- `contracts/provider/**`
- `contracts/capability/**`
- `contracts/public_surface/public_surface.contract.toml`
- `contracts/diagnostics/diagnostic_code.registry.json`
- `contracts/refusal/refusal_code.registry.json`
- `.aide/reports/PORTABILITY-MATRIX-01-validation.md`
- `.aide/reports/PORTABILITY-MATRIX-01-fast-strict.md`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

- `contracts/platform/**`
- `contracts/build/**` only for narrow references
- `contracts/provider/**` only for narrow references
- `contracts/capability/**` only for narrow references
- `contracts/release/**` only for narrow references
- `contracts/artifact/**` only for narrow references
- `contracts/diagnostics/**`
- `contracts/refusal/**`
- `contracts/public_surface/**`
- `docs/architecture/portability_matrix.md`
- `docs/development/portability_guidelines.md`
- `docs/build/toolchain_portability.md`
- `docs/release/platform_support_policy.md`
- `tools/validators/platform/check_portability_matrix.py`
- `tests/contract/portability/**`
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/audits/**`
- `docs/repo/POST_CONVERGE_NEXT_STEPS.md`
- `docs/repo/POST_RESTRUCTURE_PROOF.md`
- `docs/repo/RESTRUCTURE_REPAIR_STATUS.md`

## FORBIDDEN_PATHS

- `.git/**`
- `.aide.local/**`
- `.dominium.local/**`
- generated build/projection/release outputs
- CMake presets, CI workflow mutation, new build targets, runtime provider
  implementations, renderer implementations, package runtime, Workbench UI,
  gameplay/domain/native GUI behavior, release tags, uploads, or GitHub
  settings.

## IMPLEMENTATION

- Added provisional portability contracts, registries, matrices, validator,
  fixtures, docs, public-surface entries, diagnostics, refusals, and
  capabilities.
- Preserved existing release/platform docs as evidence references, not support
  claims.
- Refreshed `docs/archive/audit/identity_fingerprint.json` after updating
  `docs/architecture/CANON_INDEX.md`.

## VALIDATION

- `python -m py_compile tools/validators/platform/check_portability_matrix.py`
- `python tools/validators/platform/check_portability_matrix.py --repo-root . --strict`
- `python tools/validators/platform/check_portability_matrix.py --repo-root . --json`
- `python tools/validators/platform/check_portability_matrix.py --repo-root . --fixtures`
- `python tools/validators/platform/check_portability_matrix.py --repo-root . --inventory`
- Cross-law validators listed in `.aide/reports/PORTABILITY-MATRIX-01-validation.md`
- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/PORTABILITY-MATRIX-01-fast-strict.json --md-out .aide/reports/PORTABILITY-MATRIX-01-fast-strict.md`
- `git diff --check`

## EVIDENCE

- `contracts/platform/**`
- `tools/validators/platform/check_portability_matrix.py`
- `tests/contract/portability/**`
- `docs/architecture/portability_matrix.md`
- `docs/development/portability_guidelines.md`
- `docs/build/toolchain_portability.md`
- `docs/release/platform_support_policy.md`
- `.aide/reports/PORTABILITY-MATRIX-01-status.md`
- `.aide/reports/PORTABILITY-MATRIX-01-validation.md`
- `.aide/reports/PORTABILITY-MATRIX-01-results.json`
- `.aide/reports/PORTABILITY-MATRIX-01-fast-strict.md`
- `docs/repo/audits/PORTABILITY_MATRIX_01.md`

## NON_GOALS

- No new platform/toolchain support claim.
- No CMake preset, CI job, build target, provider implementation, renderer
  implementation, package runtime, product behavior, Workbench UI, release
  artifact, tag, upload, or GitHub settings mutation.

## ACCEPTANCE

- Portability validator passes strict/json/fixtures modes.
- Fast strict passes.
- Existing known debt is reported, not hidden.
- Support claims remain evidence-backed and provisional rows remain
  non-support claims.

## OUTPUT_SCHEMA

Return branch, starting/ending HEAD, origin/main, push status, result status,
created artifacts, counts, registry updates, validator status, fast strict
status, known warnings, worktree status, and next task.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 4747
- approx_tokens: 1187
- budget_status: PASS
- warnings:
  - none
