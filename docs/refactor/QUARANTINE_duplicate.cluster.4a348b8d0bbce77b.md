Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.4a348b8d0bbce77b`

- Symbol: `round_trip`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tests/schema/schema_unknown_field_tests.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tests/schema/schema_roundtrip_tests.py`
- `tests/schema/schema_unknown_field_tests.py`

## Scorecard

- `tests/schema/schema_unknown_field_tests.py` disposition=`canonical` rank=`1` total_score=`68.87` risk=`HIGH`
- `tests/schema/schema_roundtrip_tests.py` disposition=`quarantine` rank=`2` total_score=`59.06` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/SCHEMA_CANON_ALIGNMENT.md, docs/SCHEMA_EVOLUTION.md, docs/architecture/SCHEMA_STABILITY.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/SCHEMA_CANON_ALIGNMENT.md`

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
