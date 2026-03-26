Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.55396f936789fb12`

- Symbol: `_entry_fingerprint`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/compatx/core/semantic_contract_validator.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/meta_extensions_engine.py`
- `tools/compatx/core/semantic_contract_validator.py`

## Scorecard

- `tools/compatx/core/semantic_contract_validator.py` disposition=`canonical` rank=`1` total_score=`84.05` risk=`HIGH`
- `src/meta_extensions_engine.py` disposition=`quarantine` rank=`2` total_score=`79.64` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/SCHEMA_CHANGE_NOTES.md, docs/architecture/SYSTEM_TOPOLOGY_MAP.md, docs/architecture/WORLDDEFINITION.md, docs/audit/CODE_DATA_SEPARATION_REPORT.md, docs/audit/COMPAT_SEM1_RETRO_AUDIT.md, docs/audit/CONSISTENCY_AUDIT_REPORT.md, docs/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md, docs/audit/DOC_INDEX.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
