Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.b1298b209bfb3ba6`

- Symbol: `REFUSAL_MODEL_BINDING_INVALID`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/models/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/models/__init__.py`
- `src/models/model_engine.py`

## Scorecard

- `src/models/__init__.py` disposition=`canonical` rank=`1` total_score=`64.76` risk=`HIGH`
- `src/models/model_engine.py` disposition=`quarantine` rank=`2` total_score=`63.33` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/LOGIC_ELEMENTS_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/SYSTEM_INTERFACE_INVARIANT_BASELINE.md, docs/governance/REPOX_RULESETS.md, docs/logic/LOGIC_COMPILATION_MODEL.md, docs/release/PROVISIONAL_FEATURE_LIST.md, docs/specs/launcher/ARCHITECTURE.md`

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

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
