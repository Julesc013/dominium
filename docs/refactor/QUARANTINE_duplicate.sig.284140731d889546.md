Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.284140731d889546`

- Symbol: `_normalize_tree`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/meta/observability_common.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/appshell/diag/diag_snapshot.py`
- `src/appshell/ipc/ipc_client.py`
- `src/appshell/ipc/ipc_endpoint_server.py`
- `src/appshell/ipc/ipc_transport.py`
- `src/appshell/logging/log_engine.py`
- `src/appshell/paths/virtual_paths.py`
- `src/compat/migration_lifecycle.py`
- `src/compat/shims/common.py`
- `src/diag/repro_bundle_builder.py`
- `src/governance/governance_profile.py`
- `src/lib/install/install_discovery_engine.py`
- `src/meta/identity/identity_validator.py`
- `src/platform/target_matrix.py`
- `src/release/archive_policy.py`
- `src/release/component_graph_resolver.py`
- `src/release/update_resolver.py`
- `src/security/trust/license_capability.py`
- `tools/appshell/appshell4_probe.py`
- `tools/meta/observability_common.py`
- `tools/mvp/toolchain_matrix_common.py`
- `tools/security/trust_strict_common.py`

## Scorecard

- `tools/meta/observability_common.py` disposition=`canonical` rank=`1` total_score=`84.29` risk=`HIGH`
- `tools/appshell/appshell4_probe.py` disposition=`quarantine` rank=`2` total_score=`78.21` risk=`HIGH`
- `tools/mvp/toolchain_matrix_common.py` disposition=`quarantine` rank=`3` total_score=`77.85` risk=`HIGH`
- `tools/security/trust_strict_common.py` disposition=`quarantine` rank=`4` total_score=`77.8` risk=`HIGH`
- `src/compat/migration_lifecycle.py` disposition=`quarantine` rank=`5` total_score=`77.62` risk=`HIGH`
- `src/platform/target_matrix.py` disposition=`quarantine` rank=`6` total_score=`75.0` risk=`HIGH`
- `src/appshell/paths/virtual_paths.py` disposition=`drop` rank=`7` total_score=`73.87` risk=`HIGH`
- `src/governance/governance_profile.py` disposition=`drop` rank=`8` total_score=`73.87` risk=`HIGH`
- `src/lib/install/install_discovery_engine.py` disposition=`merge` rank=`9` total_score=`73.09` risk=`HIGH`
- `src/release/archive_policy.py` disposition=`drop` rank=`10` total_score=`72.38` risk=`HIGH`
- `src/meta/identity/identity_validator.py` disposition=`drop` rank=`11` total_score=`69.64` risk=`HIGH`
- `src/appshell/diag/diag_snapshot.py` disposition=`drop` rank=`12` total_score=`69.46` risk=`HIGH`
- `src/appshell/logging/log_engine.py` disposition=`drop` rank=`13` total_score=`69.46` risk=`HIGH`
- `src/compat/shims/common.py` disposition=`drop` rank=`14` total_score=`68.81` risk=`HIGH`
- `src/release/component_graph_resolver.py` disposition=`drop` rank=`15` total_score=`66.43` risk=`HIGH`
- `src/appshell/ipc/ipc_transport.py` disposition=`drop` rank=`16` total_score=`64.11` risk=`HIGH`
- `src/diag/repro_bundle_builder.py` disposition=`drop` rank=`17` total_score=`62.86` risk=`HIGH`
- `src/appshell/ipc/ipc_client.py` disposition=`drop` rank=`18` total_score=`61.73` risk=`HIGH`
- `src/appshell/ipc/ipc_endpoint_server.py` disposition=`drop` rank=`19` total_score=`56.73` risk=`HIGH`
- `src/release/update_resolver.py` disposition=`drop` rank=`20` total_score=`54.29` risk=`HIGH`
- `src/security/trust/license_capability.py` disposition=`drop` rank=`21` total_score=`49.77` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/CLIENT_IDE_START_POINTS.md, docs/app/CLIENT_READONLY_INTEGRATION.md, docs/app/CLI_CONTRACTS.md, docs/app/COMPATIBILITY_ENFORCEMENT.md, docs/app/OBSERVABILITY_PIPELINES.md, docs/app/README.md, docs/app/TOOLS_OBSERVABILITY.md, docs/architecture/AI_INTENT_MODEL.md`

## Tests Involved

- `python tools/appshell/tool_run_ipc_unify.py --repo-root .`
- `python tools/appshell/tool_run_supervisor_hardening.py --repo-root .`
- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/security/tool_run_trust_strict_suite.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
