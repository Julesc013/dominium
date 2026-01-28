# Localization Packs (UX-1)

Localization is delivered as packs. Packs are optional and never affect simulation outcomes.

## Structure
```
pack.toml
data/locale/en_US.l10n
```

## File Format
```
DOMINIUM_L10N_V1
locale_id=en_US
ui.client.title=Dominium Client
ui.client.menu.new_world=New World
```

## Rules
- String ids are stable and namespaced.
- Later packs override earlier packs deterministically.
- Localization packs must not include gameplay data or scripts.

## References
- docs/ui/LOCALIZATION_MODEL.md
- docs/distribution/PACK_TAXONOMY.md
