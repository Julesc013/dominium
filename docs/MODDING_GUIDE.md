# MODDING_GUIDE (MOD0)

Status: draft  
Version: 1

## Scope
This guide defines how mods are packaged, validated, and resolved deterministically.
Mods are data-only and must not introduce new engine code or privileged behavior.

## Manifest basics
Manifests are line-based key/value files. Required fields:
- `mod_id`
- `mod_version`
- `sim_affecting`
- `payload_hash`

Example:
```
mod_id=example.mod
mod_version=1.2.0
schema_dep=world@1.0.0-2.0.0
feature_epoch=war@3-5
sim_affecting=1
dependency=base.assets@1.0.0-2.0.0
conflict=other.mod@1.0.0-1.1.0
required_capability=ui
render_feature=dgfx_soft
payload_hash=fnv1a64:0123456789abcdef
```

## Deterministic packaging
Use the mod pack builder to hash payloads deterministically:
- `mod_pack_builder --root <mod_root> --manifest <manifest_path> --out <pack_path>`
- The pack contains an ordered file list and payload hash.

## Compatibility and safe mode
Compatibility checks validate:
- Schema version ranges
- Feature epochs
- Required capabilities
- Render feature availability
- Performance budget class

Results are deterministic: `ACCEPT`, `ACCEPT_WITH_WARNINGS`, `REFUSE`.

Safe mode is explicit and reproducible:
- `NONE`: refuse incompatibilities.
- `NON_SIM_ONLY`: disable sim-affecting mods; keep compatible non-sim mods.
- `BASE_ONLY`: disable all mods.

## Instance binding
- Resolved mod order and graph hash must be pinned in instance manifests.
- Replays and saves bind to the mod graph identity hash.

## Tooling
- `mod_pack_validator` validates packs and mod graphs.
- Refusals are explicit and never auto-repaired.

## Prohibitions
- No executable code injection into the engine.
- No runtime schema mutation.
- No silent enable/disable of mods.
