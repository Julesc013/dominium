Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.f72221ddaa275a0a`

- Symbol: `_repo_abs`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/mvp/cross_platform_gate_common.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/validation/validation_engine.py`
- `tools/audit/arch_audit_common.py`
- `tools/mvp/cross_platform_gate_common.py`
- `tools/mvp/mvp_smoke_common.py`
- `tools/mvp/stress_gate_common.py`
- `tools/time/time_anchor_common.py`

## Scorecard

- `tools/mvp/cross_platform_gate_common.py` disposition=`canonical` rank=`1` total_score=`67.74` risk=`HIGH`
- `tools/mvp/mvp_smoke_common.py` disposition=`quarantine` rank=`2` total_score=`63.33` risk=`HIGH`
- `tools/mvp/stress_gate_common.py` disposition=`quarantine` rank=`3` total_score=`62.8` risk=`HIGH`
- `tools/audit/arch_audit_common.py` disposition=`merge` rank=`4` total_score=`53.57` risk=`HIGH`
- `tools/time/time_anchor_common.py` disposition=`merge` rank=`5` total_score=`47.62` risk=`HIGH`
- `src/validation/validation_engine.py` disposition=`merge` rank=`6` total_score=`41.37` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/release/PROVISIONAL_FEATURE_LIST.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
