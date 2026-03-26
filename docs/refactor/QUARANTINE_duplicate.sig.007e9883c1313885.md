Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.007e9883c1313885`

- Symbol: `_required_fields`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/lib/save/save_validator.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/lib/artifact/artifact_validator.py`
- `src/lib/instance/instance_validator.py`
- `src/lib/save/save_validator.py`

## Scorecard

- `src/lib/save/save_validator.py` disposition=`canonical` rank=`1` total_score=`57.8` risk=`HIGH`
- `src/lib/instance/instance_validator.py` disposition=`quarantine` rank=`2` total_score=`56.49` risk=`HIGH`
- `src/lib/artifact/artifact_validator.py` disposition=`quarantine` rank=`3` total_score=`55.54` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CAPABILITY_ONLY_CANON.md, docs/architecture/INVARIANT_REGISTRY.md, docs/architecture/SCHEMA_CHANGE_NOTES.md, docs/architecture/WORLDDEFINITION.md, docs/archive/ci/COREDATA_CONSISTENCY_REPORT.md, docs/audit/CONSISTENCY_AUDIT_REPORT.md, docs/audit/CONTENT_STORE_BASELINE.md, docs/audit/DISASTER_TEST0_RETRO_AUDIT.md`

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
