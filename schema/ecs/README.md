# ECS Schema (ECSX0)

This folder defines the canonical component schema model that separates
logical component meaning from physical storage layouts.

## Contents
- `SPEC_COMPONENT_SCHEMA.md` — component/field definitions, ownership, versioning.
- `SPEC_FIELD_IDS.md` — field_id stability and assignment policy.
- `SPEC_STORAGE_BACKENDS.md` — allowed storage backends and determinism rules.
- `SPEC_PACKING_AND_DELTAS.md` — packing, serialization, and delta rules.

## Authority
These specs are binding for ECSX0 and subordinate to ARCH0. If a runtime
implementation conflicts with these specs, the specs win.
