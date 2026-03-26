Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.3e9acd788233926a`

- Symbol: `REFUSAL_TASK_TOOL_REQUIRED`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/interaction/task/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/interaction/__init__.py`
- `src/interaction/task/__init__.py`
- `src/interaction/task/task_engine.py`

## Scorecard

- `src/interaction/task/__init__.py` disposition=`canonical` rank=`1` total_score=`75.3` risk=`HIGH`
- `src/interaction/__init__.py` disposition=`quarantine` rank=`2` total_score=`65.54` risk=`HIGH`
- `src/interaction/task/task_engine.py` disposition=`merge` rank=`3` total_score=`59.17` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/ACTION_SURFACE_BASELINE.md, docs/audit/CONTROL_IR_BASELINE.md, docs/audit/CONTROL_PLANE_ENGINE_BASELINE.md, docs/audit/META_COMPUTE0_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/MW0_RETRO_AUDIT.md, docs/audit/POLLUTION_EXPOSURE_BASELINE.md, docs/audit/PROCESS_DEFINITION_BASELINE.md`

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

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
