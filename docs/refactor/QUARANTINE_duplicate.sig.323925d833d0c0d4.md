Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.323925d833d0c0d4`

- Symbol: `platform_capability_rows_by_id`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/platform/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/platform/__init__.py`
- `src/platform/platform_probe.py`

## Scorecard

- `src/platform/__init__.py` disposition=`canonical` rank=`1` total_score=`75.0` risk=`HIGH`
- `src/platform/platform_probe.py` disposition=`quarantine` rank=`2` total_score=`68.93` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/CODE_CHANGE_JUSTIFICATION.md, docs/GLOSSARY.md, docs/app/CLI_CONTRACTS.md, docs/app/PRODUCT_BOUNDARIES.md, docs/app/RUNTIME_LOOP.md, docs/app/TESTX_COMPLIANCE.md, docs/architecture/ARCH_BUILD_ENFORCEMENT.md, docs/architecture/CANONICAL_SYSTEM_MAP.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
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
