Status: DERIVED
Last Reviewed: 2026-03-31
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PI
Replacement Target: snapshot-anchored advanced capability matrix after final planning

# Pipe Dreams Matrix

## Advanced Concepts

| Concept | Category | Feasibility | Required series | Σ/Φ/Υ before Ζ? | Notes |
| --- | --- | --- | --- | --- | --- |
| `offscreen_validation_renderer` | `rendering` | `near` | `PHI, UPSILON` | `no` | Good candidate once render abstraction exists. |
| `release_rehearsal_production_like_sandbox` | `release_operations` | `near` | `OMEGA, UPSILON, SIGMA` | `no` | Maps well to current release and ecosystem verification foundations. |
| `safe_mode_degraded_boot` | `resilience` | `near` | `OMEGA, SIGMA` | `no` | Strong fit with existing explicit degrade/refusal model. |
| `trace_and_deterministic_replay_pairing` | `observability` | `near` | `OMEGA, SIGMA` | `no` | Replay discipline already exists; packaging it for operators is plausible. |
| `automatic_yanking_with_deterministic_downgrade` | `release_operations` | `medium` | `OMEGA, UPSILON, ZETA` | `yes` | Builds on update simulation and release policy. |
| `blue_green_services` | `runtime_replacement` | `medium` | `PHI, UPSILON, ZETA` | `yes` | Requires side-by-side services, routing control, and rollback policy. |
| `compatibility_scored_mod_insertion` | `mod_operations` | `medium` | `UPSILON, SIGMA, ZETA` | `yes` | Builds on pack compat and operator policy surfaces. |
| `component_warm_standby` | `runtime_replacement` | `medium` | `PHI, UPSILON, ZETA` | `yes` | Depends on lifecycle manager plus state export/import. |
| `debug_renderer_sidecar` | `rendering` | `medium` | `PHI, SIGMA, ZETA` | `yes` | Needs observer-safe sidecar boundaries. |
| `live_asset_streaming` | `runtime_streaming` | `medium` | `PHI, UPSILON, ZETA` | `yes` | Needs asset pipeline, non-blocking save coordination, and content compatibility checks. |
| `live_feature_flag_profile_cutovers` | `governance_operations` | `medium` | `SIGMA, UPSILON, ZETA` | `yes` | Must remain profile-driven, never hidden mode switches. |
| `live_privilege_capability_revocation` | `trust_operations` | `medium` | `SIGMA, UPSILON, ZETA` | `yes` | Needs live authority context invalidation and deterministic client responses. |
| `live_trust_root_rotation` | `trust_operations` | `medium` | `UPSILON, ZETA` | `yes` | Needs online trust policy roll-forward and rollback. |
| `proof_anchor_health_monitor` | `resilience` | `medium` | `SIGMA, UPSILON, ZETA` | `yes` | Natural extension of proof-backed rollback and audit surfaces. |
| `runtime_drift_detection` | `resilience` | `medium` | `SIGMA, UPSILON, ZETA` | `yes` | Repo drift immunity should evolve into live runtime attestation. |
| `shadow_service_startup_and_cutover` | `runtime_replacement` | `medium` | `PHI, UPSILON, ZETA` | `yes` | One of the most plausible early Z capabilities after componentization. |
| `world_streaming_without_loading_screens` | `runtime_streaming` | `medium` | `PHI, ZETA` | `yes` | Needs streaming-safe state partitions, scheduler awareness, and deterministic asset staging. |
| `attested_service_replacement` | `runtime_replacement` | `long` | `PHI, UPSILON, ZETA` | `yes` | Replacement flow must be signed, measured, and replay-verifiable. |
| `checkpoint_and_event_tail_sync` | `distributed_runtime` | `long` | `PHI, UPSILON, ZETA` | `yes` | Needs WAL-like event tails with deterministic replay joins. |
| `cluster_wide_proof_anchor_verification` | `distributed_runtime` | `long` | `SIGMA, UPSILON, ZETA` | `yes` | Needs distributed proof aggregation and operator health policy. |
| `deterministic_distributed_simulation` | `distributed_runtime` | `long` | `PHI, UPSILON, ZETA` | `yes` | Requires deterministic replication, partition proofs, and authority handoff. |
| `deterministic_replicated_simulation` | `distributed_runtime` | `long` | `PHI, UPSILON, ZETA` | `yes` | Core Z ambition; gated on componentized runtime and state isolation. |
| `isolation_boundaries_for_untrusted_mods` | `mod_operations` | `long` | `SIGMA, PHI, UPSILON, ZETA` | `yes` | Requires module sandboxing, capability mediation, and pack policy hardening. |
| `live_logic_network_recompilation` | `runtime_replacement` | `long` | `PHI, UPSILON, ZETA` | `yes` | Requires compile/runtime split plus safe cutover of logic graphs. |
| `live_protocol_upgrades` | `protocol_operations` | `long` | `SIGMA, PHI, UPSILON, ZETA` | `yes` | Multi-version protocol negotiation must survive live cutover. |
| `mod_abi_compatibility_layers` | `mod_operations` | `long` | `PHI, UPSILON, ZETA` | `yes` | Needs a stabilized module ABI and compatibility shims. |
| `snapshot_isolation_for_all_mutable_state` | `data_governance` | `long` | `PHI, UPSILON, ZETA` | `yes` | A database-grade foundation, not a light feature. |
| `stateful_service_mirroring` | `distributed_runtime` | `long` | `PHI, UPSILON, ZETA` | `yes` | Requires deterministic replication and mirrored state export. |
| `live_schema_evolution` | `data_governance` | `speculative` | `SIGMA, PHI, UPSILON, ZETA` | `yes` | Would require lawful online migration plus universal schema negotiation. |
| `multi_render_backend_mirrored_execution` | `rendering` | `speculative` | `PHI, ZETA` | `no` | Possible only after renderer virtualization and side-by-side backend scheduling. |
| `restartless_core_engine_replacement` | `runtime_replacement` | `speculative` | `SIGMA, PHI, UPSILON, ZETA` | `yes` | Needs stable kernel state export and proof-backed replacement choreography. |

