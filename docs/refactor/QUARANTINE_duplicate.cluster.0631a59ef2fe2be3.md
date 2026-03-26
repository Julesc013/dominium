Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.0631a59ef2fe2be3`

- Symbol: `validate_extensions_map`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/meta/extensions/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/meta/extensions/__init__.py`
- `src/meta/extensions/extensions_engine.py`
- `src/meta_extensions_engine.py`

## Scorecard

- `src/meta/extensions/__init__.py` disposition=`canonical` rank=`1` total_score=`73.33` risk=`HIGH`
- `src/meta_extensions_engine.py` disposition=`quarantine` rank=`2` total_score=`72.5` risk=`HIGH`
- `src/meta/extensions/extensions_engine.py` disposition=`quarantine` rank=`3` total_score=`69.11` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/TESTX_INVENTORY.md, docs/architecture/EXTENSION_MAP.md, docs/architecture/ID_AND_NAMESPACE_RULES.md, docs/audit/COMPAT_SEM3_RETRO_AUDIT.md, docs/audit/GEO_IDENTITY_BASELINE.md, docs/audit/INSTANCE_MANIFEST_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/NUMERICAL_TOLERANCE_BASELINE.md`

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
