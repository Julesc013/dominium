# Astro Constants (Authoring)

This directory contains authoring sources for minimal astro constants that are
explicitly used by runtime. These files are compiled to TLV packs by
`coredata_compile`.

Notes:
- Units are explicit in field names (e.g., `radius_m`, `mu_m3_s2`).
- `atmosphere_profile_id` is a forward reference to atmosphere profile data
  defined elsewhere in core data.
- Sol system site definitions live in `data/core/astro/sol_sites.toml` with
  additional intent notes in `data/core/astro/sol/README.md`.

See:
- `docs/SPEC_CORE_DATA.md`
