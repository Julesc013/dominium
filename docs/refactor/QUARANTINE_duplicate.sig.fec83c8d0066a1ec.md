Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.fec83c8d0066a1ec`

- Symbol: `_print_json`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/worldgen_offline/world_definition_cli.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/appshell/bootstrap.py`
- `tools/worldgen_offline/world_definition_cli.py`

## Scorecard

- `tools/worldgen_offline/world_definition_cli.py` disposition=`canonical` rank=`1` total_score=`70.75` risk=`HIGH`
- `src/appshell/bootstrap.py` disposition=`quarantine` rank=`2` total_score=`65.12` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/ARCHITECTURE.md, docs/SCHEMA_CANON_ALIGNMENT.md, docs/SCHEMA_EVOLUTION.md, docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/EG_H_REPO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md`

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
