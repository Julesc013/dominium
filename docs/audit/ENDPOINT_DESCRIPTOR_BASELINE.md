Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Endpoint Descriptor Baseline

## Scope
- CAP-NEG-1 materializes deterministic endpoint descriptors for product surfaces.
- Descriptor emission is now available for MVP product binaries and offline tooling.
- Live negotiation semantics remain the CAP-NEG-0 baseline.

## Products Covered
- `engine`
- `game`
- `client`
- `server`
- `setup`
- `launcher`
- `tool.attach_console_stub`

## Descriptor Content
Each emitted `EndpointDescriptor` includes:
- `product_id`
- `product_version`
- supported protocol ranges
- supported semantic contract ranges
- feature capabilities
- required capabilities
- optional capabilities
- degrade ladders
- deterministic fingerprint

## Capability Sets
- Capability defaults are now data-driven by `data/registries/product_capability_defaults.json`.
- Product identity metadata remains in `data/registries/product_registry.json`.
- Unknown capabilities remain deterministic no-ops for negotiation until declared in `data/registries/capability_registry.json`.

## Deterministic Build Identity
- Build ids are derived from:
  - git commit hash if available
  - semantic contract registry hash
  - stable compilation-options hash
- If git metadata is unavailable, a fixed fallback build number token is used.
- No wall-clock fields participate in descriptor identity.

## Offline Surfaces
- Dist wrappers emit descriptors via `--descriptor` and `--descriptor-file`.
- `tools/compat/tool_generate_descriptor_manifest.py` produces `dist/manifests/endpoint_descriptors.json`.

## Readiness
This baseline is ready for CAP-NEG-2 handshake integration, where live handshakes can consume the same emitted descriptors instead of registry-backed bootstrap descriptors.
