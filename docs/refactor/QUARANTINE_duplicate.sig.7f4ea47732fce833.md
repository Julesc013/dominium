Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.7f4ea47732fce833`

- Symbol: `compare_required_contract_ranges`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/lib/install/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/lib/install/__init__.py`
- `src/lib/install/install_validator.py`

## Scorecard

- `src/lib/install/__init__.py` disposition=`canonical` rank=`1` total_score=`64.17` risk=`HIGH`
- `src/lib/install/install_validator.py` disposition=`quarantine` rank=`2` total_score=`55.89` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/ARTIFACT_MODEL.md, docs/audit/ARTIFACT_MANIFEST_BASELINE.md, docs/audit/INSTANCE_MANIFEST_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/compat/MIGRATION_LIFECYCLE_MODEL.md, docs/release/PROVISIONAL_FEATURE_LIST.md, docs/release/RELEASE_INDEX_MODEL.md`

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
