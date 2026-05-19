Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none

Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.988c3e9aaeb0d3eb`

- Symbol: `capability_rows_by_id`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `MED`
- Canonical Candidate: `src/contracts/capability/capability/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/contracts/capability/capability/__init__.py`
- `src/contracts/capability/capability/capability_engine.py`

## Scorecard

- `src/contracts/capability/capability/__init__.py` disposition=`canonical` rank=`1` total_score=`77.98` risk=`MED`
- `src/contracts/capability/capability/capability_engine.py` disposition=`quarantine` rank=`2` total_score=`73.87` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/CAPABILITY_STAGES.md, docs/CODE_CHANGE_JUSTIFICATION.md, docs/GLOSSARY.md, docs/MODDER_GUIDE.md, docs/TESTX_STAGE_MATRIX.md, docs/agents/AGENT_GOALS.md, docs/agents/AGENT_IDENTITY.md, docs/agents/AGENT_MODEL.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validators/suite/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
