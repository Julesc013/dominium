Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.b4a97a3751d9291d`

- Symbol: `traversal_policy_registry_hash`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/geo/path/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/geo/__init__.py`
- `src/geo/path/__init__.py`
- `src/geo/path/path_engine.py`

## Scorecard

- `src/geo/path/__init__.py` disposition=`canonical` rank=`1` total_score=`74.7` risk=`HIGH`
- `src/geo/__init__.py` disposition=`quarantine` rank=`2` total_score=`69.4` risk=`HIGH`
- `src/geo/path/path_engine.py` disposition=`merge` rank=`3` total_score=`48.04` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/BUDGET_POLICY.md, docs/architecture/CANON_INDEX.md, docs/architecture/CORE_ABSTRACTIONS.md, docs/architecture/DUPLICATION_DETECTION_RULES.md, docs/architecture/EXOTIC_TRAVEL_AND_REALITY.md, docs/architecture/EXPLORATION_METRICS.md, docs/architecture/EXPLORATION_SCALING_PROOF.md, docs/architecture/NO_MAGIC_TELEPORTS.md`

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
