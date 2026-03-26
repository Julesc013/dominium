Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.06c6bfc2994e613b`

- Symbol: `illumination_model_rows`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/worldgen/earth/lighting/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/worldgen/earth/lighting/__init__.py`
- `src/worldgen/earth/lighting/illumination_engine.py`

## Scorecard

- `src/worldgen/earth/lighting/__init__.py` disposition=`canonical` rank=`1` total_score=`58.43` risk=`HIGH`
- `src/worldgen/earth/lighting/illumination_engine.py` disposition=`quarantine` rank=`2` total_score=`56.26` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/audit/ARCH_AUDIT_CONSTITUTION.md, docs/audit/ARCH_AUDIT_FIX_PLAN.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/EARTH10_RETRO_AUDIT.md, docs/audit/EARTH5_RETRO_AUDIT.md, docs/audit/EARTH8_RETRO_AUDIT.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
