Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none

# CLI Reference

This reference is generated from `data/registries/command_registry.json` and
`data/registries/refusal_to_exit_registry.json`.

## Shared Commands

| Command | Description | Refusals |
| --- | --- | --- |
| `compat-status` | Run deterministic endpoint compatibility status and show negotiated mode plus disabled features. | `refusal.compat.contract_mismatch`, `refusal.compat.no_common_protocol`, `refusal.io.invalid_args` |
| `console` | Alias of `console enter` for deterministic REPL console access. | - |
| `descriptor` | Emit the CAP-NEG endpoint descriptor for the active product. | `refusal.io.invalid_args` |
| `diag` | Emit deterministic shell diagnostic metadata. | - |
| `dom` | List the stable Dominium tool namespaces and wrapped commands. | `refusal.io.invalid_args` |
| `help` | Show deterministic AppShell help generated from the command registry. | - |
| `packs` | Alias of `packs list` for deterministic pack enumeration. | `refusal.io.invalid_args` |
| `profiles` | Alias of `profiles list` for deterministic bundle enumeration. | - |
| `validate` | Run the unified validation pipeline through `validate --all`. | `refusal.io.invalid_args` |
| `verify` | Alias of `packs verify` for offline pack/profile verification. | `refusal.io.invalid_args`, `refusal.pack.contract_range_mismatch`, `refusal.pack.registry_missing`, `refusal.pack.schema_invalid`, `refusal.pack.trust_denied` |
| `version` | Emit deterministic product version metadata and build identity. | - |
| `console attach` | Attach to a local IPC console endpoint through CAP-NEG negotiation. | `refusal.connection.negotiation_mismatch`, `refusal.connection.no_negotiation`, `refusal.io.invalid_args`, `refusal.law.attach_denied` |
| `console detach` | Detach a logical local IPC console session. | `refusal.io.invalid_args` |
| `console enter` | Open the deterministic REPL console session stub for the current product. | - |
| `console sessions` | List discovered local IPC console endpoints in deterministic order. | `refusal.io.invalid_args` |
| `diag capture` | Write a deterministic DIAG-0 repro bundle with logs, proof anchors, canonical events, and pinned runtime inputs. | `refusal.io.invalid_args` |
| `diag snapshot` | Write a deterministic offline diagnostic snapshot bundle with descriptor, logs, and proof anchors. | `refusal.io.invalid_args` |
| `dom client` | Client-facing AppShell inspection commands. | `refusal.io.invalid_args` |
| `dom compat` | Capability negotiation descriptors, replay, and interop tooling. | `refusal.io.invalid_args` |
| `dom diag` | Repro bundle capture, snapshot, and replay tooling. | `refusal.io.invalid_args` |
| `dom earth` | Earth-focused replay, stress, and verification tools. | `refusal.io.invalid_args` |
| `dom gal` | Galaxy proxy and compact-object replay tooling. | `refusal.io.invalid_args` |
| `dom geo` | Deterministic GEO replay, identity, overlay, and metric tooling. | `refusal.io.invalid_args` |
| `dom lib` | Library bundle and save verification tooling. | `refusal.io.invalid_args` |
| `dom logic` | Logic replay, compile, and stress tooling. | `refusal.io.invalid_args` |
| `dom pack` | Pack inventory, verification, and capability inspection commands. | `refusal.io.invalid_args` |
| `dom proc` | Process, capsule, and drift replay tooling. | `refusal.io.invalid_args` |
| `dom server` | Server replay and inspection tooling. | `refusal.io.invalid_args` |
| `dom sol` | Illumination and orbital proxy replay tooling. | `refusal.io.invalid_args` |
| `dom sys` | System composition replay, explain, and stress tooling. | `refusal.io.invalid_args` |
| `dom worldgen` | World generation replay, verification, and stress helpers. | `refusal.io.invalid_args` |
| `launcher attach` | Attach launcher TUI/CLI to supervised child IPC consoles in deterministic order. | `refusal.io.invalid_args`, `refusal.supervisor.not_running` |
| `launcher start` | Start a deterministic supervised local singleplayer or headless server run. | `refusal.io.invalid_args`, `refusal.pack.contract_range_mismatch`, `refusal.supervisor.already_running`, `refusal.supervisor.endpoint_unreached` |
| `launcher status` | Show deterministic supervisor state, process health, and aggregated logs. | `refusal.supervisor.not_running` |
| `launcher stop` | Stop the active supervised run in deterministic client then server order. | `refusal.supervisor.endpoint_unreached`, `refusal.supervisor.not_running` |
| `packs build-lock` | Verify packs offline and emit a deterministic pack lock plus compatibility report. | `refusal.io.invalid_args`, `refusal.pack.contract_range_mismatch`, `refusal.pack.registry_missing`, `refusal.pack.schema_invalid`, `refusal.pack.trust_denied` |
| `packs list` | List available pack manifests in deterministic order. | `refusal.io.invalid_args` |
| `packs verify` | Run the offline pack compatibility verification pipeline. | `refusal.io.invalid_args`, `refusal.pack.contract_range_mismatch`, `refusal.pack.registry_missing`, `refusal.pack.schema_invalid`, `refusal.pack.trust_denied` |
| `profiles list` | List available profile bundles in deterministic order. | - |
| `profiles show` | Show a single profile bundle by bundle id. | `refusal.io.invalid_args`, `refusal.io.profile_not_found` |
| `dom client compat-status` | Run deterministic endpoint compatibility status and show negotiated mode plus disabled features. | `refusal.compat.contract_mismatch`, `refusal.compat.no_common_protocol`, `refusal.io.invalid_args` |
| `dom client console` | Alias of `console enter` for deterministic REPL console access. | `refusal.io.invalid_args` |
| `dom client descriptor` | Emit the CAP-NEG endpoint descriptor for the active product. | `refusal.io.invalid_args` |
| `dom compat emit-descriptor` | Emit deterministic CAP-NEG-1 endpoint descriptors for product surfaces | `refusal.io.invalid_args` |
| `dom compat generate-descriptor-manifest` | Generate deterministic offline descriptor manifest from dist/bin wrappers | `refusal.io.invalid_args` |
| `dom compat generate-interop-matrix` | Generate the deterministic CAP-NEG-4 synthetic interoperability matrix | `refusal.io.invalid_args` |
| `dom compat replay-migration` | Replay deterministic PACK-COMPAT-2 artifact migrations | `refusal.io.invalid_args` |
| `dom compat replay-negotiation` | Replay deterministic endpoint negotiation from recorded or default descriptors | `refusal.io.invalid_args` |
| `dom compat run-interop-stress` | Run the deterministic CAP-NEG-4 interoperability stress harness | `refusal.io.invalid_args` |
| `dom compat status` | Run deterministic endpoint compatibility status and show negotiated mode plus disabled features. | `refusal.compat.contract_mismatch`, `refusal.compat.no_common_protocol`, `refusal.io.invalid_args` |
| `dom diag capture` | Write a deterministic DIAG-0 repro bundle with logs, proof anchors, canonical events, and pinned runtime inputs. | `refusal.io.invalid_args` |
| `dom diag replay-bundle` | Replay a DIAG-0 repro bundle and verify deterministic hashes | `refusal.io.invalid_args` |
| `dom diag snapshot` | Write a deterministic offline diagnostic snapshot bundle with descriptor, logs, and proof anchors. | `refusal.io.invalid_args` |
| `dom earth generate-earth-mvp-stress` | Generate deterministic EARTH-9 MVP stress scenario payloads | `refusal.io.invalid_args` |
| `dom earth replay-climate-window` | Verify EARTH-2 seasonal climate replay determinism | `refusal.io.invalid_args` |
| `dom earth replay-earth-physics-window` | Replay deterministic EARTH-9 movement and terrain-contact windows | `refusal.io.invalid_args` |
| `dom earth replay-earth-view-window` | EARTH-9 view replay determinism wrapper for sky, illumination, water, and map artifacts | `refusal.io.invalid_args` |
| `dom earth replay-hydrology-window` | Verify EARTH-1 hydrology-window replay determinism | `refusal.io.invalid_args` |
| `dom earth replay-illumination-view` | Compatibility wrapper for SOL-1 illumination replay determinism | `refusal.io.invalid_args` |
| `dom earth replay-material-proxy-window` | Verify EARTH-10 material-proxy replay determinism | `refusal.io.invalid_args` |
| `dom earth replay-sky-view` | Verify EARTH-4 sky replay determinism | `refusal.io.invalid_args` |
| `dom earth replay-tide-window` | Verify EARTH-3 tide replay determinism | `refusal.io.invalid_args` |
| `dom earth replay-water-view` | Verify EARTH-8 water-view replay determinism | `refusal.io.invalid_args` |
| `dom earth replay-wind-window` | Verify EARTH-7 wind replay determinism | `refusal.io.invalid_args` |
| `dom earth run-earth-mvp-stress` | Run the deterministic EARTH-9 MVP stress harness | `refusal.io.invalid_args` |
| `dom gal replay-galaxy-objects` | Verify GAL-1 galaxy object replay determinism | `refusal.io.invalid_args` |
| `dom gal replay-galaxy-proxies` | Verify GAL-0 galaxy-proxy replay determinism | `refusal.io.invalid_args` |
| `dom geo explain-property-origin` | Explain deterministic GEO-9 property provenance for an object/property path | `refusal.io.invalid_args` |
| `dom geo generate-geo-stress` | Generate deterministic GEO-10 stress scenario payloads | `refusal.io.invalid_args` |
| `dom geo replay-field-geo-window` | Verify GEO-4 field replay windows preserve GEO-keyed field hash surfaces | `refusal.io.invalid_args` |
| `dom geo replay-frame-window` | Verify GEO-2 frame graph and position transforms are stable across replay | `refusal.io.invalid_args` |
| `dom geo replay-geo-window` | Replay GEO-10 stress windows and verify GEO proof surfaces remain stable | `refusal.io.invalid_args` |
| `dom geo replay-geometry-window` | Verify GEO-7 geometry edit replay determinism | `refusal.io.invalid_args` |
| `dom geo replay-overlay-merge` | Verify GEO-9 overlay merge replay determinism | `refusal.io.invalid_args` |
| `dom geo replay-path-request` | Verify GEO-6 path queries replay deterministically | `refusal.io.invalid_args` |
| `dom geo replay-view-window` | Verify GEO-5 projected views replay deterministically under lens gating | `refusal.io.invalid_args` |
| `dom geo replay-worldgen-cell` | Verify GEO-8 worldgen replay determinism for canonical cell requests | `refusal.io.invalid_args` |
| `dom geo run-geo-stress` | Run the deterministic GEO-10 stress harness and verify repeated-run stability | `refusal.io.invalid_args` |
| `dom geo verify-id-stability` | Verify GEO-1 cell-key and object-ID stability for deterministic fixtures | `refusal.io.invalid_args` |
| `dom geo verify-metric-stability` | Verify GEO-3 metric query stability for deterministic fixtures | `refusal.io.invalid_args` |
| `dom geo verify-overlay-identity` | Verify GEO-10 overlay application preserves stable object identities | `refusal.io.invalid_args` |
| `dom geo verify-sol-pin-overlay` | Verify the Sol minimal pin overlay against the canonical MVP runtime identity | `refusal.io.invalid_args` |
| `dom lib generate-lib-stress` | Generate the deterministic LIB-7 library stress scenario workspace | `refusal.io.invalid_args` |
| `dom lib replay-save-open` | Replay deterministic save-open policy decisions and optionally verify a recorded decision | `refusal.io.invalid_args` |
| `dom lib run-lib-stress` | Run the deterministic LIB-7 library stress harness | `refusal.io.invalid_args` |
| `dom lib verify-bundle` | Verify deterministic LIB-6 bundles offline | `refusal.io.invalid_args` |
| `dom logic generate-logic-stress` | Generate deterministic LOGIC-10 stress scenario packs | `refusal.io.invalid_args` |
| `dom logic replay-compiled-logic-window` | Replay LOGIC windows through L1 and compiled paths and compare output/state hashes | `refusal.io.invalid_args` |
| `dom logic replay-fault-window` | Replay a deterministic LOGIC-8 fault/noise/security window and summarize proof hashes | `refusal.io.invalid_args` |
| `dom logic replay-logic-window` | Replay a deterministic LOGIC-4 evaluation window and summarize proof hashes | `refusal.io.invalid_args` |
| `dom logic replay-protocol-window` | Replay a deterministic LOGIC-9 protocol window and summarize protocol proof hashes | `refusal.io.invalid_args` |
| `dom logic replay-timing-window` | Replay a deterministic LOGIC-5 timing window and summarize timing hashes | `refusal.io.invalid_args` |
| `dom logic replay-trace-window` | Replay a deterministic LOGIC-7 debug window and summarize trace proof hashes | `refusal.io.invalid_args` |
| `dom logic run-logic-compile-stress` | Run a deterministic LOGIC-6 compile/collapse stress scenario and summarize compiled parity | `refusal.io.invalid_args` |
| `dom logic run-logic-debug-stress` | Run a deterministic LOGIC-7 debug stress scenario and summarize bounded trace behavior | `refusal.io.invalid_args` |
| `dom logic run-logic-eval-stress` | Run a deterministic uncompiled LOGIC-4 stress scenario and summarize hashes | `refusal.io.invalid_args` |
| `dom logic run-logic-fault-stress` | Run a deterministic LOGIC-8 fault/noise/security stress scenario | `refusal.io.invalid_args` |
| `dom logic run-logic-protocol-stress` | Run a deterministic LOGIC-9 protocol contention stress scenario | `refusal.io.invalid_args` |
| `dom logic run-logic-stress` | Run the deterministic LOGIC-10 stress envelope across scale, compile, timing, protocol, fault, and debug lanes | `refusal.io.invalid_args` |
| `dom logic run-logic-timing-stress` | Run a deterministic LOGIC-5 timing stress scenario and summarize timing hashes | `refusal.io.invalid_args` |
| `dom logic verify-compiled-vs-l1` | Verify deterministic compiled-vs-L1 parity for bounded LOGIC fixtures | `refusal.io.invalid_args` |
| `dom pack build-lock` | Verify packs offline and emit a deterministic pack lock plus compatibility report. | `refusal.io.invalid_args`, `refusal.pack.contract_range_mismatch`, `refusal.pack.registry_missing`, `refusal.pack.schema_invalid`, `refusal.pack.trust_denied` |
| `dom pack capability-inspect` | Inspect declared pack capabilities, overlaps, and dependency closure. | `refusal.io.invalid_args` |
| `dom pack list` | List available pack manifests in deterministic order. | `refusal.io.invalid_args` |
| `dom pack migrate-capability-gating` | Run the legacy capability gating migration helper through the stable umbrella. | `refusal.io.invalid_args` |
| `dom pack validate-manifest` | Run the legacy pack manifest validator through the stable umbrella. | `refusal.io.invalid_args` |
| `dom pack verify` | Run the offline pack compatibility verification pipeline. | `refusal.io.invalid_args`, `refusal.pack.contract_range_mismatch`, `refusal.pack.registry_missing`, `refusal.pack.schema_invalid`, `refusal.pack.trust_denied` |
| `dom proc generate-proc-stress` | PROC-9 deterministic process stress scenario generator | `refusal.io.invalid_args` |
| `dom proc replay-capsule-window` | Verify deterministic replay hashes for PROC-5 process capsule windows | `refusal.io.invalid_args` |
| `dom proc replay-drift-window` | Verify deterministic replay hashes for PROC-6 drift/revalidation outcomes | `refusal.io.invalid_args` |
| `dom proc replay-experiment-window` | Verify deterministic replay hashes for PROC-7 experiment/result windows | `refusal.io.invalid_args` |
| `dom proc replay-maturity-window` | Verify deterministic replay hashes for PROC-4 maturity outcomes | `refusal.io.invalid_args` |
| `dom proc replay-pipeline-window` | Verify deterministic replay hashes for PROC-8 software pipeline windows | `refusal.io.invalid_args` |
| `dom proc replay-proc-window` | Verify deterministic replay hashes for PROC-9 process windows | `refusal.io.invalid_args` |
| `dom proc replay-process-window` | Verify deterministic process-run replay hashes over a state payload window | `refusal.io.invalid_args` |
| `dom proc replay-qc-window` | Verify deterministic replay hashes for PROC-3 QC sampling outcomes | `refusal.io.invalid_args` |
| `dom proc replay-quality-window` | Verify deterministic process quality replay hashes over a state payload window | `refusal.io.invalid_args` |
| `dom proc replay-reverse-engineering-window` | Verify deterministic replay hashes for PROC-7 reverse-engineering windows | `refusal.io.invalid_args` |
| `dom proc run-proc-stress` | PROC-9 deterministic stress harness | `refusal.io.invalid_args` |
| `dom proc verify-proc-compaction` | Compact PROC derived artifacts and verify replay from compaction anchors | `refusal.io.invalid_args` |
| `dom server compat-status` | Run deterministic endpoint compatibility status and show negotiated mode plus disabled features. | `refusal.compat.contract_mismatch`, `refusal.compat.no_common_protocol`, `refusal.io.invalid_args` |
| `dom server console` | Alias of `console enter` for deterministic REPL console access. | `refusal.io.invalid_args` |
| `dom server descriptor` | Emit the CAP-NEG endpoint descriptor for the active product. | `refusal.io.invalid_args` |
| `dom server replay-local-singleplayer` | Verify SERVER-MVP-1 local singleplayer orchestration replay | `refusal.io.invalid_args` |
| `dom server replay-server-window` | Verify SERVER-MVP-0 deterministic tick, loopback, and proof-anchor replay | `refusal.io.invalid_args` |
| `dom sol replay-illumination-view` | Replay deterministic SOL-1 illumination geometry windows and verify fingerprints | `refusal.io.invalid_args` |
| `dom sol replay-orbit-view` | Replay deterministic SOL-2 orbit-view windows and verify fingerprints | `refusal.io.invalid_args` |
| `dom sys generate-sys-stress` | SYS-8 deterministic stress scenario generator | `refusal.io.invalid_args` |
| `dom sys replay-capsule-window` | Verify SYS-2 macro capsule replay hashes across a deterministic state window | `refusal.io.invalid_args` |
| `dom sys replay-certification-window` | Verify SYS-5 certification replay hashes across deterministic state windows | `refusal.io.invalid_args` |
| `dom sys replay-sys-window` | Verify SYS-8 replay windows reproduce deterministic SYS proof hash chains | `refusal.io.invalid_args` |
| `dom sys replay-system-failure-window` | Verify SYS-6 reliability replay hashes across deterministic state windows | `refusal.io.invalid_args` |
| `dom sys replay-tier-transitions` | Verify SYS-3 tier transition replay hashes across deterministic windows | `refusal.io.invalid_args` |
| `dom sys run-sys-stress` | SYS-8 deterministic stress harness | `refusal.io.invalid_args` |
| `dom sys template-browser` | SYS-4 developer template browser/instantiation CLI | `refusal.io.invalid_args` |
| `dom sys verify-explain-determinism` | Verify SYS-7 system forensics explain determinism over a state window | `refusal.io.invalid_args` |
| `dom sys verify-statevec-roundtrip` | Verify STATEVEC-0 deterministic serialize/deserialize roundtrip stability | `refusal.io.invalid_args` |
| `dom sys verify-template-reproducible` | Verify SYS-4 template compilation is deterministic and reproducible | `refusal.io.invalid_args` |
| `dom worldgen replay-climate-window` | Verify EARTH-2 seasonal climate replay determinism | `refusal.io.invalid_args` |
| `dom worldgen replay-galaxy-objects` | Verify GAL-1 galaxy object replay determinism | `refusal.io.invalid_args` |
| `dom worldgen replay-galaxy-proxies` | Verify GAL-0 galaxy-proxy replay determinism | `refusal.io.invalid_args` |
| `dom worldgen replay-hydrology-window` | Verify EARTH-1 hydrology-window replay determinism | `refusal.io.invalid_args` |
| `dom worldgen replay-illumination-view` | Compatibility wrapper for SOL-1 illumination replay determinism | `refusal.io.invalid_args` |
| `dom worldgen replay-material-proxy-window` | Verify EARTH-10 material-proxy replay determinism | `refusal.io.invalid_args` |
| `dom worldgen replay-refinement-window` | Verify MW-4 refinement-window replay determinism | `refusal.io.invalid_args` |
| `dom worldgen replay-sky-view` | Verify EARTH-4 sky replay determinism | `refusal.io.invalid_args` |
| `dom worldgen replay-system-instantiation` | Verify MW-1 star-system instantiation replay determinism | `refusal.io.invalid_args` |
| `dom worldgen replay-system-l2` | Verify MW-2 L2 star and planet instantiation replay determinism | `refusal.io.invalid_args` |
| `dom worldgen replay-tide-window` | Verify EARTH-3 tide replay determinism | `refusal.io.invalid_args` |
| `dom worldgen replay-water-view` | Verify EARTH-8 water-view replay determinism | `refusal.io.invalid_args` |
| `dom worldgen replay-wind-window` | Verify EARTH-7 wind replay determinism | `refusal.io.invalid_args` |
| `dom worldgen run-refinement-stress` | Run the MW-4 rapid-teleport and ROI-thrash stress fixture | `refusal.io.invalid_args` |
| `dom worldgen verify-earth-surface` | Verify EARTH-0 far-LOD surface consistency without renderer dependencies | `refusal.io.invalid_args` |

