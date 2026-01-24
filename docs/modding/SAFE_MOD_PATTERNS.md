# Safe Mod Patterns

Status: canonical.
Scope: explicitly supported mod patterns.
Authority: canonical. Mods SHOULD follow these patterns.

## Supported patterns
- Add new model families via `schema/worldgen_model.schema`.
- Add new refinement layers with explicit precedence tags.
- Add new epistemic datasets (knowledge and measurement artifacts).
- Add new reality domains (magic, alt-physics) as optional packs.
- Add incorrect or fictional knowledge as epistemic overlays.

## Required behaviors
- All additions MUST be capability-resolved.
- All additions MUST include provenance records.
- All additions MUST preserve unknown fields and tags.
