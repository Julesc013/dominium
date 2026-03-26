Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.9c0dce6262711f22`

- Symbol: `exchange_field_boundary_values`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/field/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/field/__init__.py`
- `src/field/field_boundary_exchange.py`

## Scorecard

- `src/field/__init__.py` disposition=`canonical` rank=`1` total_score=`68.51` risk=`HIGH`
- `src/field/field_boundary_exchange.py` disposition=`quarantine` rank=`2` total_score=`65.06` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/CONSERVATION_LEDGER_BASELINE.md, docs/audit/FIELD_DISCIPLINE_REPORT.md, docs/audit/FIELD_GENERALIZATION_BASELINE.md, docs/audit/GEO4_RETRO_AUDIT.md, docs/audit/GEO_FIELD_BINDING_BASELINE.md, docs/audit/GLOBAL_FIELD_TIME_CAUSALITY.md, docs/audit/MOB10_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md`

## Tests Involved

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
