Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.1336825ae3d8bc39`

- Symbol: `deterministic_signal_id`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `MED`
- Canonical Candidate: `src/logic/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/logic/__init__.py`
- `src/mobility/__init__.py`

## Scorecard

- `src/logic/__init__.py` disposition=`canonical` rank=`1` total_score=`69.64` risk=`MED`
- `src/mobility/__init__.py` disposition=`quarantine` rank=`2` total_score=`68.57` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/architecture/INFORMATION_MODEL.md, docs/architecture/NETWORKGRAPH_STANDARD.md, docs/architecture/PLATFORM_RESPONSIBILITY.md, docs/architecture/RENDERER_RESPONSIBILITY.md, docs/architecture/SIGNAL_MODEL.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md`

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
