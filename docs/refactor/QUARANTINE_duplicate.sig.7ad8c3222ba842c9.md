Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.7ad8c3222ba842c9`

- Symbol: `REFUSAL_MATERIALIZATION_BUDGET_EXCEEDED`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/materials/materialization/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/materials/__init__.py`
- `src/materials/materialization/__init__.py`
- `src/materials/materialization/materialization_engine.py`

## Scorecard

- `src/materials/materialization/__init__.py` disposition=`canonical` rank=`1` total_score=`56.62` risk=`HIGH`
- `src/materials/materialization/materialization_engine.py` disposition=`quarantine` rank=`2` total_score=`56.27` risk=`HIGH`
- `src/materials/__init__.py` disposition=`quarantine` rank=`3` total_score=`51.5` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/CTRL3_RETRO_AUDIT.md, docs/audit/FIDELITY_ARBITRATION_BASELINE.md, docs/audit/MACRO_MICRO_MAPPING_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/materials/GUARDRAIL_DECLARATIONS.md, docs/materials/INSPECTION_SYSTEM.md, docs/materials/MACRO_MICRO_MAPPING.md`

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
