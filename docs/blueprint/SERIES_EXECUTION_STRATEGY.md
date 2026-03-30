Status: DERIVED
Last Reviewed: 2026-03-31
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PI
Replacement Target: snapshot-anchored execution strategy after final repository re-audit

# Series Execution Strategy

## Current Boundary

This document is the post-XI master sequencing plan for SIGMA, PHI, UPSILON, and ZETA.
It is planning only and anchors itself to the live Xi-8 and OMEGA-frozen repository, while still requiring fresh snapshot remapping before any repo-specific PHI, UPSILON wiring, or ZETA implementation begins.

## Current Grounding

- Architecture graph v1 fingerprint: `ff1c955301dd733e8269f2ec3c5052de98c705a6a1d487990fb6d6e45e2da5ea`
- Module boundary rules fingerprint: `e7bdd052713a81dafbf5a0397794af6e70929cfdea49f3308e5507db58ee0ee8`
- Repository structure lock fingerprint: `6207b3e71bd604ddee58bc2d95a840833fde33b046ceb1d640530530fa9dc231`
- Xi artifact state: XI_0, XI_1, XI_2, XI_3, XI_4, XI_5, XI_6, XI_7, XI_8
- OMEGA artifact state: OMEGA_0, OMEGA_10
- CI STRICT result: `complete` via profile `STRICT`
- Sanctioned source-like roots carried by policy: `4`

## Series Order

| Rank | Series | Why It Starts Here | Overlap |
| --- | --- | --- | --- |
| `0` | `SIGMA` | Governance, operator policy, and validation mapping must exist before aggressive automation or live cutovers. | UPSILON |
| `1` | `UPSILON` | Release control, rollback policy, and deterministic distribution govern every later replacement workflow. | SIGMA, PHI |
| `2` | `PHI` | Componentization is required for replaceability, but exact insertion points must wait for the fresh snapshot mapping. | SIGMA, UPSILON |
| `3` | `ZETA` | Live runtime operations are downstream of governance, control-plane, and runtime component foundations. | none |

## Priority Bands

### Priority 0 - Must happen before any live-runtime ambitions

- `SIGMA.0_agent_governance`: Mirror AGENTS governance into stable machine-readable workflows before automation expands. [SIGMA / phase A].
- `SIGMA.1_agent_mirrors`: Create mirrored operator and agent surfaces so governance is inspectable from both human and tool paths. [SIGMA / phase A].
- `SIGMA.2_natural_language_task_bridge`: Bind natural-language tasks to deterministic task types, validations, and refusal paths. [SIGMA / phase A].
- `PHI.0_runtime_kernel_model`: Freeze the kernel doctrine for services, truth separation, and lawful state movement. [PHI / phase B].
- `PHI.1_component_model`: Define component boundaries, identity, lifecycle hooks, and state ownership expectations. [PHI / phase B].
- `PHI.2_module_loader`: Introduce capability-negotiated module loading only after exact insertion points are mapped. [PHI / phase B].
- `PHI.3_runtime_services`: Separate service responsibilities from the kernel without violating process-only mutation. [PHI / phase B].
- `PHI.4_state_externalization`: Model export/import, state ownership, and replay-safe transfer boundaries before live cutovers. [PHI / phase B].
- `UPSILON.0_build_graph_lock`: Lock the build graph so later control-plane work has a deterministic substrate. [UPSILON / phase C].
- `UPSILON.1_preset_toolchain_consolidation`: Consolidate execution presets and toolchains into a governed release surface. [UPSILON / phase C].
- `UPSILON.2_versioning_policy`: Freeze release numbering, compatibility, and migration obligations before rollout automation. [UPSILON / phase C].
- `UPSILON.3_release_index_policy_refinement`: Refine release indexing and publication semantics before live control-plane work. [UPSILON / phase C].

### Priority 1 - Makes controlled live replacement possible

- `PHI.5_lifecycle_manager`: Add governed startup, shutdown, handoff, and rollback choreography for runtime services. [PHI / phase B].
- `UPSILON.4_release_transaction_log`: Record rollout, downgrade, and rollback intent in a deterministic control-plane ledger. [UPSILON / phase C].
- `UPSILON.5_canary_blue_green_rollout_policy`: Govern staged exposure, quarantine, and reversal before live cutovers. [UPSILON / phase C].
- `UPSILON.6_disaster_downgrade_policy`: Define rollback, yank, and degraded boot discipline before higher-risk replacement work. [UPSILON / phase C].
- `PHI.6_framegraph`: Separate render intent from backend execution so renderer replacement becomes testable. [PHI / phase D].
- `PHI.7_render_device_abstraction`: Introduce a governed device abstraction before backend swap or mirrored execution work. [PHI / phase D].
- `PHI.8_hotswap_boundaries`: Define replacement boundaries and state handoff contracts before any live replacement feature work. [PHI / phase D].