## Namespaces

| Namespace | Products | Description |
| --- | --- | --- |
| `client.*` | `client` | Reserved stable namespace for client-specific runtime commands. |
| `engine.*` | `engine` | Reserved stable namespace for engine product commands. |
| `game.*` | `game` | Reserved stable namespace for game product commands. |
| `geo.*` | `client`, `tool.attach_console_stub` | Reserved stable namespace for GEO explain and inspection commands. |
| `launcher.*` | `launcher` | Reserved stable namespace for launcher product commands. |
| `logic.*` | `client`, `tool.attach_console_stub` | Reserved stable namespace for logic compile, probe, and trace commands. |
| `server.*` | `server` | Reserved stable namespace for server command surfaces. |
| `session.*` | `client`, `launcher`, `server`, `setup` | Reserved stable namespace for session lifecycle commands. |
| `setup.*` | `setup` | Reserved stable namespace for setup product commands. |
| `tool.*` | `tool.attach_console_stub` | Reserved stable namespace for tool product commands. |

## Refusal To Exit Mapping

| Refusal Match | Exit Code | Description |
| --- | --- | --- |
| `refusal.compat.*` | `30` | Compatibility and negotiation failures map to the contract/compatibility range. |
| `refusal.compat.feature_disabled` | `50` | Negotiated feature-disable refusals map to the refusal range. |
| `refusal.connection.*` | `40` | Connection and attach handshake failures map to the transport/IPC range unless explicitly overridden. |
| `refusal.connection.negotiation_mismatch` | `40` | Negotiation record mismatches on attach/connection map to the transport range. |
| `refusal.connection.no_negotiation` | `40` | Missing mandatory attach/connection negotiation maps to the transport range. |
| `refusal.contract.*` | `30` | Contract mismatches map to the contract/compatibility range. |
| `refusal.debug.*` | `50` | Debug/gating refusals map to the refusal range except where explicitly overridden. |
| `refusal.debug.command_unknown` | `10` | Unknown registered-command tokens map to usage-range exits. |
| `refusal.diag.*` | `50` | Deterministic repro-bundle capture and replay refusals map to the refusal range. |
| `refusal.io.*` | `40` | IO/host-shell failures map to the transport and IO-shell range. |
| `refusal.io.invalid_args` | `10` | Invalid command arguments map to usage-range exits. |
| `refusal.io.profile_not_found` | `20` | Missing profile bundles are treated as pack/profile surface failures. |
| `refusal.law.*` | `50` | Law refusals map to the refusal range. |
| `refusal.pack.*` | `20` | Pack validation and verification failures map to the pack/profile range. |
| `refusal.server.command_unknown` | `50` | Unknown live server console commands remain explicit refusal-range failures. |
| `refusal.supervisor.*` | `50` | Supervisor lifecycle and orchestration refusals map to the refusal range. |

