Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.d4545a1db44515b9`

- Symbol: `drift_policy_rows_by_id`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `MED`
- Canonical Candidate: `src/process/drift/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_medium_risk_batch_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/process/__init__.py`
- `src/process/drift/__init__.py`
- `src/process/drift/drift_engine.py`

## Scorecard

- `src/process/drift/__init__.py` disposition=`canonical` rank=`1` total_score=`77.44` risk=`MED`
- `src/process/drift/drift_engine.py` disposition=`merge` rank=`2` total_score=`73.87` risk=`MED`
- `src/process/__init__.py` disposition=`quarantine` rank=`3` total_score=`67.5` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/CODE_CHANGE_JUSTIFICATION.md, docs/CONTRIBUTING.md, docs/FAQ.md, docs/GLOSSARY.md, docs/MODDER_GUIDE.md, docs/PHILOSOPHY.md, docs/PROCESS_REGISTRY.md, docs/README.md`

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