### Priority 2 - Makes advanced Z capabilities possible

- `PHI.10_sandboxing`: Introduce controlled isolation before untrusted mod or sidecar work. [PHI / phase D].
- `PHI.11_multi_version_coexistence`: Support controlled version overlap before live protocol, ABI, or content cutovers. [PHI / phase D].
- `PHI.9_asset_pipeline`: Stabilize asset and shader ingestion before live mount, streaming, or mirrored execution. [PHI / phase D].
- `ZETA.0_early_replaceability_features`: Enable service restarts, controlled replacement, and shadow cutovers only after A, B, and C complete. [ZETA / phase D].
- `ZETA.1_content_live_mount_unmount`: Allow pack mount and unmount only after compatibility, rollback, and isolation controls exist. [ZETA / phase D].
- `ZETA.2_mirrored_execution_sidecars`: Add side-by-side validation services after service boundaries and proof hooks are frozen. [ZETA / phase D].

### Priority 3 - Distributed and extreme operations

- `ZETA.3_distributed_simulation`: Expand to deterministic distributed runtime only after replay, handoff, and quorum proofs exist. [ZETA / phase E].
- `ZETA.4_live_shard_relocation`: Move state across shards only after deterministic replication and authority handoff are proven. [ZETA / phase E].
- `ZETA.5_protocol_schema_live_evolution`: Evolve protocol and schema live only after version coexistence and rollback proofs are stable. [ZETA / phase E].
- `ZETA.6_restartless_core_engine_replacement`: Treat core replacement as a last-stage research problem, not an early delivery target. [ZETA / phase E].
- `ZETA.7_cluster_of_clusters`: Consider cluster-of-clusters only after deterministic distributed simulation is already boring and proven. [ZETA / phase E].

## Foundation-ready

- `compatibility_governed_update_rehearsal`: phase `C`, required foundations `OMEGA.baseline_universe, OMEGA.ecosystem_verify, OMEGA.update_sim, UPSILON.release_rehearsal_controller, UPSILON.release_transaction_log, UPSILON.versioning_policy`.
- `proof_backed_rollback_and_replay`: phase `C`, required foundations `OMEGA.baseline_universe, OMEGA.disaster_suite, SIGMA.architecture_governance_mirror, SIGMA.validation_mapping, UPSILON.release_transaction_log`.
- `safe_mode_degraded_boot`: phase `C`, required foundations `OMEGA.baseline_gameplay, OMEGA.baseline_universe, OMEGA.trust_strict, SIGMA.architecture_governance_mirror, SIGMA.operator_policy_model, UPSILON.disaster_downgrade_policy`.
- `offscreen_validation_renderer`: phase `C`, required foundations `PHI.asset_pipeline, PHI.component_model, PHI.framegraph, PHI.render_device, UPSILON.build_graph_lock, UPSILON.release_transaction_log`.
- `release_rehearsal_sandbox`: phase `C`, required foundations `OMEGA.baseline_universe, OMEGA.ecosystem_verify, OMEGA.update_sim, SIGMA.architecture_governance_mirror, SIGMA.operator_policy_model, UPSILON.release_rehearsal_controller, UPSILON.release_transaction_log`.
- `canary_mod_deployment`: phase `D`, required foundations `SIGMA.declarative_cutover_language, SIGMA.operator_policy_model, PHI.module_loader, UPSILON.canary_blue_green_policy, UPSILON.release_rehearsal_controller, UPSILON.release_transaction_log, UPSILON.versioning_policy, ZETA.live_pack_mount, ZETA.runtime_cutover_controller`.
- `debug_renderer_sidecar`: phase `D`, required foundations `SIGMA.architecture_governance_mirror, SIGMA.operator_policy_model, PHI.component_model, PHI.framegraph, PHI.hotswap_boundaries, PHI.render_device, ZETA.mirrored_execution_sidecars, ZETA.runtime_cutover_controller`.
- `deterministic_downgrade_and_yank`: phase `D`, required foundations `OMEGA.baseline_universe, OMEGA.trust_strict, OMEGA.update_sim, UPSILON.disaster_downgrade_policy, UPSILON.operator_release_controller, UPSILON.release_transaction_log, UPSILON.versioning_policy, ZETA.runtime_cutover_controller`.

