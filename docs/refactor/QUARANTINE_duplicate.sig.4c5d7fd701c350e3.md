Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.4c5d7fd701c350e3`

- Symbol: `REFUSAL_REENACTMENT_BUDGET_EXCEEDED`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/materials/commitments/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/materials/__init__.py`
- `src/materials/commitments/__init__.py`

## Scorecard

- `src/materials/commitments/__init__.py` disposition=`canonical` rank=`1` total_score=`54.69` risk=`HIGH`
- `src/materials/__init__.py` disposition=`quarantine` rank=`2` total_score=`51.5` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/FIDELITY_ARBITRATION_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/materials/GUARDRAIL_DECLARATIONS.md, docs/materials/INSPECTION_SYSTEM.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

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
