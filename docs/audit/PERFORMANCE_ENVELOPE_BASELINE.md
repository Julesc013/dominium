Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: PERFORMANCE/CI
Replacement Target: release-series performance baselines with retained regression history and per-target budgets

# Performance Envelope Baseline

## Baseline Metrics For Tier 1 Platform

- platform_tag: `win64`
- report_fingerprint: `f2d73a03bbb6324d0ba3f4105238ac263f7f41ea36b1f254ebce1fbc7045085b`
- portable_full_bundle_mb: `29.60`
- clean_room_elapsed_ms: `6112`

## Declared Targets

- `base_pack_bundle_mb` = `4`
- `clean_room_seconds` = `15.0`
- `client_memory_mb` = `128`
- `client_startup_seconds` = `5.0`
- `full_component_count` = `24`
- `idle_client_cpu_percent` = `1.0`
- `idle_server_cpu_percent` = `1.0`
- `minimal_server_profile_mb` = `48`
- `pack_lock_kb` = `8`
- `portable_full_bundle_mb` = `64`
- `server_memory_mb` = `128`
- `server_startup_seconds` = `5.0`
- `setup_startup_seconds` = `5.0`
- `store_lookup_latency_ms` = `10`

## Known Risks

- GUI first-paint timing is still proxied through CLI-safe surfaces in v0.0.0-mock.
- Idle CPU sampling is a loopback proxy because supervised children exit after startup in the current mock runtime.
- Store lookup latency is a local SSD file-open/read proxy rather than a dedicated long-running store service benchmark.

## Readiness

- ARCHIVE-POLICY-0: ready
- DIST-7 packaging guardrail inputs: ready
