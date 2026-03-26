Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.e75ca71ce4741af3`

- Symbol: `_macro_capsule_rows_by_id`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `MED`
- Canonical Candidate: `src/system/system_expand_engine.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/system/system_expand_engine.py`
- `src/system/system_validation_engine.py`

## Scorecard

- `src/system/system_expand_engine.py` disposition=`canonical` rank=`1` total_score=`70.65` risk=`MED`
- `src/system/system_validation_engine.py` disposition=`quarantine` rank=`2` total_score=`65.95` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/ARCHITECTURE.md, docs/GLOSSARY.md, docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/COUPLE0_RETRO_AUDIT.md, docs/audit/DOC_INDEX.md, docs/audit/MACROCAPSULE_BEHAVIOR_BASELINE.md, docs/audit/META_INSTR0_RETRO_AUDIT.md`

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
