Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CAP Negotiation Baseline

## Scope
- CAP-NEG-0 establishes the deterministic capability and feature negotiation constitution.
- The change adds negotiation metadata, registries, schemas, and current loopback handshake enforcement.
- Simulation, worldgen, and logic semantics remain unchanged.

## Algorithm Summary
- Endpoints publish deterministic `EndpointDescriptor` payloads.
- Negotiation chooses the highest mutually supported protocol version.
- Semantic contract categories prefer exact matches, then highest common versions.
- Known feature capabilities intersect to form the enabled set.
- Required-capability mismatches refuse.
- Optional-capability mismatches emit degrade-plan entries.
- `compat.read_only` is available only through explicit compatibility allowance and binds to observation-only law.

## Initial Capability Set
- `cap.logic.protocol_layer`
- `cap.logic.compiled_automaton`
- `cap.geo.sphere_atlas`
- `cap.geo.ortho_map_lens`
- `cap.worldgen.refinement_l3`
- `cap.ui.tui`
- `cap.ui.rendered`
- `cap.ipc.attach_console`
- `cap.server.proof_anchors`

## Standard Modes
- `compat.full`
- `compat.degraded`
- `compat.read_only`
- `compat.refuse`

## Initial Integration Points
- `tools/xstack/sessionx/net_handshake.py`
- `src/server/net/loopback_transport.py`
- `src/server/runtime/tick_loop.py`

Current integration uses registry-backed default descriptors for existing client, server, launcher-style, setup, and tool surfaces.

## Proof and Replay
- Negotiation records are derived and hash-mandatory.
- Loopback handshake and loopback server acceptance now emit negotiation hashes and endpoint descriptor hashes.
- Server proof anchors now include negotiation-record hash chains when present.

## What Stayed Stable
- No simulation semantics changed.
- No worldgen or logic algorithms changed.
- No transport mandate was introduced.
- Unknown capabilities remain inert by default.

## Readiness
This baseline is ready for `CAP-NEG-1`, which can move descriptor emission from default registry-backed descriptors to explicit per-product executable emission without changing the negotiation algorithm.
