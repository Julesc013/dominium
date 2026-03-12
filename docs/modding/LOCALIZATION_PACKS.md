Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Localization Packs (UX-1)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


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
