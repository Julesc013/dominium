Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.7d55a93586bd8bf1`

- Symbol: `REFUSAL_CTRL_IR_FORBIDDEN_OP`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/control/ir/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/control/__init__.py`
- `src/control/ir/__init__.py`
- `src/control/ir/control_ir_verifier.py`

## Scorecard

- `src/control/ir/__init__.py` disposition=`canonical` rank=`1` total_score=`73.51` risk=`HIGH`
- `src/control/__init__.py` disposition=`quarantine` rank=`2` total_score=`71.79` risk=`HIGH`
- `src/control/ir/control_ir_verifier.py` disposition=`merge` rank=`3` total_score=`58.75` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/INVARIANT_REGISTRY.md, docs/audit/CONTROL_IR_BASELINE.md, docs/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md, docs/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md, docs/audit/CONTROL_PLANE_ENGINE_BASELINE.md, docs/audit/CTRL6_RETRO_AUDIT.md, docs/audit/CTRL8_RETRO_AUDIT.md, docs/audit/DOC_INDEX.md`

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
