# Milky Way Canonical Data (CONTENT3)

Version: 1.0.0
Status: draft

## Scope
This dataset defines a scalable Milky Way backbone:
- Galaxy record with barred-spiral tags and deterministic bounds.
- Spiral arms with geometric scaffolding tags and density classes.
- Bounded galactic regions (core, disks, halo, voids, clusters).
- Anchor systems for navigation and lore (Sol, nearby stars, core reference).
- Procedural fill rules for deterministic system generation between anchors.

## Anchor rationale
Anchors provide:
- Navigation reference points (Sol, Alpha Centauri, Sirius).
- Strategic and lore-relevant systems (Cygnus X-1, Sagittarius A*).
- Density and hazard exemplars for procedural rules.

## Procedural fill philosophy
- Seed-driven, deterministic rule sets.
- Region and arm rules override galaxy-wide fallbacks.
- No runtime randomness without fixed seeds.

## Extension strategy
- Add new anchors in `milky_way.anchors.json`.
- Refine arm scaffolds and region boundaries via new boundary refs.
- Expand procedural rules with new classes; bump schema versions as needed.

## Epistemic expectations
Galactic knowledge is not omniscient. Distant regions and anchors may be
unknown until discovered by sensors or exchanged by communication networks.
