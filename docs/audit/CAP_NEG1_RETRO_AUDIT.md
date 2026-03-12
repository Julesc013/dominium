Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CAP-NEG-1 Retro Audit

## Scope
- Audit existing product/version metadata, product surfaces, and protocol/version declarations before adding deterministic endpoint descriptor emission.
- Confirm the minimum integration needed to add descriptor emission without changing live negotiation or simulation semantics.

## Existing Version and Build Metadata
- CAP-NEG-0 stores `product_version` only inside default endpoint descriptors and current handshake helpers.
- Current loopback and handshake code still hardcodes versions such as `0.0.0+client.loopback` and `0.0.0+server.default`.
- The repository already has stable git-hash helpers and build-identity references in tooling, but there is no shared Python descriptor build-metadata helper yet.
- Existing launcher/setup CLIs expose product/version-like metadata in adjacent reports, but not as a canonical `EndpointDescriptor`.

## Existing Product Surfaces
- `src/server/server_main.py` is the authoritative server CLI surface.
- `tools/mvp/runtime_entry.py` is the practical MVP client/server bootstrap surface used by `dist/bin/dominium_client` and `dist/bin/dominium_server`.
- `tools/setup/setup_cli.py` is the setup product CLI surface.
- `tools/launcher/launch.py` is the deterministic launcher product surface used by the current dist wrapper.
- `dist/bin/engine`, `dist/bin/client`, `dist/bin/server`, `dist/bin/launcher`, and `dist/bin/setup` are currently placeholder wrappers and do not emit descriptors.
- `dist/bin/game` is not present yet.

## Existing Product IDs and Capability Defaults
- CAP-NEG-0 already introduced `data/registries/product_registry.json`.
- Current registry rows exist for:
  - `engine`
  - `game`
  - `client`
  - `server`
  - `setup`
  - `launcher`
  - `tool.attach_console_stub`
- Current product defaults are embedded directly in that registry.
- CAP-NEG-1 needs a dedicated product-capability defaults registry so descriptor emission can evolve without silently entangling identity rows and default feature bundles.

## Existing Protocol and Contract Declarations
- Protocol/version ranges already exist in CAP-NEG-0 product defaults:
  - `protocol.loopback.session`
  - `protocol.loopback.control`
  - `protocol.pack.verify`
- Semantic contract support is already pinned and registry-backed through:
  - `data/registries/semantic_contract_registry.json`
  - `src/compat/capability_negotiation.py`
- Current runtime negotiation can already operate on descriptors alone once a descriptor payload is provided.

## Required CAP-NEG-1 Integration Points
- Add a deterministic descriptor engine that:
  - loads product identity rows
  - loads product capability defaults
  - derives stable build metadata
  - emits canonical JSON descriptors
- Add product-side descriptor CLI support or dist-wrapper support for:
  - engine
  - game
  - client
  - server
  - setup
  - launcher
- Add an offline manifest tool that scans `dist/bin` and records emitted descriptors deterministically.

## Risks Found
- Placeholder dist wrappers currently prevent `dist/bin` scanning from producing real descriptors.
- No shared build-metadata helper means product versions could drift if each product invents its own build id logic.
- Capability defaults are currently mixed into the product registry, which makes future identity-only tooling brittle.

## CAP-NEG-1 Fix Direction
- Keep live CAP-NEG-0 negotiation semantics unchanged.
- Add a new deterministic descriptor-emission layer for products and offline tooling.
- Reuse the existing CAP-NEG-0 descriptor shape and negotiation algorithm rather than duplicating protocol logic.
