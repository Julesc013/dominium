Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.588ff3a71a8fee98`

- Symbol: `_directory_tree_hash`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/release/archive_policy_common.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `src/release/release_manifest_engine.py`
- `tools/release/archive_policy_common.py`
- `tools/release/offline_archive_common.py`

## Scorecard

- `tools/release/archive_policy_common.py` disposition=`canonical` rank=`1` total_score=`84.64` risk=`HIGH`
- `tools/release/offline_archive_common.py` disposition=`quarantine` rank=`2` total_score=`83.04` risk=`HIGH`
- `src/release/release_manifest_engine.py` disposition=`drop` rank=`3` total_score=`62.56` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/README.md, docs/appshell/TOOL_REFERENCE.md, docs/architecture/CANON_INDEX.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md, docs/architecture/ENERGY_MODEL.md, docs/architecture/FLUIDS_MODEL.md, docs/architecture/REPO_INTENT.md`

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

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
