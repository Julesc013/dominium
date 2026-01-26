# WorldDefinition (WD-0)

Status: binding.
Scope: world description contract, creation, and load boundaries.

## Core principle
A WorldDefinition is a complete, declarative description of an initial world
state. It is the ONLY thing the engine needs to create or load a world.

WorldDefinition is the ONLY world creation input. Templates must generate
WorldDefinitions; no other creation path is allowed.

WorldDefinitions are deterministic, serializable, extensible, provenance-
tracked, and pack-agnostic.

## What a WorldDefinition MUST include
1) Topology DAG
   - universe → galaxy → system → body → surface → patch (or equivalent)
   - stable identifiers
   - explicit parent/child relationships
2) Initial field states
   - minimal required fields only
   - explicit unknown/latent fields allowed
   - no derived/cached data
3) Enabled rulesets / policies
   - movement policies
   - authority policies
   - debug/mode policies (if enabled)
   - no hardcoded defaults
4) Spawn specification
   - topology node
   - coordinate frame
   - initial position/orientation
5) Provenance
   - template_id (or "user-defined")
   - template version
   - seed(s)
   - generator source (built_in / pack / tool)
6) Extension bag
   - namespaced, opaque data
   - preserved across load/save
   - ignored safely by older engines

## What a WorldDefinition MUST NOT include
- Runtime state deltas
- Live simulation objects
- Cached geometry
- UI state
- Assumptions about assets or packs
- Era or progression markers

## Schema
The canonical schema is `schema/world_definition.schema`.

Requirements:
- Versioned (small integer)
- Forward-compatible
- Unknown fields preserved
- Explicit minimum required shape
- Explicit non-semantic notes

## Templates and neutrality
World creation occurs via templates that output WorldDefinitions. Built-in and
pack templates register into the same registry, are presented identically, and
produce the same WorldDefinition format. No provider is privileged.

Built-in and pack templates are equivalent; their outputs are compared by
deterministic WorldDefinition hash.

The engine MUST NOT infer world structure or defaults outside the
WorldDefinition. If a field is absent or unknown, the engine must refuse or
degrade explicitly.

## Save, load, replay
- Saves embed the full WorldDefinition.
- Replays reference the WorldDefinition by value or hash.
- Loading a save does NOT require re-running the template.
- Missing capabilities at load time cause explicit refusal or degraded/frozen
  modes, never silent fallback.

## Refusal semantics (stable codes)
Refusals MUST include a stable code and structured payload and be surfaced
identically in CLI/TUI/GUI.

Required refusal codes:
- `WD-REFUSAL-INVALID` — invalid or incomplete WorldDefinition.
- `WD-REFUSAL-SCHEMA` — unsupported schema version.
- `WD-REFUSAL-CAPABILITY` — missing required capabilities.
- `WD-REFUSAL-TEMPLATE` — template refusal (invalid parameters or guarantees).

Payload shape (minimum):
```
refusal:
  code: <stable code>
  message: <short summary>
  details: <map>
```

## Tooling responsibilities
Required tools (headless, deterministic, no simulation mutation):
- WorldDefinition validator.
- WorldDefinition diff tool.
- Template equivalence tester.
- CLI world creation path.

## References
- `schema/world_definition.schema`
- `docs/worldgen/TEMPLATE_REGISTRY.md`
- `docs/worldgen/BUILTIN_TEMPLATES.md`
- `docs/roadmap/WORLD_CREATION_FLOW.md`
- `docs/arch/EXTENSION_RULES.md`
- `docs/arch/ARCH0_CONSTITUTION.md`
