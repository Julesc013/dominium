Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.62a6f86ede060420`

- Symbol: `resolve_missing_capabilities`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/control/capability/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/control/capability/__init__.py`
- `src/control/capability/capability_engine.py`

## Scorecard

- `src/control/capability/__init__.py` disposition=`canonical` rank=`1` total_score=`77.98` risk=`HIGH`
- `src/control/capability/capability_engine.py` disposition=`quarantine` rank=`2` total_score=`73.87` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/MODDER_GUIDE.md, docs/app/TESTX_COMPLIANCE.md, docs/appshell/CLI_REFERENCE.md, docs/architecture/AI_INTENT_MODEL.md, docs/architecture/APP_CANON1.md, docs/architecture/BUNDLE_MODEL.md, docs/architecture/CANON_INDEX.md, docs/architecture/CAPABILITY_BASELINES.md`

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
