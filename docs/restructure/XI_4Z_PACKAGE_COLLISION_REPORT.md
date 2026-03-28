Status: DERIVED
Last Reviewed: 2026-03-28
Supersedes: docs/restructure/XI_4Z_TARGET_NORMALIZATION_REPORT.md
Superseded By: none
Stability: provisional
Future Series: XI-5
Replacement Target: XI-5a bounded execution against v3 approved lock

# XI-4Z Package Collision Report

## Outcome

- Selected option preserved: `C`
- Collision packages fixed: `2`
- Collision rows rebound: `16`
- No source files moved during this fix.

## Fixed Packages

| Package | Row Count | Old Prefix | New Prefix | Domain | Module |
| --- | --- | --- | --- | --- | --- |
| `platform` | `10` | `src/platform/` | `engine/platform/` | `engine` | `engine.platform` |
| `time` | `6` | `src/time/` | `engine/time/` | `engine` | `engine.time` |

## Representative Rows

| Source | Old Target | New Target |
| --- | --- | --- |
| `src/platform/__init__.py` | `platform/__init__.py` | `engine/platform/__init__.py` |
| `src/platform/_canonical.py` | `platform/_canonical.py` | `engine/platform/_canonical.py` |
| `src/platform/platform_audio.py` | `platform/platform_audio.py` | `engine/platform/platform_audio.py` |
| `src/platform/platform_caps_probe.py` | `platform/platform_caps_probe.py` | `engine/platform/platform_caps_probe.py` |
| `src/platform/platform_gfx.py` | `platform/platform_gfx.py` | `engine/platform/platform_gfx.py` |
| `src/platform/platform_input.py` | `platform/platform_input.py` | `engine/platform/platform_input.py` |
| `src/platform/platform_input_routing.py` | `platform/platform_input_routing.py` | `engine/platform/platform_input_routing.py` |
| `src/platform/platform_probe.py` | `platform/platform_probe.py` | `engine/platform/platform_probe.py` |
| `src/platform/platform_window.py` | `platform/platform_window.py` | `engine/platform/platform_window.py` |
| `src/platform/target_matrix.py` | `platform/target_matrix.py` | `engine/platform/target_matrix.py` |
| `src/time/__init__.py` | `time/__init__.py` | `engine/time/__init__.py` |
| `src/time/epoch_anchor_engine.py` | `time/epoch_anchor_engine.py` | `engine/time/epoch_anchor_engine.py` |
| `src/time/tick_t.py` | `time/tick_t.py` | `engine/time/tick_t.py` |
| `src/time/time_anchor_scope.py` | `time/time_anchor_scope.py` | `engine/time/time_anchor_scope.py` |
| `src/time/time_engine.py` | `time/time_engine.py` | `engine/time/time_engine.py` |
| `src/time/time_mapping_engine.py` | `time/time_mapping_engine.py` | `engine/time/time_mapping_engine.py` |
