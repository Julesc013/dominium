# Localization Model (UX-1)

Localization is implemented strictly as content packs. Localization must never affect simulation or determinism. UI logs and intent streams use stable identifiers, not localized text.

## String IDs
- All human-facing UI strings are referenced by stable string ids.
- String ids are stable, ASCII, and namespaced (e.g., `ui.client.title`); case-insensitive.
- Fallback English text may exist in code for safety, but is not authoritative.

## Pack Layout
A localization pack is a standard pack with one or more locale files.

```
pack.toml
data/locale/en_US.l10n
data/locale/ja_JP.l10n
```

Each `.l10n` file uses a deterministic line format:

```
DOMINIUM_L10N_V1
locale_id=en_US
ui.client.title=Dominium Client
ui.client.menu.new_world=New World
```

Rules:
- The first non-empty line must be `DOMINIUM_L10N_V1`.
- `locale_id` is advisory metadata.
- Duplicate ids resolve by deterministic pack order (later packs override earlier).
- Unknown keys are preserved by tooling.

## CLI Integration
Front-ends may accept:
- `--locale <id>`
- `--locale-pack <path>` (repeatable)

Localization affects presentation only. Event logs and intent ids remain stable.

## Schema
- `schema/localization_pack.schema`

## References
- docs/ui/CLI_CANON.md
- docs/ui/UX_OVERVIEW.md
