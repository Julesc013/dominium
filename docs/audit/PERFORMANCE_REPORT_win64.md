Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: PERFORMANCE/CI
Replacement Target: channel-specific performance budgets and regression history after DIST-7 packaging

# Performance Report WIN64

- result: `complete`
- report_fingerprint: `f2d73a03bbb6324d0ba3f4105238ac263f7f41ea36b1f254ebce1fbc7045085b`
- observed_metric_fingerprint: `c0aa0bc7a0b07da038716281962c7e0ea62271349aa6218ef716ebf7ea72f6eb`

## Startup

- setup_help_ms: `1674`
- client_compat_status_ms: `1589`
- server_compat_status_ms: `1624`
- launcher_compat_status_ms: `1010`
- clean_room_elapsed_ms: `5171`
- clean_room_result: `refused`

## Memory

- client_peak_working_set_mb: `64.13`
- server_peak_working_set_mb: `50.82`
- setup_peak_working_set_mb: `50.92`
- launcher_peak_working_set_mb: `50.64`
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
- clean_room_fingerprint: `c8772c4ed34917637be19055fc44b75229df87b739c453460a249d84278e9c2b`
- replay_fingerprint: ``
- release_manifest_hash_unchanged: `true`
