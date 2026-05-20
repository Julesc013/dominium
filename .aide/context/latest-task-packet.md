# AIDE Latest Task Packet

## PHASE

foundation-lock

## GOAL

Complete `API-ABI-CANON-01` by defining provisional C API/ABI canon,
public-header validation, fixtures, documentation, public-surface registration,
and evidence without changing product behavior.

## WHY

Dominium needs enforceable API/ABI law before future provider, command, module,
and compatibility work can expose stable public surfaces. Existing broad
headers must stay visible as provisional debt, not become accidental frozen ABI.

## CONTEXT_REFS

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `contracts/testing/test_tiers.contract.toml`
- `contracts/public_surface/public_surface.contract.toml`
- `docs/architecture/public_surface_registry.md`
- `docs/development/public_surface_guidelines.md`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

- `contracts/abi/**`
- `contracts/public_surface/**` for narrow registry updates
- `docs/architecture/api_abi_canon.md`
- `docs/development/c89_coding_standard.md`
- `docs/development/cpp98_implementation_standard.md`
- `docs/development/module_api_standard.md`
- `tools/validators/abi/**`
- `tests/contract/public_headers/**`
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/audits/**`
- `docs/repo/POST_CONVERGE_NEXT_STEPS.md`
- `docs/repo/POST_RESTRUCTURE_PROOF.md`
- `docs/repo/RESTRUCTURE_REPAIR_STATUS.md`
- `docs/architecture/CANON_INDEX.md`

## FORBIDDEN_PATHS

- `.dominium.local/**`
- `.aide.local/**`
- build, projection, release, installer, upload, cache, and generated output roots
- gameplay, renderer, Workbench UI, native GUI, worldgen, package runtime, and product behavior implementation paths

## IMPLEMENTATION

- Add provisional ABI contracts and rule registry.
- Add public-header validator with Python stdlib only.
- Add public-header fixtures and docs.
- Register ABI surfaces conservatively in the public-surface registry.
- Record warning debt without promoting any ABI to frozen.

## VALIDATION

- `python -m py_compile tools/validators/abi/check_public_headers.py`
- `python tools/validators/abi/check_public_headers.py --repo-root . --strict`
- `python tools/validators/abi/check_public_headers.py --repo-root . --json`
- `python tools/validators/abi/check_public_headers.py --repo-root . --fixtures`
- JSON parse for ABI registries/schemas and result reports
- TOML parse/fallback for ABI contracts
- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`
- fast strict gate
- existing strict repo/root/distribution/component validators
- docs/build/UI/ABI checks
- git diff checks

## COMMITS

Commit subject: `audit(abi): add public api canon`

## EVIDENCE

- `.aide/reports/API-ABI-CANON-01-status.md`
- `.aide/reports/API-ABI-CANON-01-validation.md`
- `.aide/reports/API-ABI-CANON-01-results.json`
- `.aide/reports/API-ABI-CANON-01-public-header-inventory.md`
- `docs/repo/audits/API_ABI_CANON_01.md`

## NON_GOALS

No feature implementation, public release, tag, upload, renderer/native GUI
behavior, package runtime, provider model, compatibility corpus, dependency
direction law, or frozen ABI promotion.

## ACCEPTANCE

ABI canon and validator exist, fixtures validate, public surface registry passes,
fast strict passes or any failure is honestly documented, and feature work stays
blocked pending Foundation Lock.

## OUTPUT_SCHEMA

Final report includes branch, starting HEAD, ending HEAD, origin/main, push
status, result, created files, header candidate counts, warning count, validator
status, fast strict status, known warnings, worktree status, and next task.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- budget_status: PASS
