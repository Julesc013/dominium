Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: release tool reference regenerated from TOOL-SURFACE-0 tooling

# Tool Reference

Use the stable umbrella form:

```text
dom <area> <command> ...
```

## `geo`

Deterministic GEO replay, identity, overlay, and metric tooling.

- `dom geo explain-property-origin`: Explain deterministic GEO-9 property provenance for an object/property path
- `dom geo generate-geo-stress`: Generate deterministic GEO-10 stress scenario payloads
- `dom geo replay-field-geo-window`: Verify GEO-4 field replay windows preserve GEO-keyed field hash surfaces
- `dom geo replay-frame-window`: Verify GEO-2 frame graph and position transforms are stable across replay
- `dom geo replay-geo-window`: Replay GEO-10 stress windows and verify GEO proof surfaces remain stable
- `dom geo replay-geometry-window`: Verify GEO-7 geometry edit replay determinism
- `dom geo replay-overlay-merge`: Verify GEO-9 overlay merge replay determinism
- `dom geo replay-path-request`: Verify GEO-6 path queries replay deterministically
- `dom geo replay-view-window`: Verify GEO-5 projected views replay deterministically under lens gating
- `dom geo replay-worldgen-cell`: Verify GEO-8 worldgen replay determinism for canonical cell requests
- `dom geo run-geo-stress`: Run the deterministic GEO-10 stress harness and verify repeated-run stability
- `dom geo verify-id-stability`: Verify GEO-1 cell-key and object-ID stability for deterministic fixtures
- `dom geo verify-metric-stability`: Verify GEO-3 metric query stability for deterministic fixtures
- `dom geo verify-overlay-identity`: Verify GEO-10 overlay application preserves stable object identities
- `dom geo verify-sol-pin-overlay`: Verify the Sol minimal pin overlay against the canonical MVP runtime identity

## `worldgen`

World generation replay, verification, and stress helpers.

- `dom worldgen generate-worldgen-baseline`: Generate the Omega worldgen lock baseline snapshot
- `dom worldgen replay-climate-window`: Verify EARTH-2 seasonal climate replay determinism
- `dom worldgen replay-galaxy-objects`: Verify GAL-1 galaxy object replay determinism
- `dom worldgen replay-galaxy-proxies`: Verify GAL-0 galaxy-proxy replay determinism
- `dom worldgen replay-hydrology-window`: Verify EARTH-1 hydrology-window replay determinism
- `dom worldgen replay-illumination-view`: Compatibility wrapper for SOL-1 illumination replay determinism
- `dom worldgen replay-material-proxy-window`: Verify EARTH-10 material-proxy replay determinism
- `dom worldgen replay-refinement-window`: Verify MW-4 refinement-window replay determinism
- `dom worldgen replay-sky-view`: Verify EARTH-4 sky replay determinism
- `dom worldgen replay-system-instantiation`: Verify MW-1 star-system instantiation replay determinism
- `dom worldgen replay-system-l2`: Verify MW-2 L2 star and planet instantiation replay determinism
- `dom worldgen replay-tide-window`: Verify EARTH-3 tide replay determinism
- `dom worldgen replay-water-view`: Verify EARTH-8 water-view replay determinism
- `dom worldgen replay-wind-window`: Verify EARTH-7 wind replay determinism
- `dom worldgen run-refinement-stress`: Run the MW-4 rapid-teleport and ROI-thrash stress fixture
- `dom worldgen verify-earth-surface`: Verify EARTH-0 far-LOD surface consistency without renderer dependencies
- `dom worldgen verify-worldgen-lock`: Verify the Omega worldgen lock against the committed baseline snapshot

## `earth`

Earth-focused replay, stress, and verification tools.

- `dom earth generate-earth-mvp-stress`: Generate deterministic EARTH-9 MVP stress scenario payloads
- `dom earth replay-climate-window`: Verify EARTH-2 seasonal climate replay determinism
- `dom earth replay-earth-physics-window`: Replay deterministic EARTH-9 movement and terrain-contact windows
- `dom earth replay-earth-view-window`: EARTH-9 view replay determinism wrapper for sky, illumination, water, and map artifacts
- `dom earth replay-hydrology-window`: Verify EARTH-1 hydrology-window replay determinism
- `dom earth replay-illumination-view`: Compatibility wrapper for SOL-1 illumination replay determinism
- `dom earth replay-material-proxy-window`: Verify EARTH-10 material-proxy replay determinism
- `dom earth replay-sky-view`: Verify EARTH-4 sky replay determinism
- `dom earth replay-tide-window`: Verify EARTH-3 tide replay determinism
- `dom earth replay-water-view`: Verify EARTH-8 water-view replay determinism
- `dom earth replay-wind-window`: Verify EARTH-7 wind replay determinism
- `dom earth run-earth-mvp-stress`: Run the deterministic EARTH-9 MVP stress harness

