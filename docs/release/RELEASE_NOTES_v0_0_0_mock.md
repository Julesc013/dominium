Status: CANONICAL
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DIST
Replacement Target: tagged mock-release notes once RELEASE-3 freeze completes

# Release Notes v0.0.0-mock

## Included

- deterministic simulation kernel and truth/process/law architecture
- GEO, MW, SOL, EARTH, LOGIC, SYS, PROC, POLL MVP surfaces
- AppShell bootstrap, CLI/TUI/rendered mode resolution, IPC, supervisor, and virtual paths
- pack compatibility, capability negotiation, install discovery, release manifests, and offline verification
- proof/replay, time anchors, smoke/stress gates, and audit/validation governance

## Out Of Scope

- chemistry, real fluid volumes, vehicles, crafting, economy, combat
- N-body physics, real ephemerides, stellar lifecycle, and dynamic supernova simulation
- native GUI completeness on all platforms
- signed release distribution requirements beyond optional detached mock signing

## Verification

- `python bin/setup verify --release-manifest manifests/release_manifest.json`
- `python bin/launcher compat-status`
- `python bin/client --descriptor`
- `python bin/server --descriptor`

## Compatibility

- mix-and-match compatibility is governed by CAP-NEG
- contract or pack-lock drift must refuse or degrade explicitly
- silent fallback is forbidden

## Stability Summary

- frozen semantic contracts remain governed by the current semantic contract registry
- provisional systems remain tagged through META-STABILITY and are not guaranteed permanent
