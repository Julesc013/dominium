Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.9882d9c624acec03`

- Symbol: `_event_fingerprint`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/materials/construction/construction_engine.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/logistics/logistics_engine.py`
- `src/materials/construction/construction_engine.py`

## Scorecard

- `src/materials/construction/construction_engine.py` disposition=`canonical` rank=`1` total_score=`70.89` risk=`HIGH`
- `src/logistics/logistics_engine.py` disposition=`quarantine` rank=`2` total_score=`68.93` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/GLOSSARY.md, docs/architecture/CANON_INDEX.md, docs/architecture/REPORT_GAME_ARCH_DECISIONS.md, docs/audit/BOM_AG_BASELINE.md, docs/audit/CANON_MAP.md, docs/audit/CAP_NEG4_RETRO_AUDIT.md, docs/audit/CONSTRUCTION_BASELINE.md, docs/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md`

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
