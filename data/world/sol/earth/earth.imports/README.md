# Earth Import Hooks (CONTENT2)

Version: 1.0.0
Status: draft

## Purpose
Define how higher-resolution Earth datasets are layered onto the canonical
Earth regions and surfaces without embedding mechanics.

## Supported import types (future)
- Heightmaps (land and bathymetry)
- Climate rasters (temperature, precipitation)
- Political boundaries (data-only, later phase)
- Satellite-derived land cover

## Overlay rules
- Imported data overlays canonical regions using deterministic transforms.
- Missing data is filled via explicit procedural defaults only.
- All imports must declare version, checksum, and provenance.
- No runtime guessing or online lookups are permitted.

## Mapping expectations
- Each import declares its target surface or region scope.
- Overlay precedence follows `docs/SPEC_WORLD_SOURCE_STACK.md`.
- Unknown fields are refused unless explicitly marked non-sim metadata.

## Validation
- Imports must pass schema validation and migration checks.
- Raster sizes and lists are bounded; no unbounded datasets.
