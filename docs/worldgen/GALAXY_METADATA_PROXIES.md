# Galaxy Metadata Proxies

GAL-0 adds a minimal, deterministic metadata layer for galaxy cells. These fields are canonical field values, but they are explicitly provisional proxy semantics rather than astrophysical truth.

## Proxy Fields

### `field.stellar_density_proxy`

- Normalized scalar proxy for expected star-system density per galaxy cell.
- Initial derivation:
  - uses galaxy-frame cell position
  - reuses MW density priors already used by MW-0 cell generation
- Intended downstream use:
  - system occurrence priors
  - starfield band brightness alignment
  - future hazard/lore weighting

### `field.metallicity_proxy`

- Normalized scalar proxy for radial metallicity trend.
- Initial derivation:
  - decreases with galactocentric radius
  - reuses MW metallicity gradient priors
- Intended downstream use:
  - planet occurrence priors
  - later stellar population overlays

### `field.radiation_background_proxy`

- Scalar proxy for galactic background radiation intensity.
- Initial derivation:
  - rises toward the galactic center
  - falls with vertical distance from the midplane
  - remains a stub, not a transport simulation
- Intended downstream use:
  - future hazards
  - lore/scan overlays
  - optional starfield tint/intensity alignment

### `field.galactic_region_id`

- Categorical region proxy for coarse galaxy structure.
- Allowed values:
  - `region.bulge`
  - `region.inner_disk`
  - `region.outer_disk`
  - `region.halo`
- Initial derivation:
  - thresholded from galactocentric radius and height
  - deterministic tie-breaks via bounded threshold rules

## Deterministic Derivation

- Inputs:
  - galaxy cell position in `frame.milky_way.galactic`
  - `data/registries/galaxy_priors_registry.json`
- Rules:
  - use integer arithmetic only
  - clamp all proxy outputs to bounded scalar ranges
  - sort all evaluation/update output by canonical `geo_cell_key`
  - round only through explicit integer division and clamping

## Extensibility

These proxies are placeholders for later domain packs and higher-fidelity galaxy models:

- stellar lifecycle / enrichment
- compact objects
- supernova and hazard domains
- gas/dust/cloud structure
- authored lore overlays

Future systems may replace the proxy derivation path, but the proxy fields remain valid fallback semantics for low-fidelity or compatibility profiles.

## Stability

All GAL-0 fields and supporting registries are `provisional`.

Required replacement planning:

- `future_series`: `GAL+/ASTRO`
- `replacement_target`: `dynamic galaxy domain packs`

No exact Milky Way claim is made here. GAL-0 is a deterministic structural stub only.
