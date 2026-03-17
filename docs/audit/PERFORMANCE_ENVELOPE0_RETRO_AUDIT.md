Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PERFORMANCE/CI
Replacement Target: release-pinned platform performance baselines with retained historical measurements

# PERFORMANCE-ENVELOPE-0 Retro Audit

## Primary Platform

- Tier 1 baseline target: `os.winnt + arch.x86_64 + abi.msvc`

## Startup Baseline

- setup startup proxy (`bin/setup help`): `1178` ms
- client startup proxy (`bin/client compat-status`): `1054` ms
- server startup proxy (`bin/server compat-status`): `937` ms
- clean-room end-to-end: `8121` ms
- clean-room result: `refused`

## Resource Baseline

- client peak working set: `50.37` MB
- server peak working set: `50.55` MB
- idle client CPU proxy: `0%`
- idle server CPU proxy: `0%`
- idle proxy note: `loopback_supervisor_children_exit_after_startup_probe`

## Storage Baseline

- portable full bundle: `29.60` MB
- minimal server profile: `30.64` MB
- store footprint: `0.08` MB
- base pack bundle: `0.00` MB
- default pack lock: `4.86` KB

## Graph And Store Shape

- default install.profile.full component count: `18`
- component graph size: `18` components / `30` edges
- store hash lookup latency proxy: `3` ms

## Tick And Idle Notes

- server config id: `server.mvp_default`
- proof_anchor_interval_ticks: `4`
- default tick rate: unpinned in current release metadata
- note: default tick rate is not explicitly pinned in the current release surface; only proof anchor cadence is declared
