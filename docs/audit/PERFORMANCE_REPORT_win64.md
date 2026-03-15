Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: PERFORMANCE/CI
Replacement Target: channel-specific performance budgets and regression history after DIST-7 packaging

# Performance Report WIN64

- result: `complete`
- report_fingerprint: `f2d73a03bbb6324d0ba3f4105238ac263f7f41ea36b1f254ebce1fbc7045085b`
- observed_metric_fingerprint: `92ff1d8098bc173451fbbed0b82ea1c51b7426635f163fc8ed5b81d7ed3b878f`

## Startup

- setup_help_ms: `3429`
- client_compat_status_ms: `1952`
- server_compat_status_ms: `1433`
- launcher_compat_status_ms: `1231`
- clean_room_elapsed_ms: `16016`
- clean_room_result: `refused`

## Memory

- client_peak_working_set_mb: `63.83`
- server_peak_working_set_mb: `50.65`
- setup_peak_working_set_mb: `51.05`
- launcher_peak_working_set_mb: `50.84`
- idle_proxy_note: `loopback_supervisor_children_exit_after_startup_probe`

## Storage

- portable_full_bundle_mb: `29.60`
- minimal_server_bundle_mb: `30.64`
- store_mb: `0.08`
- base_pack_bundle_mb: `0.00`
- default_pack_lock_kb: `4.86`
- store_lookup_latency_ms: `4`

## Graph And Determinism

- component_graph_component_count: `18`
- install_profile_full_component_count: `18`
- clean_room_fingerprint: `592b865316f757275e6b8b84d92807f35c0ff87244ecd8191f07ad9f904c3e3a`
- replay_fingerprint: ``
- release_manifest_hash_unchanged: `true`
