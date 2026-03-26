Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.fd6c24ceed7af452`

- Symbol: `REFUSAL_PROCESS_RUN_NOT_FOUND`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/process/process_run_engine.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/process/__init__.py`
- `src/process/process_run_engine.py`

## Scorecard

- `src/process/process_run_engine.py` disposition=`canonical` rank=`1` total_score=`56.96` risk=`HIGH`
- `src/process/__init__.py` disposition=`quarantine` rank=`2` total_score=`55.6` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/CLI_REFERENCE.md, docs/audit/CONSISTENCY_AUDIT_REPORT.md, docs/audit/CTRL9_RETRO_AUDIT.md, docs/audit/ELEC2_RETRO_AUDIT.md, docs/audit/LOGIC0_RETRO_AUDIT.md, docs/audit/LOGIC3_RETRO_AUDIT.md, docs/audit/LOGIC4_RETRO_AUDIT.md, docs/audit/LOGIC5_RETRO_AUDIT.md`

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
