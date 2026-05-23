# AIDE Latest Task Packet

## PHASE

PRESENTATION-CONTRACT-01 closeout; next task is `PROJECTION-CONFORMANCE-01`.

## GOAL

Define the minimum presentation contract law needed for read-only inspection,
projection conformance, future read-only Workbench shell work, and future
Universe Explorer contract work.

## WHY

The repo has moved out of broad structure cleanup. The next governed product
spine must preserve:

```text
truth -> perceived/observed -> rendered/presented
```

Presentation must show command results, diagnostics, refusals, evidence,
provenance, degradation, and projection state without becoming authority.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/current.toml`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`
- `docs/repo/FOUNDATION_LOCK.md`
- `contracts/command/command_surface.contract.toml`
- `contracts/action/action_surface.contract.toml`
- `contracts/result/result.schema.json`
- `contracts/refusal/refusal_code.registry.json`
- `contracts/diagnostic/diagnostic_code.registry.json`
- `contracts/evidence/evidence_packet.schema.json`
- `contracts/view/view_surface.contract.toml`
- `contracts/presentation/presentation_surface.contract.toml`
- `contracts/presentation/presentation_view_model.schema.json`
- `contracts/presentation/read_only_inspection.view_model.json`
- `tools/validators/contracts/check_presentation_contract.py`
- `docs/repo/audits/PRESENTATION_CONTRACT_01.md`

## ALLOWED_PATHS

- `contracts/presentation/`
- `contracts/public_surface/public_surface.contract.toml`
- `contracts/testing/test_tiers.contract.toml`
- `tests/contract/presentation/`
- `tools/validators/contracts/check_presentation_contract.py`
- `docs/repo/audits/PRESENTATION_CONTRACT_01.md`
- `.aide/queue/current.toml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`

## FORBIDDEN_PATHS

- broad Workbench UI implementation
- renderer implementation
- native GUI implementation
- gameplay/domain feature implementation
- provider runtime
- package runtime
- runtime module loader
- materialization engine
- release publication
- broad structure rewrites

## IMPLEMENTATION

- Add `contracts/presentation/presentation_surface.contract.toml`.
- Add `contracts/presentation/presentation_view_model.schema.json`.
- Add `contracts/presentation/read_only_inspection.view_model.json`.
- Add `tools/validators/contracts/check_presentation_contract.py`.
- Add valid/invalid read-only presentation fixtures.
- Register presentation public surfaces.
- Add the presentation validator to fast strict as `t1.presentation_contract`.
- Preserve all existing command/result/view/projection contracts.

## VALIDATION

- `python tools/validators/contracts/check_presentation_contract.py --repo-root . --strict`
- `python tools/validators/contracts/check_presentation_contract.py --repo-root . --fixtures`
- `python tests/contract/presentation/presentation_contract_tests.py`
- `python tools/validators/contracts/check_command_result_view.py --repo-root . --strict`
- `python tools/validators/contracts/check_command_result_view.py --repo-root . --fixtures`
- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`
- `python tools/validators/testing/check_test_tiers.py --repo-root . --strict`
- `python tools/test/run_fast_strict.py --repo-root .`
- `git diff --check`

## EVIDENCE

- changed files
- targeted validator output
- fast strict output
- audit report
- commit hash

## NON_GOALS

- No Workbench shell implementation.
- No renderer/native GUI implementation.
- No gameplay.
- No embodiment.
- No provider runtime.
- No package runtime.
- No runtime module loader.
- No materialization engine.
- No release publication.

## ACCEPTANCE

- Presentation contract law exists.
- Presentation view-model schema exists.
- Read-only inspection view model exists and validates.
- Valid presentation fixture passes.
- Invalid presentation fixtures fail.
- Public surfaces are registered.
- Fast strict includes the presentation contract validator.
- Broad feature blockers remain visible.

## NEXT

`PROJECTION-CONFORMANCE-01`

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`,
`CHANGED_FILES`, `VALIDATION`, `WARNINGS`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 4200
- approx_tokens: 1050
- budget_status: PASS
- warnings:
  - none
