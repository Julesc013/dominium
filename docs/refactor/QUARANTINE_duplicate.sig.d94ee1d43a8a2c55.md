Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.d94ee1d43a8a2c55`

- Symbol: `wind_tick_bucket`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/worldgen/earth/wind/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/worldgen/earth/__init__.py`
- `src/worldgen/earth/wind/__init__.py`
- `src/worldgen/earth/wind/wind_field_engine.py`

## Scorecard

- `src/worldgen/earth/wind/__init__.py` disposition=`canonical` rank=`1` total_score=`63.39` risk=`HIGH`
- `src/worldgen/earth/__init__.py` disposition=`quarantine` rank=`2` total_score=`57.5` risk=`HIGH`
- `src/worldgen/earth/wind/wind_field_engine.py` disposition=`merge` rank=`3` total_score=`53.01` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/EARTH7_RETRO_AUDIT.md, docs/audit/EARTH_WIND_PROXY_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/SIGNAL_QUALITY_BASELINE.md, docs/governance/REPOX_RULESETS.md, docs/release/PROVISIONAL_FEATURE_LIST.md, docs/worldgen/EARTH_WIND_PROXY_MODEL.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
