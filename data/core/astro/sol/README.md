# Sol System (Authoring)

Sol is the mechanically densest reference system in the core data set. All
other systems are treated as subsets of Sol's mechanics graph. Sol does not
require special-case runtime logic.

Mechanics coverage:
- System mechanics: `sol_reference_system` captures baseline navigation,
  debris, radiation, warp, and survey modifiers for the Sol anchor.
- Region mechanics: heliosphere and belt/cloud regions are modeled as REGION
  anchors in `data/core/cosmo/regions.toml`.
- Site mechanics: surface/atmosphere/lagrange sites are listed in
  `data/core/astro/sol_sites.toml` and bind to site profiles in
  `data/core/mechanics/site_profiles.toml`.

See:
- `docs/SPEC_COSMO_CORE_DATA.md`
- `docs/SPEC_MECHANICS_PROFILES.md`