## Future-plausible

- `distributed_shard_relocation`: phase `E`, required foundations `OMEGA.baseline_universe, OMEGA.disaster_suite, OMEGA.worldgen_lock, PHI.component_model, PHI.event_log, PHI.snapshot_service, PHI.state_partition_protocol, UPSILON.release_transaction_log, ZETA.authority_handoff_protocol, ZETA.cluster_failover_controller, ZETA.deterministic_replication, ZETA.proof_anchor_quorum, ZETA.runtime_cutover_controller`.
- `attested_service_replacement`: phase `D`, required foundations `OMEGA.trust_strict, PHI.component_model, PHI.lifecycle_manager, PHI.module_abi_boundary, PHI.service_registry, PHI.state_externalization, UPSILON.release_transaction_log, UPSILON.trust_distribution_policy, ZETA.runtime_cutover_controller`.
- `automatic_yanking_with_deterministic_downgrade`: phase `D`, required foundations `OMEGA.baseline_universe, OMEGA.trust_strict, OMEGA.update_sim, UPSILON.disaster_downgrade_policy, UPSILON.operator_release_controller, UPSILON.release_transaction_log, UPSILON.versioning_policy, ZETA.runtime_cutover_controller`.
- `blue_green_services`: phase `D`, required foundations `PHI.component_model, PHI.lifecycle_manager, PHI.service_registry, PHI.state_externalization, UPSILON.canary_blue_green_policy, UPSILON.disaster_downgrade_policy, UPSILON.release_transaction_log, ZETA.runtime_cutover_controller, ZETA.shadow_service_startup`.
- `compatibility_scored_mod_insertion`: phase `D`, required foundations `SIGMA.architecture_governance_mirror, SIGMA.operator_policy_model, PHI.module_loader, PHI.sandboxing, UPSILON.release_rehearsal_controller, UPSILON.release_transaction_log, UPSILON.versioning_policy, ZETA.live_pack_mount, ZETA.runtime_cutover_controller`.
- `component_warm_standby`: phase `D`, required foundations `PHI.component_model, PHI.lifecycle_manager, PHI.service_registry, PHI.state_externalization, UPSILON.canary_blue_green_policy, UPSILON.release_transaction_log, ZETA.runtime_cutover_controller, ZETA.shadow_service_startup`.
- `isolation_boundaries_for_untrusted_mods`: phase `D`, required foundations `OMEGA.trust_strict, SIGMA.architecture_governance_mirror, SIGMA.runtime_privilege_policy, PHI.component_model, PHI.module_abi_boundary, PHI.module_loader, PHI.sandboxing, UPSILON.release_transaction_log, UPSILON.trust_distribution_policy, UPSILON.versioning_policy, ZETA.runtime_cutover_controller`.
- `live_asset_streaming`: phase `D`, required foundations `PHI.asset_pipeline, PHI.component_model, PHI.lifecycle_manager, PHI.state_externalization, UPSILON.disaster_downgrade_policy, UPSILON.release_transaction_log, ZETA.live_pack_mount, ZETA.runtime_cutover_controller`.

## Not yet safe to implement

- `hot_swappable_renderers`: phase `D`, required foundations `PHI.component_model, PHI.framegraph, PHI.hotswap_boundaries, PHI.lifecycle_manager, PHI.render_device, PHI.state_externalization, UPSILON.disaster_downgrade_policy, UPSILON.release_transaction_log, ZETA.runtime_cutover_controller`.
- `live_protocol_upgrades`: phase `D`, required foundations `OMEGA.trust_strict, SIGMA.architecture_governance_mirror, SIGMA.contract_change_protocol, SIGMA.declarative_cutover_language, PHI.component_model, PHI.module_loader, PHI.multi_version_coexistence, PHI.state_externalization, UPSILON.disaster_downgrade_policy, UPSILON.migration_policy, UPSILON.release_transaction_log, UPSILON.versioning_policy, ZETA.runtime_cutover_controller`.
- `mod_hot_activation`: phase `D`, required foundations `PHI.module_loader, PHI.service_registry, UPSILON.disaster_downgrade_policy, UPSILON.release_transaction_log, UPSILON.versioning_policy, ZETA.live_pack_mount, ZETA.runtime_cutover_controller`.
- `partial_live_module_reload`: phase `D`, required foundations `SIGMA.architecture_governance_mirror, SIGMA.declarative_cutover_language, PHI.component_model, PHI.lifecycle_manager, PHI.module_abi_boundary, PHI.module_loader, PHI.state_externalization, UPSILON.disaster_downgrade_policy, UPSILON.release_transaction_log, ZETA.runtime_cutover_controller`.
- `renderer_virtualization`: phase `D`, required foundations `PHI.component_model, PHI.framegraph, PHI.hotswap_boundaries, PHI.render_device, ZETA.mirrored_execution_sidecars, ZETA.runtime_cutover_controller`.
- `snapshot_isolation_all_mutable_state`: phase `D`, required foundations `OMEGA.baseline_universe, OMEGA.disaster_suite, PHI.component_model, PHI.event_log, PHI.snapshot_service, PHI.state_externalization, PHI.state_partition_protocol, UPSILON.migration_policy, UPSILON.release_transaction_log, ZETA.runtime_cutover_controller`.

