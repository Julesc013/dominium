Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.d16537811d05e585`

- Symbol: `__dir__`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/embodiment/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/appshell/__init__.py`
- `src/appshell/commands/__init__.py`
- `src/embodiment/__init__.py`
- `src/release/__init__.py`

## Scorecard

- `src/embodiment/__init__.py` disposition=`canonical` rank=`1` total_score=`79.64` risk=`HIGH`
- `src/release/__init__.py` disposition=`merge` rank=`2` total_score=`79.64` risk=`HIGH`
- `src/appshell/__init__.py` disposition=`drop` rank=`3` total_score=`78.57` risk=`HIGH`
- `src/appshell/commands/__init__.py` disposition=`quarantine` rank=`4` total_score=`76.43` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/STATUS_NOW.md, docs/agents/AGENT_IDENTITY.md, docs/architecture/CANON_INDEX.md, docs/architecture/EXTENSION_MAP.md, docs/architecture/IDENTITY_ACROSS_TIME.md, docs/architecture/LIFE_AND_POPULATION.md, docs/audit/BODY_COLLISION_BASELINE.md, docs/audit/CAMERA_VIEW_BASELINE.md`

## Tests Involved

- `python tools/appshell/tool_run_ipc_unify.py --repo-root .`
- `python tools/compat/tool_run_interop_stress.py --repo-root .`
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
