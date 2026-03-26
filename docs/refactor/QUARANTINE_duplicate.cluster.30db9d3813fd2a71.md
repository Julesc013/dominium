Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.30db9d3813fd2a71`

- Symbol: `domui_win32_run_shell`
- Cluster Kind: `near`
- Cluster Resolution: `merge`
- Risk Level: `MED`
- Canonical Candidate: `launcher/gui/launcher_app_win32.cpp`
- Quarantine Reasons: `cross_domain_helper_collision, cross_product_surface, file_scope_ambiguity, near_duplicate_requires_review, phase_boundary_deferred, requires_medium_risk_batch_gate, secondary_file_active_in_default_build`
- Planned Action Kinds: `merge, rewire, deprecate`

## Competing Files

- `client/gui/client_app_win32.cpp`
- `launcher/gui/launcher_app_win32.cpp`
- `server/gui/server_app_win32.cpp`
- `setup/gui/setup_app_win32.cpp`
- `tools/gui/tools_app_win32.cpp`

## Scorecard

- `launcher/gui/launcher_app_win32.cpp` disposition=`canonical` rank=`1` total_score=`67.27` risk=`MED`
- `setup/gui/setup_app_win32.cpp` disposition=`merge` rank=`2` total_score=`67.27` risk=`MED`
- `client/gui/client_app_win32.cpp` disposition=`merge` rank=`3` total_score=`66.91` risk=`MED`
- `server/gui/server_app_win32.cpp` disposition=`drop` rank=`4` total_score=`66.31` risk=`MED`
- `tools/gui/tools_app_win32.cpp` disposition=`merge` rank=`5` total_score=`60.71` risk=`LOW`

## Usage Sites

- Build Targets: `launcher_app_win32`
- Docs: `docs/audit/REPO_TREE_INDEX.md`

## Tests Involved

- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile FAST`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