## `sol`

Illumination and orbital proxy replay tooling.

- `dom sol replay-illumination-view`: Replay deterministic SOL-1 illumination geometry windows and verify fingerprints
- `dom sol replay-orbit-view`: Replay deterministic SOL-2 orbit-view windows and verify fingerprints

## `gal`

Galaxy proxy and compact-object replay tooling.

- `dom gal replay-galaxy-objects`: Verify GAL-1 galaxy object replay determinism
- `dom gal replay-galaxy-proxies`: Verify GAL-0 galaxy-proxy replay determinism

## `logic`

Logic replay, compile, and stress tooling.

- `dom logic generate-logic-stress`: Generate deterministic LOGIC-10 stress scenario packs
- `dom logic replay-compiled-logic-window`: Replay LOGIC windows through L1 and compiled paths and compare output/state hashes
- `dom logic replay-fault-window`: Replay a deterministic LOGIC-8 fault/noise/security window and summarize proof hashes
- `dom logic replay-logic-window`: Replay a deterministic LOGIC-4 evaluation window and summarize proof hashes
- `dom logic replay-protocol-window`: Replay a deterministic LOGIC-9 protocol window and summarize protocol proof hashes
- `dom logic replay-timing-window`: Replay a deterministic LOGIC-5 timing window and summarize timing hashes
- `dom logic replay-trace-window`: Replay a deterministic LOGIC-7 debug window and summarize trace proof hashes
- `dom logic run-logic-compile-stress`: Run a deterministic LOGIC-6 compile/collapse stress scenario and summarize compiled parity
- `dom logic run-logic-debug-stress`: Run a deterministic LOGIC-7 debug stress scenario and summarize bounded trace behavior
- `dom logic run-logic-eval-stress`: Run a deterministic uncompiled LOGIC-4 stress scenario and summarize hashes
- `dom logic run-logic-fault-stress`: Run a deterministic LOGIC-8 fault/noise/security stress scenario
- `dom logic run-logic-protocol-stress`: Run a deterministic LOGIC-9 protocol contention stress scenario
- `dom logic run-logic-stress`: Run the deterministic LOGIC-10 stress envelope across scale, compile, timing, protocol, fault, and debug lanes
- `dom logic run-logic-timing-stress`: Run a deterministic LOGIC-5 timing stress scenario and summarize timing hashes
- `dom logic verify-compiled-vs-l1`: Verify deterministic compiled-vs-L1 parity for bounded LOGIC fixtures

## `sys`

System composition replay, explain, and stress tooling.

- `dom sys generate-sys-stress`: SYS-8 deterministic stress scenario generator
- `dom sys replay-capsule-window`: Verify SYS-2 macro capsule replay hashes across a deterministic state window
- `dom sys replay-certification-window`: Verify SYS-5 certification replay hashes across deterministic state windows
- `dom sys replay-sys-window`: Verify SYS-8 replay windows reproduce deterministic SYS proof hash chains
- `dom sys replay-system-failure-window`: Verify SYS-6 reliability replay hashes across deterministic state windows
- `dom sys replay-tier-transitions`: Verify SYS-3 tier transition replay hashes across deterministic windows
- `dom sys run-sys-stress`: SYS-8 deterministic stress harness
- `dom sys template-browser`: SYS-4 developer template browser/instantiation CLI
- `dom sys verify-explain-determinism`: Verify SYS-7 system forensics explain determinism over a state window
- `dom sys verify-statevec-roundtrip`: Verify STATEVEC-0 deterministic serialize/deserialize roundtrip stability
- `dom sys verify-template-reproducible`: Verify SYS-4 template compilation is deterministic and reproducible

## `proc`

Process, capsule, and drift replay tooling.

