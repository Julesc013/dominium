Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: PERFORMANCE/CI
Replacement Target: channel-specific performance budgets and regression history after DIST-7 packaging

# Performance Report WIN64

- result: `complete`
- report_fingerprint: `f2d73a03bbb6324d0ba3f4105238ac263f7f41ea36b1f254ebce1fbc7045085b`
- observed_metric_fingerprint: `bd861a32488fb8a461943a190977e12f29b25b6b6690f3695ebd99ea0e9211cf`

## Startup

- setup_help_ms: `3487`
- client_compat_status_ms: `3623`
- server_compat_status_ms: `2942`
- launcher_compat_status_ms: `2490`
- clean_room_elapsed_ms: `19606`
- clean_room_result: `refused`

## Memory

- client_peak_working_set_mb: `64.02`
- server_peak_working_set_mb: `50.84`
- setup_peak_working_set_mb: `51.34`
- launcher_peak_working_set_mb: `50.83`
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
- clean_room_fingerprint: `c0063a54225779164e84d7d5a780a2f3dbe8b372f873c4c89340a635494eb2a0`
- replay_fingerprint: ``
- release_manifest_hash_unchanged: `true`
