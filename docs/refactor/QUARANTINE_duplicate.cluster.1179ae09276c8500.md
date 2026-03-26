Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.1179ae09276c8500`

- Symbol: `REFUSAL_COMPILE_MISSING_PROOF`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/meta/compile/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/meta/compile/__init__.py`
- `src/meta/compile/compile_engine.py`

## Scorecard

- `src/meta/compile/__init__.py` disposition=`canonical` rank=`1` total_score=`64.76` risk=`HIGH`
- `src/meta/compile/compile_engine.py` disposition=`quarantine` rank=`2` total_score=`56.07` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/CLI_REFERENCE.md, docs/architecture/CANON_INDEX.md, docs/architecture/lockfile.md, docs/audit/CANON_MAP.md, docs/audit/COMPILED_MODEL_BASELINE.md, docs/audit/DOC_INDEX.md, docs/audit/LOGIC10_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md`

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
