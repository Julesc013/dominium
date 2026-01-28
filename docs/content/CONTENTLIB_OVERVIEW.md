# Content Library Overview (CONTENTLIB-0)

This document describes the minimal, official, **optional** data packs shipped
with Dominium. These packs exist to demonstrate the fabrication ontology and
provide a safe starting point for mods. No pack is required for correctness.

## Why these packs exist
- Provide tiny, deterministic examples of FAB-0 schemas.
- Offer neutral defaults for tooling and onboarding.
- Remain fully replaceable by mods or alternate packs.

## Design principles
- Data only; no executable code.
- Abstract and non-realistic values.
- No gameplay rules, balance, or era assumptions.
- Capability-driven, not pack-name driven.

## Pack list (minimal set)
Core ontology (optional, recommended):
- `org.dominium.core.units`
- `org.dominium.core.interfaces`
- `org.dominium.core.materials.basic`
- `org.dominium.core.parts.basic`
- `org.dominium.core.processes.basic`
- `org.dominium.core.standards.basic`

Worldgen:
- `org.dominium.worldgen.minimal`

## Replace or override with mods
Mods can:
- Provide the same capabilities with different data.
- Replace any or all records with new identifiers.
- Disable official packs entirely and remain valid.

The engine and game must continue to run with zero packs installed.
