Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: PERFORMANCE/CI
Replacement Target: channel-specific performance budgets and regression history after DIST-7 packaging

# Performance Report WIN64

- result: `complete`
- report_fingerprint: `f2d73a03bbb6324d0ba3f4105238ac263f7f41ea36b1f254ebce1fbc7045085b`
- observed_metric_fingerprint: `0e951bf5ae1da4f2f6f2c936b3c8c9f676cce03a630b54a1105547e88bcef723`

## Startup

- setup_help_ms: `3862`
- client_compat_status_ms: `1517`
- server_compat_status_ms: `882`
- launcher_compat_status_ms: `935`
- clean_room_elapsed_ms: `6112`
- clean_room_result: `refused`

## Memory

- client_peak_working_set_mb: `63.95`
- server_peak_working_set_mb: `50.96`
- setup_peak_working_set_mb: `51.03`
- launcher_peak_working_set_mb: `50.86`
- idle_proxy_note: `loopback_supervisor_children_exit_after_startup_probe`

## Storage

- portable_full_bundle_mb: `29.60`
- minimal_server_bundle_mb: `30.64`
- store_mb: `0.08`
- base_pack_bundle_mb: `0.00`
- default_pack_lock_kb: `4.86`
- store_lookup_latency_ms: `3`

## Graph And Determinism

- component_graph_component_count: `18`
- install_profile_full_component_count: `18`
- clean_room_fingerprint: `4013449c61e025f7b743bb3808bfb2e09dabc833adf37a5eaeb52033c782acef`
- replay_fingerprint: ``
- release_manifest_hash_unchanged: `true`
