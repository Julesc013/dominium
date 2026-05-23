Status: DERIVED
Last Reviewed: 2026-05-23
Supersedes: none
Superseded By: none
Result: PASS_WITH_WARNINGS
Task: PRESENTATION-CONTRACT-01
Date: 2026-05-23
Baseline Commit: 1406490bba4a8db617911f54cc85a8e939d29baa
Branch: main

# PRESENTATION-CONTRACT-01

## Scope

This task defines the minimum presentation contract layer needed before
`PROJECTION-CONFORMANCE-01`, `WORKBENCH-SHELL-READONLY-01`, and future
Universe Explorer contract work.

It is contract/schema/fixture/validator work only. It does not implement a
Workbench shell, renderer, native GUI, gameplay, provider runtime, package
runtime, runtime module loader, materialization engine, or product feature.

## Files Inspected

- `AGENTS.md`
- `.aide/queue/current.toml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`
- `docs/repo/FOUNDATION_LOCK.md`
- `contracts/command/command_surface.contract.toml`
- `contracts/action/action_surface.contract.toml`
- `contracts/action/validation_actions.registry.json`
- `contracts/result/result.schema.json`
- `contracts/refusal/refusal_code.registry.json`
- `contracts/diagnostic/diagnostic_code.registry.json`
- `contracts/evidence/evidence_packet.schema.json`
- `contracts/view/view_surface.contract.toml`
- `contracts/view/validation_summary.view.json`
- `contracts/presentation/projection_kind.registry.json`
- `contracts/presentation/projection.schema.json`
- `contracts/presentation/validation_summary.projections.json`
- `tools/validators/contracts/check_command_result_view.py`
- `tests/contract/presentation/command_result_view_contract_tests.py`

## Files Changed

- `.aide/queue/current.toml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`
- `contracts/presentation/presentation_surface.contract.toml`
- `contracts/presentation/presentation_view_model.schema.json`
- `contracts/presentation/read_only_inspection.view_model.json`
- `contracts/public_surface/public_surface.contract.toml`
- `contracts/testing/test_tiers.contract.toml`
- `tests/contract/presentation/presentation_contract_tests.py`
- `tests/contract/presentation/view_model_fixtures/valid_read_only_inspection_view_model.json`
- `tests/contract/presentation/view_model_fixtures/invalid_authoritative_view_model.json`
- `tests/contract/presentation/view_model_fixtures/invalid_missing_diagnostic_binding.json`
- `tests/contract/presentation/view_model_fixtures/invalid_modal_loading_required.json`
- `tests/contract/presentation/view_model_fixtures/invalid_private_tool_binding.json`
- `tools/validators/contracts/check_presentation_contract.py`
- `docs/repo/audits/PRESENTATION_CONTRACT_01.md`

## Policy Created

`contracts/presentation/presentation_surface.contract.toml` defines:

- presentations are not authority;
- presentations do not mutate or create truth;
- Workbench shell and renderer are not authority;
- private tool calls are forbidden;
- read-only inspection requires diagnostics, refusals, evidence, provenance,
  degradation, and projection state;
- no-modal-loading claims require pending/degraded states instead of blocking;
- runtime implementation remains out of scope.

## Schema Created

`contracts/presentation/presentation_view_model.schema.json` defines the
descriptor shape for presentation view models.

The first governed descriptor is
`contracts/presentation/read_only_inspection.view_model.json`. It is the narrow
contract target for future Workbench/Client Universe Explorer inspection work.

## Fixtures Created

Valid fixture:

- `tests/contract/presentation/view_model_fixtures/valid_read_only_inspection_view_model.json`

Invalid fixtures:

- `tests/contract/presentation/view_model_fixtures/invalid_authoritative_view_model.json`
- `tests/contract/presentation/view_model_fixtures/invalid_missing_diagnostic_binding.json`
- `tests/contract/presentation/view_model_fixtures/invalid_modal_loading_required.json`
- `tests/contract/presentation/view_model_fixtures/invalid_private_tool_binding.json`

## Validator Created

