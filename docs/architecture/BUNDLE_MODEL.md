Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Bundle Model (SHARE0)

Status: FROZEN.  
Scope: shareable bundles for saves, replays, blueprints, and modpacks.

## Bundle Types (Authoritative)

All bundles share a common container format.

A) Save Bundle
- Purpose: share a world save.
- Contents: save artifact, capability_lockfile, pack references, optional embedded packs, read-only instance metadata.

B) Replay Bundle
- Purpose: share a deterministic replay or bug reproduction.
- Contents: replay artifact, capability_lockfile, compat_report, optional embedded packs, runtime metadata.

C) Blueprint Bundle
- Purpose: share designs (assemblies, processes, layouts).
- Contents: blueprint artifact, referenced schema objects, optional embedded part/material definitions, compatibility hints.

D) Modpack Bundle
- Purpose: share a curated set of packs.
- Contents: modpack manifest, capability_lockfile, pack references, optional embedded packs, profile suggestions.

## Common Container

Schema:
- `schema/bundle.container.schema`

Rules:
- Bundles are immutable once created.
- Bundles are portable (single file or folder).
- Bundles do NOT contain executable code.
- Bundles do NOT bypass capability checks.

## Export Semantics

- User chooses pack references only or embeds packs.
- Bundles are generated atomically.
- compat_report is generated at export time.

## Import Semantics

- Bundle is inspected before import.
- compat_report is shown before import.
- Missing packs are resolved via OPS-0 sources (never implicitly).
- User explicitly confirms any degraded modes.
- Incompatible bundles refuse explicitly.

## Safety & Trust

- Bundles inherit trust tier from creator.
- Embedded packs are scanned/validated.
- No bundle executes code.

## Advanced Users

Power users can inspect bundle internals and override pack resolution via tools.