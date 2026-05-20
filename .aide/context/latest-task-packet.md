# AIDE Latest Task Packet

## PHASE

foundation-lock

## GOAL

Complete `DIAGNOSTIC-CODE-REGISTRY-01` by defining Dominium's diagnostic code,
severity, category, evidence, event, and refusal/recovery metadata surfaces.

## WHY

Free-text-only failures are not enough for CLI, TUI, Workbench, headless tools,
tests, release proof, AIDE/Codex, setup, package validation, and runtime/service
diagnostics. Conditions need stable codes, owners, severity, recovery actions,
and evidence references.

## CONTEXT_REFS

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `contracts/testing/test_tiers.contract.toml`
- `contracts/public_surface/public_surface.contract.toml`
- `contracts/abi/c_api.contract.toml`
- `contracts/repo/dependency_directions.contract.toml`
- `contracts/command/command_surface.contract.toml`
- `contracts/refusal/refusal_code.registry.json`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

- `contracts/diagnostics/**`
- `contracts/evidence/**`
- `contracts/event/**` for narrow diagnostic/evidence alignment
- `contracts/refusal/**` for diagnostic cross-references
- `contracts/command/**` for narrow diagnostic/evidence references
- `contracts/public_surface/**` for narrow registry cross-reference
- `docs/architecture/diagnostics_and_evidence.md`
- `docs/development/diagnostic_code_guidelines.md`
- `tools/validators/contracts/check_diagnostics_registry.py`
- `tests/contract/diagnostics/**`
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/audits/**`
- narrow repo status docs

## FORBIDDEN_PATHS

- `.dominium.local/**`
- `.aide.local/**`
- build, projection, release, installer, upload, cache, and generated output roots
- gameplay, renderer, Workbench UI, native GUI, package runtime, diagnostic
  runtime dispatch, command runtime dispatch, and product behavior paths

## IMPLEMENTATION

- Add diagnostic code, severity, category, and policy contracts.
- Add evidence packet/reference schemas and minimal event-schema alignment.
- Link existing command refusal codes to diagnostic codes where direct.
- Add diagnostics validator and fixture suite.
- Register diagnostics/evidence/event surfaces in public-surface governance.
- Record evidence honestly, including existing dependency-direction debt.

## VALIDATION

- `python -m py_compile tools/validators/contracts/check_diagnostics_registry.py`
- JSON parse for created/touched schemas, registries, fixtures, and reports.
- TOML parse/fallback for `contracts/diagnostics/diagnostic_policy.contract.toml`.
- `python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict`
- `python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --json`
- `python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --fixtures`
- command/public-surface/dependency-direction/ABI validators.
- strict repo/root/distribution/component validators.
- docs/build/UI/ABI supplemental checks.
- `python tools/test/run_fast_strict.py --repo-root .`
- git diff checks.

## TOKEN_ESTIMATE

Expected review packet size is under 1,200 tokens. Detailed diagnostic registry
and validation evidence lives in `.aide/reports/DIAGNOSTIC-CODE-REGISTRY-01-*`.

## COMMITS

Commit subject: `audit(diagnostics): add diagnostic code registry`

## EVIDENCE

- `.aide/reports/DIAGNOSTIC-CODE-REGISTRY-01-status.md`
- `.aide/reports/DIAGNOSTIC-CODE-REGISTRY-01-validation.md`
- `.aide/reports/DIAGNOSTIC-CODE-REGISTRY-01-results.json`
- `.aide/reports/DIAGNOSTIC-CODE-REGISTRY-01-initial-diagnostic-inventory.md`
- `.aide/reports/DIAGNOSTIC-CODE-REGISTRY-01-fast-strict.json`
- `.aide/reports/DIAGNOSTIC-CODE-REGISTRY-01-fast-strict.md`
- `docs/repo/audits/DIAGNOSTIC_CODE_REGISTRY_01.md`

## NON_GOALS

No diagnostic runtime dispatch, Workbench UI, gameplay, renderer, package
runtime change, capability/refusal law, provider model, public release, tag,
upload, or full CTest proof.

## ACCEPTANCE

Diagnostic registry law and validator exist, fixtures pass, initial diagnostics
are provisional and honest, surrounding validators run, and feature work stays
blocked pending Foundation Lock.

## OUTPUT_SCHEMA

Final report includes branch, starting HEAD, ending HEAD, origin/main, push
status, result, created contracts/schemas/docs/tools, diagnostic and
severity/category counts, public-surface update status, command/refusal update
status, validator status, fast strict status, known warnings, worktree status,
and next task.
