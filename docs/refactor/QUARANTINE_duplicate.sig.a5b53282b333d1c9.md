Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.a5b53282b333d1c9`

- Symbol: `_rel`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/registry_compile/bundle_profile.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `tools/appshell/ipc_unify_common.py`
- `tools/xstack/pack_loader/loader.py`
- `tools/xstack/registry_compile/bundle_profile.py`

## Scorecard

- `tools/xstack/registry_compile/bundle_profile.py` disposition=`canonical` rank=`1` total_score=`85.89` risk=`HIGH`
- `tools/xstack/pack_loader/loader.py` disposition=`quarantine` rank=`2` total_score=`84.64` risk=`HIGH`
- `tools/appshell/ipc_unify_common.py` disposition=`drop` rank=`3` total_score=`78.95` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/CODE_CHANGE_JUSTIFICATION.md, docs/app/TESTX_INVENTORY.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/TOOL_REFERENCE.md, docs/architecture/ARCHITECTURE_LAYERS.md, docs/architecture/BOUNDARY_ENFORCEMENT.md, docs/architecture/CANON_INDEX.md, docs/architecture/COMPONENTS.md`

## Tests Involved

- `python tools/appshell/tool_run_ipc_unify.py --repo-root .`
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

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
