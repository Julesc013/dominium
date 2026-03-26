Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.e3090d32e94994c1`

- Symbol: `build_product_descriptor`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/compat/descriptor/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/compat/descriptor/__init__.py`
- `src/compat/descriptor/descriptor_engine.py`

## Scorecard

- `src/compat/descriptor/__init__.py` disposition=`canonical` rank=`1` total_score=`77.44` risk=`HIGH`
- `src/compat/descriptor/descriptor_engine.py` disposition=`quarantine` rank=`2` total_score=`70.77` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/XSTACK.md, docs/app/ARTIFACT_IDENTITY.md, docs/app/CLI_CONTRACTS.md, docs/app/NATIVE_UI_POLICY.md, docs/app/PRODUCT_BOUNDARIES.md, docs/app/README.md, docs/app/RUNTIME_LOOP.md, docs/app/TESTX_COMPLIANCE.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