## How Work Should Be Executed

1. Docs and schemas first.
2. Registries and policy artifacts next.
3. Tooling and validators next.
4. Implementation only after validators exist.
5. Regression baselines and smoke harnesses before enabling by default.
6. Distribution and release only after convergence and archive checks.

## Capability-to-Foundation Highlights

| Capability | Phase | Foundations |
| --- | --- | --- |
| `distributed_shard_relocation` | `E` | OMEGA.baseline_universe, OMEGA.disaster_suite, OMEGA.worldgen_lock, PHI.component_model, PHI.event_log, PHI.snapshot_service, PHI.state_partition_protocol, UPSILON.release_transaction_log, ZETA.authority_handoff_protocol, ZETA.cluster_failover_controller, ZETA.deterministic_replication, ZETA.proof_anchor_quorum, ZETA.runtime_cutover_controller |
| `hot_swappable_renderers` | `D` | PHI.component_model, PHI.framegraph, PHI.hotswap_boundaries, PHI.lifecycle_manager, PHI.render_device, PHI.state_externalization, UPSILON.disaster_downgrade_policy, UPSILON.release_transaction_log, ZETA.runtime_cutover_controller |
| `live_protocol_upgrades` | `D` | OMEGA.trust_strict, SIGMA.architecture_governance_mirror, SIGMA.contract_change_protocol, SIGMA.declarative_cutover_language, PHI.component_model, PHI.module_loader, PHI.multi_version_coexistence, PHI.state_externalization, UPSILON.disaster_downgrade_policy, UPSILON.migration_policy, UPSILON.release_transaction_log, UPSILON.versioning_policy, ZETA.runtime_cutover_controller |
| `live_save_migration` | `D` | OMEGA.baseline_universe, OMEGA.disaster_suite, PHI.snapshot_service, PHI.state_externalization, UPSILON.migration_policy, UPSILON.release_transaction_log, ZETA.runtime_cutover_controller |
| `mod_hot_activation` | `D` | PHI.module_loader, PHI.service_registry, UPSILON.disaster_downgrade_policy, UPSILON.release_transaction_log, UPSILON.versioning_policy, ZETA.live_pack_mount, ZETA.runtime_cutover_controller |
| `partial_live_module_reload` | `D` | SIGMA.architecture_governance_mirror, SIGMA.declarative_cutover_language, PHI.component_model, PHI.lifecycle_manager, PHI.module_abi_boundary, PHI.module_loader, PHI.state_externalization, UPSILON.disaster_downgrade_policy, UPSILON.release_transaction_log, ZETA.runtime_cutover_controller |
| `release_rehearsal_sandbox` | `C` | OMEGA.baseline_universe, OMEGA.ecosystem_verify, OMEGA.update_sim, SIGMA.architecture_governance_mirror, SIGMA.operator_policy_model, UPSILON.release_rehearsal_controller, UPSILON.release_transaction_log |
| `restartless_core_engine_replacement` | `E` | OMEGA.trust_strict, SIGMA.architecture_governance_mirror, SIGMA.contract_change_protocol, PHI.component_model, PHI.lifecycle_manager, PHI.module_abi_boundary, PHI.runtime_kernel_model, PHI.state_externalization, UPSILON.disaster_downgrade_policy, UPSILON.release_transaction_log, ZETA.runtime_cutover_controller |
| `runtime_drift_detection` | `D` | OMEGA.baseline_universe, SIGMA.architecture_governance_mirror, SIGMA.validation_mapping, UPSILON.drift_attestation_pipeline, UPSILON.release_transaction_log, ZETA.runtime_cutover_controller |

