Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.07162c47dda2a254`

- Symbol: `build_water_view_surface`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/worldgen/earth/water/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/worldgen/earth/water/__init__.py`
- `src/worldgen/earth/water/water_view_engine.py`

## Scorecard

- `src/worldgen/earth/water/__init__.py` disposition=`canonical` rank=`1` total_score=`76.37` risk=`HIGH`
- `src/worldgen/earth/water/water_view_engine.py` disposition=`quarantine` rank=`2` total_score=`69.82` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/SURVIVAL_SLICE.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/TOOL_REFERENCE.md, docs/architecture/CANON_INDEX.md, docs/architecture/CORE_ABSTRACTIONS.md, docs/audit/ARCH_AUDIT0_RETRO_AUDIT.md, docs/audit/ARCH_AUDIT_CONSTITUTION.md, docs/audit/CANON_MAP.md`

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
