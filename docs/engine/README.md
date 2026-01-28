# Engine Layer Documentation

This directory defines the authoritative engine-layer contract. The canonical
architecture rules live in `docs/architectureitecture/INVARIANTS.md`,
`docs/architectureitecture/TERMINOLOGY.md`, `docs/architectureitecture/NON_GOALS.md`,
`docs/architectureitecture/COMPATIBILITY_PHILOSOPHY.md`, and
`docs/architectureitecture/MENTAL_MODEL.md`. If there is any conflict, those documents
are authoritative.

## Scope

- The engine MUST be content-agnostic and MUST boot with zero assets.
- The engine MUST be deterministic and replay-safe for authoritative simulation.
- The engine MUST expose primitives and interfaces only; it MUST NOT encode
  gameplay mechanics or platform assumptions.
- The engine MUST treat renderer/client/server/platform code as
  non-authoritative.
- The engine MUST support headless/CI/server-only operation.

## Canonical Engine Interfaces

The engine exposes the following primitive interfaces:

- Topology DAG: `engine/include/domino/topology.h`
- Domain volumes: `engine/include/domino/domain.h` (spatial domain primitives
  are in `engine/include/domino/world/domain_*.h`)
- Representation tiers: `engine/include/domino/representation.h`
- Field layers: `engine/include/domino/field_layer.h`, `engine/include/domino/dfield.h`
- Process descriptors and hooks: `engine/include/domino/process.h`
- Capability descriptors and matching: `engine/include/domino/capability.h`
- Authority tokens: `engine/include/domino/authority.h`
- Snapshots (objective/subjective): `engine/include/domino/snapshot.h`
- Knowledge/latent state: `engine/include/domino/knowledge_state.h`
- Deterministic provenance and seed namespaces: `engine/include/domino/provenance.h`
- Compatibility modes and negotiation inputs: `engine/include/domino/compat_modes.h`
- Universal Pack System (UPS) manifests and capability resolution: `engine/include/domino/ups.h`

Note: `engine/include/domino/caps.h` is for system/backend selection and MUST
NOT be used as simulation capability descriptors.

UPS runtime details are defined in `docs/engine/UPS_RUNTIME.md`.

## Enforcement Status (Explicit)

To preserve existing behavior, the following requirements are specified but not
yet enforced in current engine code:

- All authoritative state changes flowing through the process executor.
- Authority token enforcement on all mutating operations.
- Snapshot creation and query routing through the snapshot interfaces.
- Compatibility negotiation applied to runtime/save/mod/pack interactions.
- UPS manifest loading and capability resolution wired into package/content scanning.

These gaps are deliberate. Enforcing them without a breaking revision would
change behavior. See `docs/engine/PRIMITIVES.md` for the normative contracts.

## Non-Features (Engine Layer)

- The engine MUST NOT implement gameplay rules, balance, or content logic.
- The engine MUST NOT require assets, clients, or UI to operate.
- The engine MUST NOT include platform, renderer, audio, or OS code in
  authoritative paths.
- The engine MUST NOT silently coerce or repair incompatible data.
