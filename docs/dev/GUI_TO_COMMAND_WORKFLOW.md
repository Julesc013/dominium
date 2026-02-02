Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# GUI → Command Workflow

This is the canonical workflow for changing UI IR or command bindings.

## 1) Edit UI IR

- Update `.tlv` UI documents under `tools/<app>/ui/doc/`.
- Ensure widget names follow `docs/dev/UI_NAMING_CONVENTIONS.md`.

## 2) Auto-annotate accessibility and localization

Run:

```sh
tool_ui_doc_annotate --repo-root . --ui-index tools/ui_index/ui_index.json --write
```

This will:
- add missing accessibility properties
- add missing localization keys
- update JSON mirrors

## 3) Regenerate bindings

Run:

```sh
tool_ui_bind --repo-root . --ui-index tools/ui_index/ui_index.json --out-dir libs/appcore/ui_bind --write
```

This will regenerate:
- UI command binding tables
- accessibility maps
- localization usage report

## 4) Build and test

- Build GUI targets.
- Run TestX; UI_BIND_PHASE must pass.

## 5) Commit generated files

Generated artifacts under `libs/appcore/ui_bind/` are checked in and must remain in sync.
