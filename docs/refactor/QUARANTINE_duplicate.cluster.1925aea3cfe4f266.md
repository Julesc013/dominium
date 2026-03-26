Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.1925aea3cfe4f266`

- Symbol: `collect_file_entry`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/lib/bundle/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/lib/bundle/__init__.py`
- `src/lib/bundle/bundle_manifest.py`

## Scorecard

- `src/lib/bundle/__init__.py` disposition=`canonical` rank=`1` total_score=`76.37` risk=`HIGH`
- `src/lib/bundle/bundle_manifest.py` disposition=`quarantine` rank=`2` total_score=`74.94` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/SLICE_1_CONTRACT.md, docs/audit/POWER_NETWORK_BASELINE.md, docs/audit/SRZ_HYBRID_BASELINE_REPORT.md, docs/audit/xstack/BOTTLENECK_ANALYSIS.md, docs/audit/xstack/OPTIMIZATION_SUMMARY.md, docs/dev/IMPACT_GRAPH.md, docs/diag/REPRO_BUNDLE_MODEL.md, docs/examples/SLICE_1_WALKTHROUGH.md`

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
