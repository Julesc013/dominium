Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: PERFORMANCE/CI
Replacement Target: release-series performance budgets with per-target historical regression lanes

# Performance Envelope v0.0.0-mock

## Scope

- Applies to standalone portable bundles, installed mode, singleplayer, and local server/client loopback on Tier 1 win64.
- This envelope is declarative guardrail policy, not an optimization or scheduling feature.

## Startup Targets

- Setup cold startup proxy (`bin/setup help`) <= `5.0` s
- Client startup to governed main-menu equivalent proxy (`bin/client compat-status`) <= `5.0` s
- Server startup proxy (`bin/server compat-status`) <= `5.0` s
- Clean-room end-to-end acceptance lane <= `15.0` s

## Idle Resource Targets

- Idle server CPU proxy <= `1.0` %
- Idle client CPU proxy <= `1.0` %
- Client peak working set <= `128` MB
- Server peak working set <= `128` MB

## Storage Targets

- Portable full bundle <= `64` MB
- Minimal server profile <= `48` MB
- Base pack bundle <= `4` MB

## Graph And Store Targets

- Default install.profile.full component count <= `24`
- Default pack lock size <= `8` KB
- Store hash lookup latency proxy <= `10` ms on local SSD baseline

## Determinism Guarantees

- Performance probes must not modify canonical release manifests or semantic fingerprints.
- Bundle execution used for measurement must run against disposable probe copies.
- Hashes and proof/replay anchors remain governed by RELEASE, DIST, and DIAG contracts; this envelope only observes them.

## Known Limits

- v0.0.0-mock does not expose a stable GUI first-paint benchmark surface, so client startup is measured through the governed compat-status proxy.
- Loopback supervisor children exit after the startup probe in the current mock lane, so idle CPU is recorded as an explicit proxy value rather than a long-lived resident sample.
