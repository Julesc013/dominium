Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.c04b6ccb45889c40`

- Symbol: `build_teleport_tool_surface`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/embodiment/tools/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/embodiment/tools/__init__.py`
- `src/embodiment/tools/teleport_tool.py`

## Scorecard

- `src/embodiment/tools/__init__.py` disposition=`canonical` rank=`1` total_score=`72.38` risk=`HIGH`
- `src/embodiment/tools/teleport_tool.py` disposition=`quarantine` rank=`2` total_score=`69.76` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/CLI_REFERENCE.md, docs/appshell/TOOL_REFERENCE.md, docs/architecture/ANTI_CHEAT_AS_LAW.md, docs/architecture/AUTHORITY_AND_OMNIPOTENCE.md, docs/architecture/INVARIANTS.md, docs/architecture/NO_TELEPORTATION_EXCEPT_BY_CONTRACT.md, docs/architecture/TOOLS_AS_CAPABILITIES.md, docs/architecture/astronomy_catalogs.md`

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
