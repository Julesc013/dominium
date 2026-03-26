Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.b15aac146f6b16e4`

- Symbol: `TickT`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/time/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/time/__init__.py`
- `src/time/tick_t.py`

## Scorecard

- `src/time/__init__.py` disposition=`canonical` rank=`1` total_score=`77.86` risk=`HIGH`
- `src/time/tick_t.py` disposition=`quarantine` rank=`2` total_score=`76.01` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/GLOSSARY.md, docs/architecture/AI_AND_DELEGATED_AUTONOMY_MODEL.md, docs/architecture/ARCH0_CONSTITUTION.md, docs/architecture/CANONICAL_SYSTEM_MAP.md, docs/architecture/COLLAPSE_EXPAND_CONTRACT.md, docs/architecture/CROSS_SHARD_LOG.md, docs/architecture/DETERMINISTIC_ORDERING_POLICY.md, docs/architecture/DISTRIBUTED_TIME_MODEL.md`

## Tests Involved

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

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
