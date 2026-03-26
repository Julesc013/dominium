Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.0bd404858c0f8514`

- Symbol: `_binding_by_network_id`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `MED`
- Canonical Candidate: `src/logic/eval/logic_eval_engine.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_medium_risk_batch_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/logic/compile/logic_compiler.py`
- `src/logic/eval/logic_eval_engine.py`
- `src/logic/network/logic_network_engine.py`

## Scorecard

- `src/logic/eval/logic_eval_engine.py` disposition=`canonical` rank=`1` total_score=`49.89` risk=`MED`
- `src/logic/network/logic_network_engine.py` disposition=`quarantine` rank=`2` total_score=`49.76` risk=`HIGH`
- `src/logic/compile/logic_compiler.py` disposition=`merge` rank=`3` total_score=`48.5` risk=`MED`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/LOGIC0_RETRO_AUDIT.md, docs/audit/LOGIC7_RETRO_AUDIT.md, docs/audit/LOGIC_CONSTITUTION_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/PLATFORM_RENDERER_SURFACE.md`

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
