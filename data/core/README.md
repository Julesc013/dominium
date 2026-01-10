# Core Data (Authoring)

This directory contains human-authored core data sources for the universe canon.
Files under `/data/core` are compiled into deterministic TLV packs by
`coredata_compile`; runtime code never reads these files directly.

Authoring rules and sim-affecting boundaries are defined in:
- `docs/SPEC_CORE_DATA.md`
- `docs/SPEC_CORE_DATA_PIPELINE.md`
