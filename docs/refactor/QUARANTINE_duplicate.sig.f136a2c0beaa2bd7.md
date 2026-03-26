Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.f136a2c0beaa2bd7`

- Symbol: `ALLOWED_CONTROL_IR_OP_TYPES`
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
- `src/control/ir/control_ir_verifier.py` disposition=`merge` rank=`3` total_score=`55.18` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/SPECTATOR_TO_GODMODE.md, docs/audit/GEO5_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/MOD_POLICY0_RETRO_AUDIT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/SIGNAL_BUS_BASELINE.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/control/CONTROL_EXTENSION_CONTRACT.md`

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