## Product Views

### `client`

- `compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `console`: Alias of `console enter` for deterministic REPL console access.
- `descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
- `diag`: Emit deterministic shell diagnostic metadata.
- `help`: Show deterministic AppShell help generated from the command registry.
- `packs`: Alias of `packs list` for deterministic pack enumeration.
- `profiles`: Alias of `profiles list` for deterministic bundle enumeration.
- `validate`: Run the unified validation pipeline through `validate --all`.
- `verify`: Alias of `packs verify` for offline pack/profile verification.
- `version`: Emit deterministic product version metadata and build identity.
- `console attach`: Attach to a local IPC console endpoint through CAP-NEG negotiation.
- `console detach`: Detach a logical local IPC console session.
- `console enter`: Open the deterministic REPL console session stub for the current product.
- `console sessions`: List discovered local IPC console endpoints in deterministic order.
- `diag capture`: Write a deterministic DIAG-0 repro bundle with logs, proof anchors, canonical events, and pinned runtime inputs.
- `diag snapshot`: Write a deterministic offline diagnostic snapshot bundle with descriptor, logs, and proof anchors.
- `packs build-lock`: Verify packs offline and emit a deterministic pack lock plus compatibility report.
- `packs list`: List available pack manifests in deterministic order.
- `packs verify`: Run the offline pack compatibility verification pipeline.
- `profiles list`: List available profile bundles in deterministic order.
- `profiles show`: Show a single profile bundle by bundle id.
- `client.*`: Reserved stable namespace for client-specific runtime commands.
- `geo.*`: Reserved stable namespace for GEO explain and inspection commands.
- `logic.*`: Reserved stable namespace for logic compile, probe, and trace commands.
- `session.*`: Reserved stable namespace for session lifecycle commands.

