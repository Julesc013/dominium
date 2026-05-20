# AIDE Latest Task Packet

## PHASE

foundation-lock

## GOAL

Complete `COMMAND-SURFACE-01` by defining Dominium's command/result/view/event/
refusal/evidence law, validator, fixtures, documentation, public-surface
registration, and evidence.

## WHY

Workbench, CLI, TUI, headless tools, server/admin surfaces, rendered UI,
AIDE/Codex, and tests must share typed command/result/refusal/evidence contracts
instead of calling private tools or implementation paths as separate authority.

## CONTEXT_REFS

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `contracts/testing/test_tiers.contract.toml`
- `contracts/public_surface/public_surface.contract.toml`
- `contracts/abi/c_api.contract.toml`
- `contracts/repo/dependency_directions.contract.toml`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

- `contracts/command/**`
- `contracts/result/**`
- `contracts/view/**`
- `contracts/event/**`
- `contracts/refusal/**`
- `contracts/document/**`
- `contracts/evidence/**`
- `contracts/public_surface/**` for narrow registry cross-reference
- `docs/architecture/command_view_event_refusal.md`
- `docs/development/command_surface_guidelines.md`
- `tools/validators/contracts/check_command_surface.py`
- `tests/contract/command_surface/**`
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/audits/**`
- narrow repo status docs

## FORBIDDEN_PATHS

- `.dominium.local/**`
- `.aide.local/**`
- build, projection, release, installer, upload, cache, and generated output roots
- gameplay, renderer, Workbench UI, native GUI, package runtime, command runtime
  dispatch, and product behavior implementation paths

## IMPLEMENTATION

- Add command/result/view/event/refusal/document/evidence contracts and schemas.
- Add a command-surface validator and fixture suite.
- Register foundational validation/test command IDs conservatively.
- Register command-surface surfaces in public-surface governance.
- Record evidence honestly, including existing dependency-direction debt.

## VALIDATION

- `python -m py_compile tools/validators/contracts/check_command_surface.py`
- JSON parse for created schemas/registries/fixtures.
- TOML parse for command/view/event contracts and fixtures.
- `python tools/validators/contracts/check_command_surface.py --repo-root . --strict`
- `python tools/validators/contracts/check_command_surface.py --repo-root . --fixtures`
- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`
- `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict`
- `python tools/validators/abi/check_public_headers.py --repo-root . --strict`
- strict repo/root/distribution/component validators.
- docs/build/UI/ABI supplemental checks.
- `python tools/test/run_fast_strict.py --repo-root .`
- git diff checks.

## TOKEN_ESTIMATE

Expected review packet size is under 1,200 tokens. Detailed command-surface and
validation evidence lives in `.aide/reports/COMMAND-SURFACE-01-*`.

## COMMITS

Commit subject: `audit(command): add command surface law`

## EVIDENCE

- `.aide/reports/COMMAND-SURFACE-01-status.md`
- `.aide/reports/COMMAND-SURFACE-01-validation.md`
- `.aide/reports/COMMAND-SURFACE-01-results.json`
- `.aide/reports/COMMAND-SURFACE-01-initial-command-inventory.md`
- `.aide/reports/COMMAND-SURFACE-01-fast-strict.json`
- `.aide/reports/COMMAND-SURFACE-01-fast-strict.md`
- `docs/repo/audits/COMMAND_SURFACE_01.md`

## NON_GOALS

No command runtime implementation, Workbench UI, gameplay, renderer, package
runtime, provider model, full diagnostic registry, public release, tag, upload,
or full CTest proof.

## ACCEPTANCE

Command-surface law and validator exist, fixtures pass, initial commands are
provisional and honest, surrounding validators run, and feature work stays
blocked pending Foundation Lock.

## OUTPUT_SCHEMA

Final report includes branch, starting HEAD, ending HEAD, origin/main, push
status, result, created contracts/schemas/docs/tools, command/refusal counts,
public-surface update status, validator status, fast strict status, known
warnings, worktree status, and next task.
