# Dominium Root Recycling Plan

Status: dry_run_no_apply

Q52 plans only. It does not move files, delete files, rename files, rewrite references, create aliases, or create shims.

## Selected Root

| Root | Files | Risk | Status | Next Action |
|---|---:|---|---|---|
| `ide/` | 4 | high | review_required | Preserve tracked manifest surfaces; validate schema/examples before any future map. |

## File Plan

| Path | Kind | Status | Fate | Risk | Future Need |
|---|---|---|---|---|---|
| `ide/README.md` | doc | active | keep | authority_sensitive | remain at ide/README.md unless a future reviewed root plan proves a replacement authority path |
| `ide/manifests/projection_manifest.schema.json` | schema | active | keep | identity_sensitive | remain under ide/manifests/ unless future schema ownership review approves a move-map and alias plan |
| `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json` | fixture | template_only | keep | generated_sensitive | remain under ide/manifests/projection_manifest_examples/ unless future example fixture map is approved |
| `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json` | fixture | template_only | keep | generated_sensitive | remain under ide/manifests/projection_manifest_examples/ unless future example fixture map is approved |

## Future Required Maps

- Salvage map: required before any future file-level migration decision; current recommendation is preserve all tracked files.
- Move map: not proposed in Q52.
- Path alias plan: not proposed in Q52.
- Reference rewrite plan: not proposed in Q52.

## Exception Retirement Conditions

- Generated IDE project outputs remain ignored under /ide/** except README and manifests.
- Projection manifest schema and examples stay tracked or a future reviewed map proves an equivalent canonical location.
- All references to IDE projection generation commands are inventoried before any path rewrite is proposed.
