Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.de4aa0e10bcb06f9`

- Symbol: `field_binding_rows_by_field_id`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/fields/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/field/__init__.py`
- `src/fields/__init__.py`

## Scorecard

- `src/fields/__init__.py` disposition=`canonical` rank=`1` total_score=`77.62` risk=`HIGH`
- `src/field/__init__.py` disposition=`quarantine` rank=`2` total_score=`73.27` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/GLOSSARY.md, docs/SURVIVAL_SLICE.md, docs/architecture/CANON_INDEX.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/DETERMINISTIC_ORDERING_POLICY.md, docs/architecture/GLOBAL_ID_MODEL.md, docs/architecture/HAZARDS_MODEL.md, docs/architecture/RISK_AND_LIABILITY_MODEL.md`

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
