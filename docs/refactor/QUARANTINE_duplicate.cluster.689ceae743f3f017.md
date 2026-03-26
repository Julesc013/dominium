Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.689ceae743f3f017`

- Symbol: `_rows_by_id`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `MED`
- Canonical Candidate: `src/materials/dimension_engine.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_medium_risk_batch_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/logistics/logistics_engine.py`
- `src/materials/blueprint_engine.py`
- `src/materials/composition_engine.py`
- `src/materials/construction/construction_engine.py`
- `src/materials/dimension_engine.py`

## Scorecard

- `src/materials/dimension_engine.py` disposition=`canonical` rank=`1` total_score=`74.88` risk=`MED`
- `src/materials/blueprint_engine.py` disposition=`merge` rank=`2` total_score=`73.21` risk=`MED`
- `src/materials/composition_engine.py` disposition=`merge` rank=`3` total_score=`72.61` risk=`MED`
- `src/materials/construction/construction_engine.py` disposition=`quarantine` rank=`4` total_score=`70.89` risk=`HIGH`
- `src/logistics/logistics_engine.py` disposition=`quarantine` rank=`5` total_score=`68.93` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MATERIAL_TAXONOMY_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/UNITS_AND_DIMENSIONS_BASELINE.md, docs/audit/VALIDATION_STACK_MAP.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
