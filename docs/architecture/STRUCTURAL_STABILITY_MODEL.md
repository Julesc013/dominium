# Structural Stability Model (TERRAIN0)

Status: binding.
Scope: process-driven stability and collapse for terrain.

## Core rule
Collapse triggers when derived stress exceeds `terrain.support_capacity`.

## Process-driven collapse
- Collapse is a Process that emits overlays (rubble, fill, debris).
- No implicit or background mutation is permitted.
- Collapse effects are auditable and provenance-tagged.

## Interactions
- Bridges/buildings are assemblies that interact with terrain via fields.
- No special-case "tunnel collapse" code paths are allowed.

## Minimum stability checks (BOUNDED)
Early models MUST be coarse and scalable:
- chunk-level stress envelopes
- support_capacity thresholds
- bounded neighbor influence

## Extension path
Future models may refine:
- multi-layer support envelopes
- material-aware stress propagation
- process-specific collapse responses

All extensions MUST remain process-driven, deterministic, and budgeted.
