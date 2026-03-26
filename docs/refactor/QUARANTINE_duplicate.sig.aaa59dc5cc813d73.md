Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.aaa59dc5cc813d73`

- Symbol: `build_field_cell`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `MED`
- Canonical Candidate: `src/fields/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_medium_risk_batch_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/field/__init__.py`
- `src/fields/__init__.py`
- `src/fields/field_engine.py`

## Scorecard

- `src/fields/__init__.py` disposition=`canonical` rank=`1` total_score=`77.62` risk=`MED`
- `src/field/__init__.py` disposition=`quarantine` rank=`2` total_score=`73.27` risk=`HIGH`
- `src/fields/field_engine.py` disposition=`merge` rank=`3` total_score=`70.89` risk=`MED`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/ARCH_AUDIT_FIX_PLAN.md, docs/audit/EARTH10_RETRO_AUDIT.md, docs/audit/EARTH2_RETRO_AUDIT.md, docs/audit/EARTH3_RETRO_AUDIT.md, docs/audit/FIELD1_RETRO_AUDIT.md, docs/audit/FIELD_LAYER_BASELINE.md, docs/audit/GAL0_RETRO_AUDIT.md, docs/audit/GALAXY_PROXY_BASELINE.md`

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
