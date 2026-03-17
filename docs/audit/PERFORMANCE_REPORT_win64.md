Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PERFORMANCE/CI
Replacement Target: channel-specific performance budgets and regression history after DIST-7 packaging

# Performance Report WIN64

- result: `complete`
- report_fingerprint: `f2d73a03bbb6324d0ba3f4105238ac263f7f41ea36b1f254ebce1fbc7045085b`
- observed_metric_fingerprint: `e899e774da1406c0376362b38fec3aedac69ca9e907c3b2a53d15fd19384179c`

## Startup

- setup_help_ms: `1178`
- client_compat_status_ms: `1054`
- server_compat_status_ms: `937`
- launcher_compat_status_ms: `987`
- clean_room_elapsed_ms: `8121`
- clean_room_result: `refused`

## Memory

- client_peak_working_set_mb: `50.37`
- server_peak_working_set_mb: `50.55`
- setup_peak_working_set_mb: `51.02`
- launcher_peak_working_set_mb: `50.91`
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
- clean_room_fingerprint: `42a096ffa41611da67e5a0e79af0ba5b4e49c86c1ddbb3b169ac6c926fef92c3`
- replay_fingerprint: ``
- release_manifest_hash_unchanged: `true`
