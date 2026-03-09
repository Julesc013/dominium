Status: CANONICAL
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none

# MVP Viewer Shell

## Purpose

UX-0 defines the minimal playable viewer shell for Dominium v0.0.0.

The viewer shell is a deterministic, lens-first client surface that lets a user:

- start an MVP session from `profile.bundle.mvp_default`
- set a seed
- traverse with freecam or embodied lenses
- teleport through lawful process plans
- inspect visible objects, fields, systems, and overlays
- view map/minimap projections
- view overlay provenance through the canonical explain tool

The viewer shell is presentation and control orchestration only.
It must not read or mutate TruthModel directly.

## Binding Rules

- UI consumes PerceivedModel and derived view artifacts only.
- UI must not import or read `truth_model`, `universe_state`, or authoritative runtime rows directly.
- Any authoritative mutation request must remain a process plan:
  - `process.camera_teleport`
  - `process.camera_set_view_mode`
  - `process.camera_set_lens`
  - `process.worldgen_request`
- Inspection content must come from:
  - `process.inspect_generate_snapshot`
  - derived inspection overlays
  - explain/provenance tools
- Overlay provenance must use the canonical GEO-9 property-origin explain tool.

## Core User Flows

### Launch Flow

Boot flow is:

1. `Boot`
2. `BundleSelect`
3. `SeedSelect`
4. `SessionRunning`

The canonical launch target is `bundle.mvp_default`.
Dev launch defaults to deterministic `seed=0` unless explicitly overridden.
Release launch requires an explicit user seed.

## Teleport Flow

The shell must expose deterministic teleport commands:

- `/tp sol`
- `/tp earth`
- `/tp random_star`
- `/tp <object_id>`
- `/tp <coords>`

Teleport behavior rules:

- teleport does not directly move truth from UI code
- teleport emits a deterministic process sequence
- if destination refinement is missing, the sequence must request worldgen first
- random star selection must be derived from `universe_seed + counter` via named deterministic hashing
- teleport selection order must be stable across platforms

## Lens Flow

The shell must expose profile-gated lens switching:

- `lens.freecam`
- `lens.fp`
- `lens.tp`
- `lens.inspect`

Lens access rules:

- freecam is dev/lab gated
- inspect lens is observer/admin gated
- first-person and third-person require embodiment
- lens switching is resolved through lens profiles and authority entitlements, not hardcoded mode branches

## Panels

### Object Inspector

The object inspector must show only visible/derived object data:

- `object_id`
- object type / kind
- parent relationships
- key pinned or procedural physical parameters
- current refinement / LOD state

### Field Inspector

The field inspector must show only field values visible through the current lens/view artifact:

- `temperature`
- `daylight`
- `pollution`

### Domain Panels

The viewer shell may expose additional derived panels when backing artifacts exist:

- surface tile panel
- geometry cell panel
- logic/network panel
- system/capsule panel

Absent data must degrade deterministically to empty or redacted sections.

### Overlay Provenance

The viewer shell must expose a “why is this value set?” panel.

This panel must be backed by the canonical property-origin explain tool and show:

- current layer id
- prior value chain
- explain contract ids
- deterministic provenance/report fingerprints

## Views

### Map View

Map view is a GEO-5 projection + lens artifact.

Rules:

- default projection is `geo.projection.ortho_2d`
- available layers are selectable but profile/lens redaction still applies
- no omniscient terrain or marker visibility unless the current profile/tooling explicitly allows it

### Minimap

Minimap is a reduced-resolution ROI map tied to current camera/body position.

Rules:

- minimap uses deterministic downsampling
- minimap cell bounds are budget-capped deterministically
- minimap redaction must match current lens/epistemic limits

### CLI / TUI / GUI

- CLI/TUI uses ASCII summaries over projected view artifacts
- GUI uses buffer-based rendering from derived artifacts only
- renderers may differ in presentation backend, but must consume the same RenderModel/view-artifact inputs

## Inspection Contract

Inspection is not a direct truth read.

The shell must compose:

- `process.inspect_generate_snapshot`
- `src/client/interaction/inspection_overlays.py`
- explain/provenance tools

The shell must not synthesize hidden state by reading runtime internals.

## Performance / Budget Contract

- map generation must cap cell counts deterministically
- debug-heavy surfaces must throttle deterministically
- view artifacts must be cacheable by truth anchor hash plus request hashes
- no viewer path may eagerly instantiate galaxy, systems, or surface tiles

## Non-Goals

UX-0 does not include:

- a full launcher
- art packs, models, or textures
- live wall-clock effects
- ad hoc truth-only admin panels outside entitlement/profile rules
- authoritative mutation from UI code

## Required Outcome

A UX-0 compliant viewer shell provides a lawful, deterministic substrate for:

- galaxy traversal
- Sol/Earth teleport
- map/minimap viewing
- inspect/provenance access
- cross-renderer presentation

without breaking observer/renderer/truth separation.
