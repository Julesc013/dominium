# Geology and Resources Baseline (GEOLOGY2)

Status: baseline.
Scope: static subsurface geology and resource field sampling for T2.

## What exists
- Subsurface geology is represented as fields, not entities.
- Minimum geology fields:
  - `geology.strata_layers`
  - `geology.hardness`
  - `geology.fracture_risk` (optional)
- Resource density fields:
  - `resource.density.<resource_id>` (0..1, unit-tagged)
- Providers are layered (procedural base → anchor → simulation → overlays).
- Sampling is deterministic, budgeted, and LOD-aware.
- Inspection tools include:
  - Core sample along a ray (strata segments + resource densities).
  - Surface-projected geology map (coarse).
  - Resource slice inspection.

## What does not exist yet
- No mining, extraction, or inventory logic.
- No fluid, erosion, or weather simulation.
- No per-tick global updates or background mutation.
- No planet/station special casing.

## Determinism and scaling
- Authoritative logic is fixed-point only.
- Sampling cost is bounded by domain policy budgets.
- Cached tiles are disposable; providers remain canonical.
- Collapse/expand uses macro capsules with coarse invariants and statistics.

## Maturity labels
Current geology models are early and bounded:
- `model.geology.procedural_base`: maturity.bounded
- `model.geology.anchor`: maturity.extension_path
- `model.geology.simulation`: maturity.future
- `model.geology.overlays`: maturity.future
- `model.resource.density`: maturity.bounded

## Why these omissions
T2 establishes a stable, deterministic subsurface representation first. Mining,
erosion, fluids, and construction are deferred to later prompts so that the
field model and scaling guarantees stay locked.

## See also
- `docs/worldgen/GEOLOGY_STORAGE.md`
- `docs/architecture/TERRAIN_PROVIDER_CHAIN.md`
- `docs/architecture/UNIT_SYSTEM_POLICY.md`
