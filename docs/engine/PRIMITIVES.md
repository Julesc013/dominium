# Engine Primitives and Interfaces (Normative)

This document is normative for the engine layer. It MUST be read alongside
`docs/architectureitecture/INVARIANTS.md` and `docs/architectureitecture/TERMINOLOGY.md`.

## Topology DAG

- The topology MUST be a directed acyclic graph (DAG); cycles are forbidden.
- Node type MUST be expressed only via data-defined traits; there are no
  hardcoded node types.
- Traversal and queries MUST be read-only and deterministic.
- Canonical interface: `engine/include/domino/topology.h`

## Domain and Domain Volume Model

- Domain volumes MUST be first-class primitives with explicit bounds.
- Domain kinds MUST be explicit (spatial, jurisdictional, economic,
  institutional).
- There MUST be no implicit global domain.
- Canonical interface: `engine/include/domino/domain.h`
- Spatial domain primitives are defined in `engine/include/domino/world/domain_*.h`.

## Representation Tier Metadata

- Representation tiers MUST be declarative metadata only.
- Representation tiers MUST NOT alter simulation logic.
- Representation tiers MAY vary by node and by LOD index.
- Canonical interface: `engine/include/domino/representation.h`

## Field Layers (Typed, Unitful)

- Field layers MUST be typed, unitful, and associated with an explicit domain.
- Field layers MUST include representation tier metadata.
- Field layers MUST include provenance metadata and knowledge state.
- Field layers MAY be explicit, hybrid, or procedural.
- Canonical interface: `engine/include/domino/field_layer.h`
- Field units and storage are defined in `engine/include/domino/dfield.h`.

## Process Execution Core (Class-Aware)

- All authoritative state change MUST occur through process execution.
- A process MUST declare class, inputs, outputs, waste, time cost, required
  capabilities, required authority scope, applicable domains, and failure modes.
- Processes MUST be class-aware: Transformative, Transactional, Epistemic.
- Scheduling, execution, and audit hooks MUST be exposed and deterministic.
- Canonical interface: `engine/include/domino/process.h`

## Capability Model

- Capabilities MUST be data-defined and composable.
- The engine MUST match required vs provided capabilities deterministically.
- Capability meaning MUST NOT be hardcoded in engine logic.
- Canonical interface: `engine/include/domino/capability.h`
- System/backend capabilities are defined separately in `engine/include/domino/caps.h`.

## Authority Tokens

- Authority tokens MUST be opaque, immutable, and non-forgeable.
- Tokens MUST be issued only during engine/game initialization.
- All mutating operations MUST require a valid authority token.
- Read-only tokens MUST NOT escalate to mutating authority.
- Canonical interface: `engine/include/domino/authority.h`

## Snapshot System (Objective + Subjective)

- Snapshots MUST be immutable and MUST NOT expose live state or raw pointers.
- Snapshots MUST include a versioned schema ID and explicit cost metadata.
- Snapshot iteration and query ordering MUST be deterministic.
- Canonical interface: `engine/include/domino/snapshot.h`

## Knowledge and Latent State

- Unknown/latent state MUST be first-class and queryable.
- Known, inferred, and unknown MUST be represented explicitly.
- Canonical interface: `engine/include/domino/knowledge_state.h`

## Determinism, Seeds, and Provenance

- There MUST be a single universe seed.
- Seed namespaces MUST be explicit.
- Seed derivation MUST be deterministic and reproducible.
- Provenance records MUST attach to processes, field materialization, and snapshots.
- Canonical interface: `engine/include/domino/provenance.h`
- Deterministic RNG streams are defined in `engine/include/domino/core/rng*.h`.

## Compatibility Negotiation and Modes

- Compatibility MUST be negotiated via capabilities and explicit modes.
- Supported modes are: Authoritative, Degraded, Frozen, Transform-only.
- The engine MUST prefer explicit degradation over silent breakage.
- The engine MUST fail loudly on incompatible inputs.
- Canonical interface: `engine/include/domino/compat_modes.h`

## Universal Pack System (UPS)

- Pack manifests MUST be loadable without accessing pack contents.
- Capability resolution MUST be by declared capability only, never by file path.
- Precedence MUST be explicit and data-driven; the engine MUST NOT hardcode tiers.
- The engine MUST support zero-pack boot and deterministic inspection.
- Canonical interface: `engine/include/domino/ups.h`

## Interface Hygiene and Safety

- Public interfaces MUST use opaque handles and MUST avoid exposing concrete
  structs.
- Public interfaces MUST define thread-safety, error handling, allocator, and
  determinism constraints explicitly.
- Public interfaces MUST NOT include platform, renderer, or OS headers.

## Enforcement Status (Explicit Gaps)

To preserve current behavior, the following norms are specified but not yet
enforced in implementation:

- Process execution is not yet the sole mutation entry point.
- Authority token checks are not yet applied to all mutations.
- Snapshot interfaces are not yet wired to existing state views.
- Compatibility negotiation is not yet mandatory across runtime/save/mod/pack.
- UPS resolution is not yet wired into legacy package/content scanning.

These gaps MUST be resolved only via explicit breaking revision.
