Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.ae6630cf70156055`

- Symbol: `build_logic_behavior_model_row`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `MED`
- Canonical Candidate: `src/logic/element/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_medium_risk_batch_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/logic/__init__.py`
- `src/logic/element/__init__.py`
- `src/logic/element/logic_element_validator.py`

## Scorecard

- `src/logic/element/__init__.py` disposition=`canonical` rank=`1` total_score=`69.35` risk=`MED`
- `src/logic/__init__.py` disposition=`quarantine` rank=`2` total_score=`67.26` risk=`HIGH`
- `src/logic/element/logic_element_validator.py` disposition=`merge` rank=`3` total_score=`48.44` risk=`MED`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/LOGIC2_RETRO_AUDIT.md, docs/audit/LOGIC4_RETRO_AUDIT.md, docs/audit/LOGIC_ELEMENTS_BASELINE.md, docs/audit/LOGIC_FAULT_NOISE_BASELINE.md, docs/audit/META_STABILITY0_RETRO_AUDIT.md`

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
