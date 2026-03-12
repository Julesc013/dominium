Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md`, `data/registries/capability_registry.json`, `data/registries/product_registry.json`, `data/registries/product_capability_defaults.json`, and `data/registries/semantic_contract_registry.json`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Endpoint Descriptors

## Purpose
- Materialize CAP-NEG-0 endpoint descriptors as deterministic executable output surfaces.
- Allow offline tooling, portable installs, setup verification, launcher orchestration, and future handshakes to operate from descriptors alone.
- Keep descriptor emission deterministic, stable for the same build, and independent of wall-clock or online services.

## Descriptor Emission
Each supported product must expose deterministic descriptor emission through:

- `--descriptor`
  - write the canonical `EndpointDescriptor` JSON to stdout
- `--descriptor-file <path>`
  - write the same canonical descriptor JSON to disk

For v0.0.0, JSON is the required emission format.
TLV may be added later, but JSON output is the normative offline baseline.

Descriptor emission must not:
- read wall-clock time
- depend on transport availability
- require repo-only mutable state
- mutate authoritative truth

## Product Baseline

### Engine
- capabilities:
  - `cap.geo.metric`
  - `cap.geo.projection`
  - `cap.worldgen.refinement`
  - `cap.proof.verify`

### Game
- capabilities:
  - `cap.proc`
  - `cap.sys`
  - `cap.logic`
  - `cap.worldgen.refinement`

### Client
- capabilities:
  - `cap.ui.cli`
  - `cap.ui.tui`
  - `cap.ui.rendered`
  - `cap.ipc.attach_console`
  - `cap.geo.projection`
  - `cap.geo.sphere_atlas`
  - `cap.worldgen.refinement`
  - `cap.worldgen.refinement_l3`

### Server
- capabilities:
  - `cap.server.authority`
  - `cap.server.proof_anchors`
  - `cap.net.loopback`
  - `cap.ipc.attach_console`
  - `cap.logic.protocol_layer`
  - `cap.logic.compiled_automaton`
  - `cap.worldgen.refinement`
  - `cap.worldgen.refinement_l3`

### Setup
- capabilities:
  - `cap.pack.verify`
  - `cap.pack.install`
  - `cap.profile.manage`

### Launcher
- capabilities:
  - `cap.process.supervise`
  - `cap.negotiation.run`
  - `cap.console.mux`
  - `cap.ipc.attach_console`
  - `cap.ui.cli`
  - `cap.ui.tui`

### Tools
- tools declare per-tool descriptors using `product_id = tool.<name>`.
- v0.0.0 baseline explicitly ships `tool.attach_console_stub`.

## Degrade Ladders
Baseline degrade ladders are data-driven through `data/registries/product_capability_defaults.json`.

Examples:
- client:
  - rendered UI missing -> substitute TUI
  - sphere-atlas lens unavailable -> substitute ortho map lens
- server:
  - attach-console unavailable -> disable console attachment while preserving authoritative tick
- launcher:
  - attach-console unavailable -> keep supervise surface, disable console mux attach action

All degrade ladders must be ordered, deterministic, and emitted exactly as declared.

## Build Metadata
`product_version` is `semver + build_id`.

For CAP-NEG-1, `build_id` is derived deterministically from:
- git commit hash, if available
- otherwise a fixed build number token
- semantic contract registry hash
- compilation-options hash

Compilation-options hash must avoid host-specific volatility.
It may include only stable declared build/runtime options.

## Offline Descriptor Manifest
`tools/compat/tool_generate_descriptor_manifest.py` scans `dist/bin`, runs each shipped product surface with `--descriptor`, and writes:

- `dist/manifests/endpoint_descriptors.json`

This manifest is deterministic and suitable for:
- setup validation
- launcher compatibility choice
- offline portable installs

## What CAP-NEG-1 Does Not Change
- It does not change live simulation semantics.
- It does not change worldgen, logic, or process behavior.
- It does not implement new handshake transports.
- It does not require network access.

## Readiness
This baseline is ready for CAP-NEG-2, which can wire the emitted descriptors into live client/server and IPC handshakes without changing descriptor shape or build identity rules.