- `dom proc generate-proc-stress`: PROC-9 deterministic process stress scenario generator
- `dom proc replay-capsule-window`: Verify deterministic replay hashes for PROC-5 process capsule windows
- `dom proc replay-drift-window`: Verify deterministic replay hashes for PROC-6 drift/revalidation outcomes
- `dom proc replay-experiment-window`: Verify deterministic replay hashes for PROC-7 experiment/result windows
- `dom proc replay-maturity-window`: Verify deterministic replay hashes for PROC-4 maturity outcomes
- `dom proc replay-pipeline-window`: Verify deterministic replay hashes for PROC-8 software pipeline windows
- `dom proc replay-proc-window`: Verify deterministic replay hashes for PROC-9 process windows
- `dom proc replay-process-window`: Verify deterministic process-run replay hashes over a state payload window
- `dom proc replay-qc-window`: Verify deterministic replay hashes for PROC-3 QC sampling outcomes
- `dom proc replay-quality-window`: Verify deterministic process quality replay hashes over a state payload window
- `dom proc replay-reverse-engineering-window`: Verify deterministic replay hashes for PROC-7 reverse-engineering windows
- `dom proc run-proc-stress`: PROC-9 deterministic stress harness
- `dom proc verify-proc-compaction`: Compact PROC derived artifacts and verify replay from compaction anchors

## `pack`

Pack inventory, verification, and capability inspection commands.

- `dom pack build-lock`: Verify packs offline and emit a deterministic pack lock plus compatibility report.
- `dom pack capability-inspect`: Inspect declared pack capabilities, overlaps, and dependency closure.
- `dom pack list`: List available pack manifests in deterministic order.
- `dom pack migrate-capability-gating`: Run the legacy capability gating migration helper through the stable umbrella.
- `dom pack validate-manifest`: Run the legacy pack manifest validator through the stable umbrella.
- `dom pack verify`: Run the offline pack compatibility verification pipeline.

## `lib`

Library bundle and save verification tooling.

- `dom lib generate-lib-stress`: Generate the deterministic LIB-7 library stress scenario workspace
- `dom lib replay-save-open`: Replay deterministic save-open policy decisions and optionally verify a recorded decision
- `dom lib run-lib-stress`: Run the deterministic LIB-7 library stress harness
- `dom lib run-store-gc`: Run deterministic STORE-GC-0 baseline generation
- `dom lib store-verify`: Run deterministic store verification and write STORE-GC-0 verify outputs
- `dom lib verify-bundle`: Verify deterministic LIB-6 bundles offline

## `compat`

Capability negotiation descriptors, replay, and interop tooling.

- `dom compat apply-migration`: Apply deterministic migration lifecycle actions for a single artifact
- `dom compat emit-descriptor`: Emit deterministic CAP-NEG-1 endpoint descriptors for product surfaces
- `dom compat generate-descriptor-manifest`: Generate deterministic offline descriptor manifest from dist/bin wrappers
- `dom compat generate-interop-matrix`: Generate the deterministic CAP-NEG-4 synthetic interoperability matrix
- `dom compat plan-migration`: Plan deterministic migration lifecycle actions for a single artifact
- `dom compat replay-migration`: Replay deterministic PACK-COMPAT-2 artifact migrations
- `dom compat replay-negotiation`: Replay deterministic endpoint negotiation from recorded or default descriptors
- `dom compat run-interop-stress`: Run the deterministic CAP-NEG-4 interoperability stress harness
- `dom compat run-migration-lifecycle`: Generate deterministic MIGRATION-LIFECYCLE-0 report artifacts
- `dom compat status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.

## `diag`

Repro bundle capture, snapshot, and replay tooling.

- `dom diag capture`: Write a deterministic DIAG-0 repro bundle with logs, proof anchors, canonical events, and pinned runtime inputs.
- `dom diag replay-bundle`: Replay a DIAG-0 repro bundle and verify deterministic hashes
- `dom diag snapshot`: Write a deterministic offline diagnostic snapshot bundle with descriptor, logs, and proof anchors.

## `server`

Server replay and inspection tooling.

- `dom server compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `dom server console`: Alias of `console enter` for deterministic REPL console access.
- `dom server descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
- `dom server replay-local-singleplayer`: Verify SERVER-MVP-1 local singleplayer orchestration replay
- `dom server replay-server-window`: Verify SERVER-MVP-0 deterministic tick, loopback, and proof-anchor replay

## `client`

Client-facing AppShell inspection commands.

- `dom client compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `dom client console`: Alias of `console enter` for deterministic REPL console access.
- `dom client descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
