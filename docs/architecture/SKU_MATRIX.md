# SKU Matrix (SKU0)

Status: binding.
Scope: supported SKUs and their capability baselines.

## SKU to baseline mapping

| SKU | Baseline | Notes |
| --- | --- | --- |
| legacy_core | BASELINE_LEGACY_CORE | C89/C++98; zero-pack executable required |
| mainline_core | BASELINE_MAINLINE_CORE | Future core baseline |
| modern_ui | BASELINE_MODERN_UI | UI-focused capabilities |
| server_min | BASELINE_SERVER_MIN | Minimal server runtime |

## Rules
- SKUs declare baselines, not engine versions.
- Old binaries may load new saves in degraded/frozen mode.
- Refusal is required when missing core capabilities.

## See also
- `docs/architecture/CAPABILITY_BASELINES.md`
- `docs/architecture/LOCKFILES.md`
