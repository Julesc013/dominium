Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.75e24a22f6c992de`

- Symbol: `_tokens`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `MED`
- Canonical Candidate: `src/meta/profile/profile_engine.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_medium_risk_batch_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/meta/instrumentation/instrumentation_engine.py`
- `src/meta/profile/profile_engine.py`
- `src/process/capsules/capsule_builder.py`
- `src/process/capsules/capsule_executor.py`
- `src/process/process_run_engine.py`
- `src/process/qc/qc_engine.py`

## Scorecard

- `src/meta/profile/profile_engine.py` disposition=`canonical` rank=`1` total_score=`73.87` risk=`MED`
- `src/process/process_run_engine.py` disposition=`merge` rank=`2` total_score=`71.25` risk=`MED`
- `src/process/qc/qc_engine.py` disposition=`merge` rank=`3` total_score=`69.76` risk=`MED`
- `src/process/capsules/capsule_builder.py` disposition=`quarantine` rank=`4` total_score=`68.57` risk=`HIGH`
- `src/meta/instrumentation/instrumentation_engine.py` disposition=`merge` rank=`5` total_score=`62.32` risk=`MED`
- `src/process/capsules/capsule_executor.py` disposition=`drop` rank=`6` total_score=`53.75` risk=`MED`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/ARCHITECTURE.md, docs/CODE_CHANGE_JUSTIFICATION.md, docs/CONTRIBUTING.md, docs/GLOSSARY.md, docs/PHILOSOPHY.md, docs/PROCESS_REGISTRY.md, docs/STATUS_NOW.md, docs/agents/AGENT_MODEL.md`

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