### `engine`

- `compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `console`: Alias of `console enter` for deterministic REPL console access.
- `descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
- `diag`: Emit deterministic shell diagnostic metadata.
- `help`: Show deterministic AppShell help generated from the command registry.
- `packs`: Alias of `packs list` for deterministic pack enumeration.
- `profiles`: Alias of `profiles list` for deterministic bundle enumeration.
- `validate`: Run the unified validation pipeline through `validate --all`.
- `verify`: Alias of `packs verify` for offline pack/profile verification.
- `version`: Emit deterministic product version metadata and build identity.
- `console attach`: Attach to a local IPC console endpoint through CAP-NEG negotiation.
- `console detach`: Detach a logical local IPC console session.
- `console enter`: Open the deterministic REPL console session stub for the current product.
- `console sessions`: List discovered local IPC console endpoints in deterministic order.
- `diag capture`: Write a deterministic DIAG-0 repro bundle with logs, proof anchors, canonical events, and pinned runtime inputs.
- `diag snapshot`: Write a deterministic offline diagnostic snapshot bundle with descriptor, logs, and proof anchors.
- `packs build-lock`: Verify packs offline and emit a deterministic pack lock plus compatibility report.
- `packs list`: List available pack manifests in deterministic order.
- `packs verify`: Run the offline pack compatibility verification pipeline.
- `profiles list`: List available profile bundles in deterministic order.
- `profiles show`: Show a single profile bundle by bundle id.
- `engine.*`: Reserved stable namespace for engine product commands.

