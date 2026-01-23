# Content Overview

This document defines what "content" means in Dominium. It MUST be read
alongside `docs/content/UPS_OVERVIEW.md` and `docs/architecture/TERMINOLOGY.md`.

## Content Is Optional

- Content is delivered via packs and is ALWAYS optional.
- The engine and game MUST boot and run with zero packs installed.
- Content MUST be discoverable by capability, never by file path.

## What Content Provides

Content packs provide data that describes:
- Topology nodes and relationships
- Domains and domain volumes
- Fields and their representation tiers
- Processes, capabilities, and institutions (as descriptors only)
- Knowledge artifacts such as scenarios

Content MUST NOT encode behavior, rules, or authoritative logic.

## Pack Structure

Each pack MUST include:
- A plain-text `pack.manifest` for UPS loading
- A schema-aligned `pack_manifest.json`
- Schema-aligned content files in `content/`

## Required Metadata

Every content record MUST include:
- A stable ID
- `provenance_ref`
- Explicit representation tier metadata (when applicable)
- Explicit `detail_absence` and a `refinement_ceiling` in extensions

## Canonical Base Packs

Canonical, optional base packs live under `data/packs/` and are documented in
`docs/content/BASE_PACKS.md`.
