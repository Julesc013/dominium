Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.640fafd6438672a8`

- Symbol: `_fidelity_candidates`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/control/fidelity/fidelity_engine.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/control/fidelity/fidelity_engine.py`
- `src/control/negotiation/negotiation_kernel.py`

## Scorecard

- `src/control/fidelity/fidelity_engine.py` disposition=`canonical` rank=`1` total_score=`58.11` risk=`HIGH`
- `src/control/negotiation/negotiation_kernel.py` disposition=`quarantine` rank=`2` total_score=`49.49` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/CTRL3_RETRO_AUDIT.md, docs/audit/EARTH0_RETRO_AUDIT.md, docs/mobility/MOBILITY_EXTENSION_CONTRACT.md, docs/release/PROVISIONAL_FEATURE_LIST.md, docs/specs/SPEC_LOD.md`

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

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
