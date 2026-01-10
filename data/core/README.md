# Core Data (Authoring)

This directory contains human-authored core data sources for the universe canon.
Files under `/data/core` are compiled into deterministic TLV packs by
`coredata_compile`; runtime code never reads these files directly.

Authoring rules and sim-affecting boundaries are defined in:
- `docs/SPEC_CORE_DATA.md`
- `docs/SPEC_CORE_DATA_PIPELINE.md`

Consistency notes (v1):
- `evidence_grade` marks confirmed vs candidate anchors; candidates must never
  be required for progression.
- `mechanics_profile_id` in cosmo anchors must match
  `data/core/mechanics/system_profiles.toml`.
- Procedural expansion uses only `data/core/cosmo/procedural_rules.toml`; there
  are no implicit defaults.

Current anchor totals (v1):
- systems: 32
- regions: 12
