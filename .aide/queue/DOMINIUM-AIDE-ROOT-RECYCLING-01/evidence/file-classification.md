# File Classification

Status: needs_review

Full JSON classification: `.aide/roots/dominium-root-file-classification.json`

| Path | Kind | Status | Fate | Risk | Target Hint | Validators Required | Review |
|---|---|---|---|---|---|---|---|
| `ide/README.md` | doc | active | keep | authority_sensitive | Keep at current path unless a future reviewed root plan proves a replacement authority path. | roots validate; repo validate; docs reference validation if future rewrite is proposed | required |
| `ide/manifests/projection_manifest.schema.json` | schema | active | keep | identity_sensitive | Keep under `ide/manifests/` unless future schema ownership review approves a move-map and alias plan. | json parse; schema validation against examples; roots validate; refactor validate | required |
| `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json` | fixture | template_only | keep | generated_sensitive | Keep under projection manifest examples unless future example fixture map is approved. | json parse; projection schema validation; roots validate | required |
| `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json` | fixture | template_only | keep | generated_sensitive | Keep under projection manifest examples unless future example fixture map is approved. | json parse; projection schema validation; roots validate | required |

## Summary

- Files classified: 4.
- Unknown after Dominium overlay: 0.
- Recommended fates: all `keep`.
- Apply allowed: false for every file.
