Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.616a22a6fb1e6200`

- Symbol: `REFUSAL_ARTIFACT_CONTRACT_RANGE_MISMATCH`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/lib/artifact/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/lib/artifact/__init__.py`
- `src/lib/artifact/artifact_validator.py`

## Scorecard

- `src/lib/artifact/__init__.py` disposition=`canonical` rank=`1` total_score=`65.54` risk=`HIGH`
- `src/lib/artifact/artifact_validator.py` disposition=`quarantine` rank=`2` total_score=`57.92` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/CLI_REFERENCE.md, docs/audit/DISASTER_SUITE_BASELINE.md, docs/audit/DISASTER_SUITE_RUN.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/PACK_VERIFICATION_BASELINE.md, docs/audit/REPO_TREE_INDEX.md, docs/mvp/DISASTER_SUITE_MODEL_v0_0_0.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

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
