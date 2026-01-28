# Pack Taxonomy (SHIP-0)

Status: binding.
Scope: canonical pack classes and their purpose.

Pack identity is always the `pack_id` from `pack_manifest.json` and must be
reverse-DNS per `docs/arch/ID_AND_NAMESPACE_RULES.md`. Packs are optional and
capability-driven; no pack is required by code.

## Canonical Classes

### Core Ontology Packs (Optional, Recommended)
Purpose: Provide generic primitives (units, interfaces, minimal FAB families).
They are never required by code and may be replaced by mods or alternate packs.

Examples:
- org.dominium.core.units
- org.dominium.core.interfaces
- org.dominium.core.materials.basic
- org.dominium.core.processes.basic
- org.dominium.core.standards.basic

### Worldgen Packs
Purpose: Define topology, anchors, and templates for world creation. These are
data-only and must not encode gameplay rules.

Examples:
- org.dominium.worldgen.minimal
- org.dominium.worldgen.realistic.earth
- org.dominium.worldgen.realistic.sol
- org.dominium.worldgen.realistic.milkyway

### Content / Gameplay Packs
Purpose: Optional depth and realism. They remain fully optional and must be
capability-resolved.

Examples:
- org.dominium.content.real.materials
- org.dominium.content.real.vehicles
- org.dominium.content.magic.alchemy

### Examples / Tutorial Packs
Purpose: Learning and demonstration only.

Examples:
- org.dominium.examples.simple_factory
- org.dominium.examples.failure_modes

### Localization Packs
Purpose: UI strings, help text, and locale resources only. These packs must not
affect simulation semantics.

Examples:
- org.dominium.l10n.en_us
- org.dominium.l10n.ja_jp

## Pack Class Tags (Advisory)
Pack manifests may label themselves using `pack_tags` to indicate class. Tags
are advisory and never mandatory for correctness.

Recommended tags:
- pack.class.core_ontology
- pack.class.worldgen
- pack.class.content
- pack.class.examples
- pack.class.localization
