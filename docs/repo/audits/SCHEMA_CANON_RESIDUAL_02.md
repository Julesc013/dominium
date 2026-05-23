Status: DERIVED
Last Reviewed: 2026-05-23
Supersedes: none
Superseded By: none
Result: PASS_WITH_WARNINGS
Date: 2026-05-23
Task: SCHEMA-CANON-RESIDUAL-02
Scope: focused schema residual routing and structure warning retirement

# SCHEMA_CANON_RESIDUAL_02

## Summary

This pass moves the two clear schema residual buckets into explicit schema
families:

- `contracts/schema/engine/` -> `contracts/schema/runtime/engine/`
- `contracts/schema/meta/` -> `contracts/schema/repo/meta/`

The move preserves schema file contents and updates active TestX, AuditX,
RepoX, and structure validator references. Historical audit notes are left
unchanged.

## Files Moved

- former engine component, concurrency, constraint, partition, schedule, state,
  tolerance, and migration-note schemas now live under
  `contracts/schema/runtime/engine/`
- former meta/profile/instrumentation/provenance/equivalence/compile/player
  demand schemas now live under `contracts/schema/repo/meta/`

## References Updated

- `tools/xstack/repox/check.py`
- `tools/xstack/auditx/analyzers/e231_undeclared_temporal_domain_smell.py`
- `tools/xstack/auditx/analyzers/e279_missing_equivalence_proof_smell.py`
- `tools/xstack/testx/tests/test_action_template_schema_allows_constitutive_models.py`
- `tools/xstack/testx/tests/test_instrumentation_surface_schema_valid.py`
- `tools/xstack/testx/tests/test_player_demand_matrix_schema_valid.py`
- `tools/validators/repo/check_canonical_structure.py`
- `tools/validators/repo/check_structure_residuals.py`
- `docs/repo/structure_residual_classification.md`

## Accepted Locations

No move was made for the following paths because live repo evidence already
binds them to their current owners:

- `runtime/project_graph/`: contract-backed runtime service surface
- `runtime/ui/client/`: accepted reusable client UI-facing surface from
  `APPS_THIN_01`
- `runtime/ui/control/domui/` and `runtime/include/domino/ui/dui/`: Dominium UI facade and
  include surfaces from `SPEC_DUI` and `STRUCTURE_CANON_SWEEP_01`

## Deferred Moves

The following remain warnings because the current notes and repo evidence do
not define a safe one-to-one destination:

- `engine/compatibility/`
- `archive/legacy/runtime/compatx/`
- `engine/foundation/`
- `engine/serialization/`
- `runtime/serialization/`
- `engine/session/`
- `runtime/session/`
- broad `tests/**` first-level taxonomy
- pack-local `content/` payload layout
- AIDE state-like control-plane roots

## Non-Goals

- no runtime implementation relocation;
- no broad tests tree migration;
- no package payload layout normalization;
- no generated registry rewrite;
- no product behavior change;
- no full CTest.

## Validation

- `py -3 -m py_compile tools/validators/repo/check_canonical_structure.py tools/validators/repo/check_structure_residuals.py tools/xstack/repox/check.py tools/xstack/auditx/analyzers/e231_undeclared_temporal_domain_smell.py tools/xstack/auditx/analyzers/e279_missing_equivalence_proof_smell.py tools/xstack/testx/tests/test_action_template_schema_allows_constitutive_models.py tools/xstack/testx/tests/test_instrumentation_surface_schema_valid.py tools/xstack/testx/tests/test_player_demand_matrix_schema_valid.py` - PASS
- `py -3 tools/validators/repo/check_canonical_structure.py --repo-root . --strict --max-findings 120` - PASS_WITH_WARNINGS
- `py -3 tools/validators/repo/check_structure_residuals.py --repo-root . --strict --max-findings 120` - PASS_WITH_WARNINGS
- `py -3 tools/validators/repo/check_structure_report_integrity.py --repo-root . --strict` - PASS
- `py -3 tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_action_template_schema_allows_constitutive_models,test_instrumentation_surface_schema_valid,test_player_demand_matrix_schema_valid` - PASS
- `py -3 tools/validators/contracts/check_project_graph_service.py --repo-root .` - PASS
- `py -3 tools/validators/contracts/check_project_graph.py --repo-root .` - PASS
- `py -3 .aide/scripts/aide_lite.py doctor` - PASS
- `py -3 .aide/scripts/aide_lite.py validate` - PASS
- `py -3 tools/validators/repo/check_content_layout.py --repo-root . --strict` - PASS
- `git diff --check` - PASS
- `git diff --cached --check` - PASS
