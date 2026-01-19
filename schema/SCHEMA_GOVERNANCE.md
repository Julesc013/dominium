# Schema Governance Law (DATA0)

This document defines non-negotiable governance for all schemas under `schema/`.
All data-driven systems MUST comply. Violations are merge-blocking.

## Scope

This law applies to:
- Engine and game authoritative data.
- Mods, saves, network payloads, and replay data.
- Tooling that produces or validates schema-bound content.

It does NOT authorize gameplay changes.

## Canonical Rules

- All persisted data MUST conform to a declared schema under `schema/**`.
- Schemas are authoritative; runtime code MUST NOT interpret authoritative data without a schema-aware reader.
- Ad-hoc JSON/TOML/YAML parsing is FORBIDDEN for authoritative data without a schema definition.
- Unknown fields MUST be preserved (skip-unknown) and MUST NOT be destroyed or reordered.
- Schema changes MUST NOT silently alter simulation semantics.
- Tool-only schemas MUST NOT be used by runtime systems.
- Schema definitions MUST be immutable at runtime; no dynamic mutation or hot patching.

## Schema Classes

Each schema MUST declare its class explicitly:

- Engine schemas: mechanics primitives and engine-owned data contracts.
- Game schemas: rules, policies, and domain logic data contracts.
- Tool-only schemas: authoring metadata or editor-only data not loaded at runtime.

**MUST NOT**
- Tool-only schemas consumed by runtime.
- Game schemas extending engine schemas without explicit governance approval.
- Engine schemas importing game or tool definitions.

## Schema Location and Ownership

- All schemas live under `schema/**` and are versioned.
- Ownership is aligned to top-level domains:
  - `schema/world/**` for game world data.
  - `schema/save/**` for saves.
  - `schema/net/**` for network payloads.
  - `schema/mod/**` for mod manifests and compatibility.
  - `schema/tool/**` for authoring-only metadata.

**Rationale**
Centralized schema ownership prevents format drift and preserves determinism.

## Integration Rules (Mandatory)

### Mods
- Mods MUST declare compatible schema versions.
- Mods MUST NOT extend engine schemas.
- Mods MUST NOT bypass determinism or performance rules.

### Save Files
- Save files MUST record schema versions for every schema referenced.
- Unknown fields MUST be preserved and round-tripped.
- Saves using unsupported major versions MUST be refused or migrated.

### Network
- Schema compatibility MUST be negotiated explicitly.
- Unknown fields MUST be preserved and forwarded when possible.

### Replays
- Replays MUST pin schema versions.
- Replays MUST refuse playback if required schemas are missing or incompatible.

## Determinism and Performance Guarantees

- Any schema change that affects simulation semantics MUST:
  - bump MAJOR version,
  - update determinism gates in CI,
  - update migration rules or refuse old versions.
- Validators MUST enforce:
  - no unbounded lists/maps in authoritative data,
  - presence of LOD/fidelity ladders where required,
  - absence of forbidden constructs in authoritative data (time, RNG, floats).

## Prohibitions (Absolute)

The following are FORBIDDEN:
- Unversioned schemas.
- Silent defaulting of new fields.
- Runtime mutation of schema definitions.
- Loading tool-only schemas in runtime.
- Schema changes without CI validation.

## FINAL0 Policy References
- `docs/LONG_TERM_SUPPORT_POLICY.md`
- `docs/DEPRECATION_POLICY.md`
- `docs/COMPATIBILITY_PROMISES.md`
- `docs/FEATURE_EPOCH_POLICY.md`
- `docs/RENDER_BACKEND_LIFECYCLE.md`
