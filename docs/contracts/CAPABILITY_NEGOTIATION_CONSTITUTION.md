Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `data/registries/semantic_contract_registry.json`, `data/registries/capability_registry.json`, `data/registries/product_registry.json`, and `data/registries/compat_mode_registry.json`.
Stability: stable
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Capability Negotiation Constitution

## Purpose
- Define the deterministic interoperability layer for Dominium products.
- Allow arbitrary engine, game, client, server, launcher, setup, and tool versions to interoperate through explicit compatibility negotiation.
- Replace silent breakage with explicit negotiation, degradation, or refusal.
- Keep offline portable installs viable without network services or repo-only tooling.
- Identify themselves and their capabilities.
- Choose a mutually supported “compatibility mode”.
- Produce a signed/hashed negotiation record.

## Scope
This constitution governs endpoint compatibility behavior for:
- Client to Server connection handshakes
- Launcher to Client or Server local orchestration
- Setup to Pack or Profile verification
- Tool attach, diagnostics, and console negotiation

This constitution does not change simulation semantics.
It versions negotiation behavior and the records required to audit compatibility outcomes.

## Core Concepts

### EndpointDescriptor
Every executable or attachable endpoint exposes a deterministic descriptor containing:
- `product_id`
- `product_version`
- `protocol_versions_supported`
- `semantic_contract_versions_supported`
- `feature_capabilities`
- `required_capabilities`
- `optional_capabilities`
- `degrade_ladders`
- `deterministic_fingerprint`

Unknown capabilities inside a descriptor are ignored deterministically after capability-registry filtering.
For avoidance of doubt: unknown capabilities are ignored deterministically after capability-registry filtering.

### Capability
Capabilities are stable declarative interoperability claims such as:
- `cap.logic.protocol_layer`
- `cap.logic.compiled_automaton`
- `cap.geo.sphere_atlas`
- `cap.geo.ortho_map_lens`
- `cap.worldgen.refinement_l3`
- `cap.ui.tui`
- `cap.ui.rendered`
- `cap.ipc.attach_console`
- `cap.server.proof_anchors`

Capabilities are declarative only.
They do not alter law, authority, or truth semantics by themselves.

### NegotiationRecord
A deterministic artifact describing:
- participating endpoint descriptors
- the chosen protocol version
- the chosen semantic contract versions
- the enabled capability subset
- disabled capabilities and reasons
- the chosen compatibility mode
- the degrade plan
- input hashes
- the deterministic fingerprint

Negotiation records are hash-mandatory and signable.

## Deterministic Negotiation Algorithm
Given endpoints `A` and `B`:

1. Determine compatible protocol version.
   Choose the highest mutually supported protocol version.
   When multiple protocol ids are common, compare by numeric version first, then by `protocol_id`.

2. Determine compatible semantic contracts.
   For each contract category, prefer exact match.
   Otherwise choose the highest mutually supported version.
   If no mutually supported version exists, negotiation refuses unless explicit read-only compatibility is allowed.

3. Determine capability set.
   Filter both endpoints to known capability ids from `data/registries/capability_registry.json`.
   Enabled capabilities are the deterministic intersection of the filtered feature-capability sets.
   Required-capability mismatches refuse.
   Optional-capability mismatches generate degrade-plan entries.

4. Apply degrade ladders.
   Degrade rules are processed in deterministic priority order.
   The first stable common fallback mode is selected.

5. Produce the NegotiationRecord.
   All lists are sorted deterministically.
   The record includes endpoint hashes, chosen contract bundle hash, disabled capability reasons, and the final compatibility mode.

Stable refusal codes:
- `refusal.compat.no_common_protocol`
- `refusal.compat.contract_mismatch`
- `refusal.compat.missing_required_cap`

## Graceful Degradation Rules
Every product must declare fallback behavior for features it can disable or substitute.
Supported fallback actions are:
- disable feature
- substitute stub
- refuse only the affected action
- refuse the entire connection

Examples:
- If rendered UI is unavailable, fall back to `cap.ui.tui` when available.
- If `cap.geo.sphere_atlas` is unavailable, fall back to `cap.geo.ortho_map_lens` when available.
- If attach-console support is unavailable, disable attach-console actions without refusing the base connection.

All degradation decisions must appear in the NegotiationRecord.

## Standard Compatibility Modes
- `compat.full`
- `compat.degraded`
- `compat.read_only`
- `compat.refuse`

`compat.read_only` is lawful only when:
- semantic contract mismatch prevents authoritative mutation compatibility, and
- a safe observation-only fallback is explicitly allowed.

`compat.read_only` must bind mutation law to a read-only observer law profile, typically `law.observer.default`.

## Runtime Integration Points

### Client to Server
- Endpoints exchange `EndpointDescriptor` payloads during handshake.
- Negotiation is mandatory before connection acceptance.
- Server enforces the chosen compatibility mode.
- NegotiationRecord hash is stored in session and proof surfaces.

### Launcher or Local Orchestration
- Local process and control-channel bootstraps use the same descriptor and record model.
- Attach-console and local singleplayer orchestration must negotiate capabilities instead of assuming them.

### Setup and Verification
- Setup reads pack and profile descriptors and selects a compatible mode or refuses.
- Migration remains explicit invoke-only.

## Proof and Replay
Proof bundles must include:
- `negotiation_record_hash`
- endpoint descriptor hashes
- the chosen contract bundle hash

Replay must verify that:
- endpoint descriptors still hash the same way
- the NegotiationRecord still matches the inputs
- the chosen contract bundle hash still matches the replay surface

If verification fails, replay refuses unless an explicit compatibility or migration tool is invoked.

## Evolution Rules
- New behavior-critical negotiation meaning requires an explicit semantic contract update.
- New capability interpretation surfaces must be data-declared.
- Unknown capabilities remain inert by default.
- Silent degradation is forbidden.

## Non-Goals
- No network transport is mandated.
- No specific renderer or launcher stack is mandated.
- No simulation rule or worldgen behavior is changed by this constitution alone.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/contracts/SEMANTIC_CONTRACT_MODEL.md`
- `docs/meta/UNIVERSE_CONTRACT_BUNDLE.md`
- `docs/meta/EXTENSION_DISCIPLINE.md`
- `docs/geo/OVERLAY_CONFLICT_POLICIES.md`
- `docs/modding/MOD_TRUST_AND_CAPABILITIES.md`
- `data/registries/capability_registry.json`
- `data/registries/product_registry.json`
- `data/registries/compat_mode_registry.json`