`tools/validators/contracts/check_presentation_contract.py` validates:

- presentation policy booleans;
- read-only inspection descriptor presence;
- view-model ID and source refs;
- presentation-only and non-authority constraints;
- diagnostic/refusal/evidence bindings;
- no-modal-loading/degradation/pending-state requirements;
- projection-kind references;
- action bindings, transaction policy, and private-tool forbiddance;
- valid fixtures pass and invalid fixtures fail.

The validator is registered in `contracts/testing/test_tiers.contract.toml` as
`t1.presentation_contract`, so future fast strict runs include it.

## Public Surfaces Registered

- `dominium.presentation.surface.v1`
- `dominium.presentation.view_model.schema.v1`
- `dominium.presentation.read_only_inspection.v1`
- presentation contract validator public surface

## Validation

Targeted validation run:

```text
python tools/validators/contracts/check_presentation_contract.py --repo-root . --strict
python tools/validators/contracts/check_presentation_contract.py --repo-root . --fixtures
python tests/contract/presentation/presentation_contract_tests.py
python -m json.tool contracts/presentation/presentation_view_model.schema.json
python tools/validators/contracts/check_command_result_view.py --repo-root . --strict
python tools/validators/contracts/check_command_result_view.py --repo-root . --fixtures
python tools/validators/repo/check_public_surface.py --repo-root . --strict
python -m py_compile tools/validators/contracts/check_presentation_contract.py tests/contract/presentation/presentation_contract_tests.py
python tools/validators/testing/check_test_tiers.py --repo-root . --strict
python .aide/scripts/aide_lite.py validate
python .aide/scripts/aide_lite.py doctor
python scripts/ci/check_repox_rules.py --repo-root . --profile STRICT --proof-manifest-out .aide/reports/PRESENTATION-CONTRACT-01-repox-proof-manifest.json --profile-out .aide/reports/PRESENTATION-CONTRACT-01-repox-profile.json
python tools/test/run_fast_strict.py --repo-root .
git diff --check
```

Results: PASS for all commands above. RepoX reports the known stale AuditX
output warning only. Fast strict passed with `34` commands and elapsed time
`381.406` seconds.

Full CTest was not run for this contract-only slice and remains full-gate debt.

## Relationship To Prior Work

`COMMAND-RESULT-VIEW-SLICE-01` proved one validation-summary view and projection
set. `PRESENTATION-CONTRACT-01` generalizes that into presentation law for
read-only inspection without changing runtime behavior.

`PROJECTION-CONFORMANCE-01` should build on this by proving projection
descriptors and mode conformance against the presentation law.

`WORKBENCH-SHELL-READONLY-01` should consume this contract rather than inventing
private Workbench tool calls or UI authority.

Future `UNIVERSE-EXPLORER-CONTRACT-01` should use
`dominium.presentation.read_only_inspection.v1` as the contract floor for
observer-only universe inspection.

## Warnings Preserved

- Foundation Lock remains `PASS_WITH_WARNINGS`.
- Full CTest remains T4/full-gate debt.
- Broad feature work remains blocked.
- Workbench shell, renderer, native GUI, gameplay, provider runtime, package
  runtime, runtime module loader, materialization engine, and release
  publication remain blocked.

## Non-Goals Preserved

- No broad Workbench UI.
- No renderer implementation.
- No native GUI.
- No gameplay.
- No embodiment.
- No provider runtime.
- No package runtime.
- No runtime module loader.
- No materialization engine.
- No release publication.
- No broad structure rewrite.

## Feature Readiness Verdict

LIMITED.

The presentation contract spine is stronger and ready for
`PROJECTION-CONFORMANCE-01`, but this does not authorize broad product features.

## Next Tasks

1. `PROJECTION-CONFORMANCE-01`
2. `WORKBENCH-SHELL-READONLY-01`
3. `UNIVERSE-EXPLORER-CONTRACT-01`
4. `POINTER-WIDTH-SERIALIZATION-AUDIT-01`
5. `FULL-GATE-LEGACY-TEST-ROUTE-01`
