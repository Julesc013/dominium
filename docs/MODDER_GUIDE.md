Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Modder Guide

Dominium is data‑first. Mods are content packs that extend reality through schemas and processes. You do not need to change code to add materials, parts, assemblies, laws, or worldgen anchors.

## Core principles

- Data defines reality. Code interprets it.
- Identifiers are namespaced and never reused.
- Unknown fields must round‑trip without loss.
- Refusals are explicit and stable. Do not rely on silent fallbacks.

## Creating a pack safely

- Start with a clear pack ID and version.
- Follow the pack taxonomy in `docs/distribution/PACK_TAXONOMY.md`.
- Use the schemas in `schema/` and respect unit policies in `docs/architecture/UNIT_SYSTEM_POLICY.md`.
- Validate with `tools/pack/pack_validate.py` and `tools/fab/fab_validate.py`.

## Maturity labels

Packs declare maturity so others know what to expect:

- PARAMETRIC: safe to deepen via parameters.
- STRUCTURAL: safe to deepen via new sub‑objects.
- BOUNDED: placeholder that will need replacement.
- INCOMPLETE: known insufficient, for testing only.

## Compatibility and stability

- Never reuse an ID with new meaning.
- Preserve unknown fields so older tools can round‑trip data.
- Avoid hard dependencies on other packs. Use capability requirements instead.
- Expect refusals when required capabilities are missing.

## Sharing mods

- Use bundles to share packs, blueprints, saves, and replays.
- Bundles are portable and never contain executable code.
- Use the share and bugreport tools for deterministic, inspectable artifacts.

If you need a new primitive, document the gap first and propose it through the contribution process.