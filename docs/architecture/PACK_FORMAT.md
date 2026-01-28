# Pack Format (UPS1)

Status: binding.
Scope: UPS pack structure, manifest format, and safety rules.

## Pack structure
```
data/packs/<pack_id>/
├── pack.toml
├── data/
├── schema/
├── ui/
└── docs/
```

Rules:
- `pack.toml` is REQUIRED.
- No executable code inside packs.
- No hardcoded paths.
- No implicit load-order dependencies.
- Everything namespaced (reverse-DNS).

## Manifest schema
The canonical manifest schema is:
- `schema/pack_manifest.schema`

Required fields (stable):
- pack_id
- pack_version
- pack_format_version
- provides[]
- depends[]
- requires_engine
- extensions{}

Unknown fields MUST be preserved.

## Format notes
- `pack.toml` is the runtime manifest format.
- `pack_manifest.json` is a schema-mapped representation for tooling/source control.
- Conversion between formats MUST preserve unknown fields.

## Safety
- Packs MUST be loadable without reading pack contents.
- Capabilities are resolved by identifier only; file paths are never used.
- No pack may embed executable logic.

## See also
- `docs/arch/MOD_ECOSYSTEM_RULES.md`
- `docs/arch/LOCKFILES.md`
- `schema/pack_manifest.schema`