### `game`

- `compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `console`: Alias of `console enter` for deterministic REPL console access.
- `descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
- `diag`: Emit deterministic shell diagnostic metadata.
- `help`: Show deterministic AppShell help generated from the command registry.
- `packs`: Alias of `packs list` for deterministic pack enumeration.
- `profiles`: Alias of `profiles list` for deterministic bundle enumeration.
- `validate`: Run the unified validation pipeline through `validate --all`.
- `verify`: Alias of `packs verify` for offline pack/profile verification.
- `version`: Emit deterministic product version metadata and build identity.
- `console attach`: Attach to a local IPC console endpoint through CAP-NEG negotiation.
- `console detach`: Detach a logical local IPC console session.
- `console enter`: Open the deterministic REPL console session stub for the current product.
- `console sessions`: List discovered local IPC console endpoints in deterministic order.
- `diag capture`: Write a deterministic DIAG-0 repro bundle with logs, proof anchors, canonical events, and pinned runtime inputs.
- `diag snapshot`: Write a deterministic offline diagnostic snapshot bundle with descriptor, logs, and proof anchors.
- `packs build-lock`: Verify packs offline and emit a deterministic pack lock plus compatibility report.
- `packs list`: List available pack manifests in deterministic order.
- `packs verify`: Run the offline pack compatibility verification pipeline.
- `profiles list`: List available profile bundles in deterministic order.
- `profiles show`: Show a single profile bundle by bundle id.
- `game.*`: Reserved stable namespace for game product commands.

