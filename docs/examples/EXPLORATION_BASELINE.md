Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Exploration Baseline (W0)

This example describes the minimal, data-defined exploration world that ships with the client
and works with zero content packs.

## Template

- Template ID: `world.template.exploration_baseline`
- Source: `data/world/templates/exploration_baseline.worlddef.json`
- Structure: Universe → Milky Way → Sol → Earth (data-only, no assets required)
- Spawn: deterministic per seed on the Earth surface

The client loads the template from:
1) `DOM_INSTALL_ROOT` (if set),
2) `DOM_DATA_ROOT` (if set), or
3) the current working directory.

## Create World (CLI)

```
dominium_client create-world template=world.template.exploration_baseline seed=42
```

Expected output includes:

- `world_create=ok`
- `world_save=ok`

## Navigation & Camera

Navigation modes (meta-law):

- `policy.mode.nav.surface`
- `policy.mode.nav.free`
- `policy.mode.nav.orbit`

Camera modes:

- `camera.first_person`
- `camera.third_person`
- `camera.free`

Example batch run:

```
dominium_client batch new-world template=world.template.exploration_baseline seed=42; \
  mode policy.mode.nav.surface; \
  move dx=1 dy=0 dz=0; \
  camera-next; \
  inspect-toggle; \
  hud-toggle; \
  save; \
  replay-save
```

## Inspect Mode

Inspect mode is always available and read-only:

- `inspect-toggle` (CLI)
- `inspect` (alias)

The world view shows:

- current domain (node id)
- position and orientation
- geo lat/lon/alt when Earth radius is known
- active mode and camera
- inspect/hud state

## Save / Load / Replay

Artifacts include compat reports:

- `world.save.compat_report.json`
- `session.replay.compat_report.json`

Example:

```
dominium_client load path=data/saves/world.save
dominium_client replay-save path=data/saves/session.replay
```

## Zero-Pack Guarantee

This template is data-only and requires no external packs. The client should boot,
create, move, inspect, save, load, and replay deterministically with zero assets installed.