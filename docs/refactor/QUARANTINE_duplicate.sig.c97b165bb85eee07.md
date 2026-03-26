Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.c97b165bb85eee07`

- Symbol: `build_qc_result_record_row`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/process/qc/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/process/qc/__init__.py`
- `src/process/qc/qc_engine.py`

## Scorecard

- `src/process/qc/__init__.py` disposition=`canonical` rank=`1` total_score=`74.76` risk=`HIGH`
- `src/process/qc/qc_engine.py` disposition=`quarantine` rank=`2` total_score=`69.76` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/CLI_REFERENCE.md, docs/archive/architecture/COMPATIBILITY_PHILOSOPHY.md, docs/archive/architecture/TERMINOLOGY.md, docs/audit/ARCHIVE_POLICY_BASELINE.md, docs/audit/ARCH_AUDIT_FIX_PLAN.md, docs/audit/BASELINE_UNIVERSE0_RETRO_AUDIT.md, docs/audit/CHEM_DEGRADATION_BASELINE.md, docs/audit/COMBUSTION_BASELINE.md`

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