### `launcher`

- `compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `console`: Alias of `console enter` for deterministic REPL console access.
- `descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
- `diag`: Emit deterministic shell diagnostic metadata.
- `help`: Show deterministic AppShell help generated from the command registry.
- `packs`: Alias of `packs list` for deterministic pack enumeration.
- `profiles`: Alias of `profiles list` for deterministic bundle enumeration.
- `validate`: Run the unified validation pipeline through `validate --all`.
- `verify`: Alias of `packs verify` for offline pack/profile verification.
- `version`: Emit deterministic product version metadata and build identity.
- `console attach`: Attach to a local IPC console endpoint through CAP-NEG negotiation.
- `console detach`: Detach a logical local IPC console session.
- `console enter`: Open the deterministic REPL console session stub for the current product.
- `console sessions`: List discovered local IPC console endpoints in deterministic order.
- `diag capture`: Write a deterministic DIAG-0 repro bundle with logs, proof anchors, canonical events, and pinned runtime inputs.
- `diag snapshot`: Write a deterministic offline diagnostic snapshot bundle with descriptor, logs, and proof anchors.
- `launcher attach`: Attach launcher TUI/CLI to supervised child IPC consoles in deterministic order.
- `launcher start`: Start a deterministic supervised local singleplayer or headless server run.
- `launcher status`: Show deterministic supervisor state, process health, and aggregated logs.
- `launcher stop`: Stop the active supervised run in deterministic client then server order.
- `packs build-lock`: Verify packs offline and emit a deterministic pack lock plus compatibility report.
- `packs list`: List available pack manifests in deterministic order.
- `packs verify`: Run the offline pack compatibility verification pipeline.
- `profiles list`: List available profile bundles in deterministic order.
- `profiles show`: Show a single profile bundle by bundle id.
- `launcher.*`: Reserved stable namespace for launcher product commands.
- `session.*`: Reserved stable namespace for session lifecycle commands.

