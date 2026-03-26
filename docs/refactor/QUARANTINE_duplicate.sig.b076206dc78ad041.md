Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.b076206dc78ad041`

- Symbol: `build_process_run_record_row`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `MED`
- Canonical Candidate: `src/process/process_run_engine.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/process/__init__.py`
- `src/process/process_run_engine.py`

## Scorecard

- `src/process/process_run_engine.py` disposition=`canonical` rank=`1` total_score=`71.25` risk=`MED`
- `src/process/__init__.py` disposition=`quarantine` rank=`2` total_score=`67.5` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/CLI_REFERENCE.md, docs/archive/architecture/INVARIANTS.md, docs/archive/architecture/TERMINOLOGY.md, docs/audit/APPSHELL_IPC_BASELINE.md, docs/audit/CHEM1_RETRO_AUDIT.md, docs/audit/CHEM4_RETRO_AUDIT.md, docs/audit/COMBUSTION_BASELINE.md, docs/audit/COMPUTE_BUDGET_BASELINE.md`

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
