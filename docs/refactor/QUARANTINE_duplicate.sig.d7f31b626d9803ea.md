Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.d7f31b626d9803ea`

- Symbol: `__getattr__`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/sessionx/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/appshell/__init__.py`
- `src/appshell/commands/__init__.py`
- `src/astro/__init__.py`
- `src/compat/__init__.py`
- `src/embodiment/__init__.py`
- `src/packs/compat/__init__.py`
- `src/release/__init__.py`
- `src/worldgen/galaxy/__init__.py`
- `src/worldgen/mw/__init__.py`
- `tools/xstack/sessionx/__init__.py`

## Scorecard

- `tools/xstack/sessionx/__init__.py` disposition=`canonical` rank=`1` total_score=`70.54` risk=`HIGH`
- `src/worldgen/mw/__init__.py` disposition=`quarantine` rank=`2` total_score=`62.98` risk=`HIGH`
- `src/compat/__init__.py` disposition=`merge` rank=`3` total_score=`58.21` risk=`HIGH`
- `src/embodiment/__init__.py` disposition=`drop` rank=`4` total_score=`58.21` risk=`HIGH`
- `src/release/__init__.py` disposition=`drop` rank=`5` total_score=`58.21` risk=`HIGH`
- `src/packs/compat/__init__.py` disposition=`drop` rank=`6` total_score=`57.62` risk=`HIGH`
- `src/appshell/__init__.py` disposition=`drop` rank=`7` total_score=`57.14` risk=`HIGH`
- `src/worldgen/galaxy/__init__.py` disposition=`drop` rank=`8` total_score=`55.21` risk=`HIGH`
- `src/appshell/commands/__init__.py` disposition=`drop` rank=`9` total_score=`53.07` risk=`HIGH`
- `src/astro/__init__.py` disposition=`drop` rank=`10` total_score=`49.21` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `none`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
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