### `server`

- `compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `console`: Alias of `console enter` for deterministic REPL console access.
- `descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
- `diag`: Emit deterministic shell diagnostic metadata.
- `help`: Show deterministic AppShell help generated from the command registry.
- `packs`: Alias of `packs list` for deterministic pack enumeration.
- `profiles`: Alias of `profiles list` for deterministic bundle enumeration.
- `validate`: Run the unified validation pipeline through `validate --all`.
- `verify`: Alias of `packs verify` for offline pack/profile verification.
- `version`: Emit deterministic product version metadata and build identity.
- `console attach`: Attach to a local IPC console endpoint through CAP-NEG negotiation.
- `console detach`: Detach a logical local IPC console session.
- `console enter`: Open the deterministic REPL console session stub for the current product.
- `console sessions`: List discovered local IPC console endpoints in deterministic order.
- `diag capture`: Write a deterministic DIAG-0 repro bundle with logs, proof anchors, canonical events, and pinned runtime inputs.
- `diag snapshot`: Write a deterministic offline diagnostic snapshot bundle with descriptor, logs, and proof anchors.
- `packs build-lock`: Verify packs offline and emit a deterministic pack lock plus compatibility report.
- `packs list`: List available pack manifests in deterministic order.
- `packs verify`: Run the offline pack compatibility verification pipeline.
- `profiles list`: List available profile bundles in deterministic order.
- `profiles show`: Show a single profile bundle by bundle id.
- `server.*`: Reserved stable namespace for server command surfaces.
- `session.*`: Reserved stable namespace for session lifecycle commands.

### `setup`

- `compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `console`: Alias of `console enter` for deterministic REPL console access.
- `descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
- `diag`: Emit deterministic shell diagnostic metadata.
- `help`: Show deterministic AppShell help generated from the command registry.
- `packs`: Alias of `packs list` for deterministic pack enumeration.
- `profiles`: Alias of `profiles list` for deterministic bundle enumeration.
- `validate`: Run the unified validation pipeline through `validate --all`.
- `verify`: Alias of `packs verify` for offline pack/profile verification.
- `version`: Emit deterministic product version metadata and build identity.
- `console attach`: Attach to a local IPC console endpoint through CAP-NEG negotiation.
- `console detach`: Detach a logical local IPC console session.
- `console enter`: Open the deterministic REPL console session stub for the current product.
- `console sessions`: List discovered local IPC console endpoints in deterministic order.
- `diag capture`: Write a deterministic DIAG-0 repro bundle with logs, proof anchors, canonical events, and pinned runtime inputs.
- `diag snapshot`: Write a deterministic offline diagnostic snapshot bundle with descriptor, logs, and proof anchors.
- `packs build-lock`: Verify packs offline and emit a deterministic pack lock plus compatibility report.
- `packs list`: List available pack manifests in deterministic order.
- `packs verify`: Run the offline pack compatibility verification pipeline.
- `profiles list`: List available profile bundles in deterministic order.
- `profiles show`: Show a single profile bundle by bundle id.
- `session.*`: Reserved stable namespace for session lifecycle commands.
- `setup.*`: Reserved stable namespace for setup product commands.

### `tool.attach_console_stub`

