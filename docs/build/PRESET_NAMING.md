# Preset Naming

Status: PROVISIONAL

Phase: POST-CONVERGE-10

## Good Tuple Names

Tuple IDs should expose their actual build dimensions:

```text
verify.winnt7.x86_64.msvc143.mt.debug
verify.host.host.host_default.host.debug
research.xp.x86.msvc141_xp.mt.release
```

## Bad Names

Avoid vague names in tuple/component IDs:

- `legacy`
- `modern`
- `universal`
- `compat`
- `broad_compatibility`
- `early_modern_desktop`
- `retro_research`
- `advanced_modern`

Those words hide important dimensions and tend to become support claims without evidence.

## Field Discipline

Do not encode renderer or API nicknames such as `gl1`, `gl2`, `gl4`, `dx9`, `dx11`, `dx12`, or `vk1` into primary component IDs when they should be fields. Use renderer family fields such as `opengl`, `direct3d`, `software`, and `null`, with version/profile fields when a specific API target is needed.

Use explicit tuple fields for:

- floor
- architecture
- toolchain
- runtime
- config
- platform
- renderer
- package intent

Generated preset names may use the tuple ID directly, prefixed with `tuple.`.
