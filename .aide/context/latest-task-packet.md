# AIDE Latest Task Packet

## PHASE

foundation-lock

## GOAL

Complete `VERSION-DEPRECATION-LAW-01` by defining Dominium's versioning,
lifecycle, deprecation, retirement, removal, compatibility, transition,
migration, and refusal law.

## WHY

Dominium public surfaces and durable artifacts must evolve without silent
breakage. Nothing becomes stable by existing; nothing is removed without
replacement, migration, compatibility bridge, or explicit refusal policy.

## CONTEXT_REFS

- `AGENTS.md`
- `contracts/versioning/versioning.contract.toml`
- `contracts/versioning/lifecycle_state.registry.json`
- `contracts/versioning/version_compatibility.schema.json`
- `contracts/versioning/deprecation_notice.schema.json`
- `contracts/versioning/version_transition.schema.json`
- `contracts/public_surface/public_surface.contract.toml`
- `contracts/diagnostics/diagnostic_code.registry.json`
- `contracts/refusal/refusal_code.registry.json`
- `docs/architecture/versioning_and_deprecation.md`
- `docs/development/versioning_deprecation_guidelines.md`
- `.aide/reports/VERSION-DEPRECATION-LAW-01-validation.md`

## ALLOWED_PATHS

- `contracts/versioning/**`
- `contracts/public_surface/**` for narrow version/deprecation registration
- `contracts/diagnostics/**` for narrow version/deprecation diagnostic codes
- `contracts/refusal/**` for narrow version/deprecation refusal codes
- `docs/architecture/versioning_and_deprecation.md`
- `docs/development/versioning_deprecation_guidelines.md`
- `tools/validators/contracts/check_version_deprecation.py`
- `tests/contract/versioning/**`
- `.aide/context/**`
- `.aide/reports/**`
- `.aide/ledgers/**`
- `docs/repo/audits/**`
- `docs/repo/POST_CONVERGE_NEXT_STEPS.md`
- `docs/repo/POST_RESTRUCTURE_PROOF.md`
- `docs/repo/RESTRUCTURE_REPAIR_STATUS.md`
- `docs/architecture/CANON_INDEX.md`

## FORBIDDEN_PATHS

- `.dominium.local/**`
- `.aide.local/**`
- generated build/projection/release outputs
- runtime provider, migration, package, Workbench, gameplay, renderer, native GUI, release publication, or product behavior implementation paths

## IMPLEMENTATION

- Define law, schemas, registries, validator, fixtures, documentation, inventory, and evidence only.
- Do not actually deprecate, retire, remove, migrate, or promote active surfaces.
- Keep public surface, diagnostic, and refusal updates provisional.
- Record existing version-like surfaces as inventory only.

## VALIDATION

- `python -m py_compile tools/validators/contracts/check_version_deprecation.py`
- `python tools/validators/contracts/check_version_deprecation.py --repo-root . --strict`
- `python tools/validators/contracts/check_version_deprecation.py --repo-root . --json`
- `python tools/validators/contracts/check_version_deprecation.py --repo-root . --fixtures`
- `python tools/validators/contracts/check_version_deprecation.py --repo-root . --inventory`
- cross-validators for replacement, module/workbench/app, provider, capability/refusal, schema/protocol, artifact, diagnostics, command, public surface, dependency direction, and ABI
- fast strict gate
- `git diff --check`

## EVIDENCE

- `.aide/reports/VERSION-DEPRECATION-LAW-01-status.md`
- `.aide/reports/VERSION-DEPRECATION-LAW-01-validation.md`
- `.aide/reports/VERSION-DEPRECATION-LAW-01-results.json`
- `.aide/reports/VERSION-DEPRECATION-LAW-01-initial-versioning-inventory.md`
- `docs/repo/audits/VERSION_DEPRECATION_LAW_01.md`

## NON_GOALS

- No actual deprecation or removal.
- No broad version rewrites.
- No migration runtime.
- No release promotion runtime.
- No Workbench UI.
- No gameplay, renderer, native GUI, or product behavior changes.

## ACCEPTANCE

- Version/deprecation validator strict and fixture modes pass.
- Lifecycle state count is 9.
- Public surface, diagnostics, and refusal registries are updated if present.
- Fast strict passes or warning status records why it did not.
- Next task is `MOD-PACK-TRUST-MODEL-01`.

## OUTPUT_SCHEMA

Return branch, starting HEAD, ending HEAD, origin/main, pushed status, result
status, created contracts/schemas/docs/tools, lifecycle count, fixture status,
inventory summary, registry update status, validator status, fast strict status,
known warnings, worktree status, and next task.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 4320
- approx_tokens: 1080
- budget_status: PASS
- warnings:
  - none