- `compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `console`: Alias of `console enter` for deterministic REPL console access.
- `descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
- `diag`: Emit deterministic shell diagnostic metadata.
- `dom`: List the stable Dominium tool namespaces and wrapped commands.
- `help`: Show deterministic AppShell help generated from the command registry.
- `packs`: Alias of `packs list` for deterministic pack enumeration.
- `profiles`: Alias of `profiles list` for deterministic bundle enumeration.
- `validate`: Run the unified validation pipeline through `validate --all`.
- `verify`: Alias of `packs verify` for offline pack/profile verification.
- `version`: Emit deterministic product version metadata and build identity.
- `console attach`: Attach to a local IPC console endpoint through CAP-NEG negotiation.
- `console detach`: Detach a logical local IPC console session.
- `console enter`: Open the deterministic REPL console session stub for the current product.
- `console sessions`: List discovered local IPC console endpoints in deterministic order.
- `diag capture`: Write a deterministic DIAG-0 repro bundle with logs, proof anchors, canonical events, and pinned runtime inputs.
- `diag snapshot`: Write a deterministic offline diagnostic snapshot bundle with descriptor, logs, and proof anchors.
- `dom client`: Client-facing AppShell inspection commands.
- `dom compat`: Capability negotiation descriptors, replay, and interop tooling.
- `dom diag`: Repro bundle capture, snapshot, and replay tooling.
- `dom earth`: Earth-focused replay, stress, and verification tools.
- `dom gal`: Galaxy proxy and compact-object replay tooling.
- `dom geo`: Deterministic GEO replay, identity, overlay, and metric tooling.
- `dom lib`: Library bundle and save verification tooling.
- `dom logic`: Logic replay, compile, and stress tooling.
- `dom pack`: Pack inventory, verification, and capability inspection commands.
- `dom proc`: Process, capsule, and drift replay tooling.
- `dom server`: Server replay and inspection tooling.
- `dom sol`: Illumination and orbital proxy replay tooling.
- `dom sys`: System composition replay, explain, and stress tooling.
- `dom worldgen`: World generation replay, verification, and stress helpers.
- `packs build-lock`: Verify packs offline and emit a deterministic pack lock plus compatibility report.
- `packs list`: List available pack manifests in deterministic order.
- `packs verify`: Run the offline pack compatibility verification pipeline.
- `profiles list`: List available profile bundles in deterministic order.
- `profiles show`: Show a single profile bundle by bundle id.
- `dom client compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `dom client console`: Alias of `console enter` for deterministic REPL console access.
- `dom client descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
- `dom compat emit-descriptor`: Emit deterministic CAP-NEG-1 endpoint descriptors for product surfaces
- `dom compat generate-descriptor-manifest`: Generate deterministic offline descriptor manifest from dist/bin wrappers
- `dom compat generate-interop-matrix`: Generate the deterministic CAP-NEG-4 synthetic interoperability matrix
- `dom compat replay-migration`: Replay deterministic PACK-COMPAT-2 artifact migrations
- `dom compat replay-negotiation`: Replay deterministic endpoint negotiation from recorded or default descriptors
- `dom compat run-interop-stress`: Run the deterministic CAP-NEG-4 interoperability stress harness
- `dom compat status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `dom diag capture`: Write a deterministic DIAG-0 repro bundle with logs, proof anchors, canonical events, and pinned runtime inputs.
- `dom diag replay-bundle`: Replay a DIAG-0 repro bundle and verify deterministic hashes
- `dom diag snapshot`: Write a deterministic offline diagnostic snapshot bundle with descriptor, logs, and proof anchors.
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
- `dom gal replay-galaxy-objects`: Verify GAL-1 galaxy object replay determinism
- `dom gal replay-galaxy-proxies`: Verify GAL-0 galaxy-proxy replay determinism
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
- `dom lib generate-lib-stress`: Generate the deterministic LIB-7 library stress scenario workspace
- `dom lib replay-save-open`: Replay deterministic save-open policy decisions and optionally verify a recorded decision
- `dom lib run-lib-stress`: Run the deterministic LIB-7 library stress harness
- `dom lib verify-bundle`: Verify deterministic LIB-6 bundles offline
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
- `dom pack build-lock`: Verify packs offline and emit a deterministic pack lock plus compatibility report.
- `dom pack capability-inspect`: Inspect declared pack capabilities, overlaps, and dependency closure.
- `dom pack list`: List available pack manifests in deterministic order.
- `dom pack migrate-capability-gating`: Run the legacy capability gating migration helper through the stable umbrella.
- `dom pack validate-manifest`: Run the legacy pack manifest validator through the stable umbrella.
- `dom pack verify`: Run the offline pack compatibility verification pipeline.
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
- `dom server compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `dom server console`: Alias of `console enter` for deterministic REPL console access.
- `dom server descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
- `dom server replay-local-singleplayer`: Verify SERVER-MVP-1 local singleplayer orchestration replay
- `dom server replay-server-window`: Verify SERVER-MVP-0 deterministic tick, loopback, and proof-anchor replay
- `dom sol replay-illumination-view`: Replay deterministic SOL-1 illumination geometry windows and verify fingerprints
- `dom sol replay-orbit-view`: Replay deterministic SOL-2 orbit-view windows and verify fingerprints
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
- `geo.*`: Reserved stable namespace for GEO explain and inspection commands.
- `logic.*`: Reserved stable namespace for logic compile, probe, and trace commands.
- `tool.*`: Reserved stable namespace for tool product commands.
