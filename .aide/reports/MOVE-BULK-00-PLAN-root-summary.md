# MOVE-BULK-00-PLAN Root Summary

| Root | Tracked Files | Batch | Planned Effect | Risk |
| --- | ---: | --- | --- | --- |
| `core/` | 16 | F | retire if empty after runtime/source migration | high |
| `control/` | 21 | F | retire if empty after runtime/source migration | high |
| `data/` | 1279 | A/C | narrow after Batch A; retire if empty after Batch C | high |
| `packs/` | 256 | C | retire if empty after identity-safe migration | high |
| `profiles/` | 1 | C | retire if empty | high |
| `bundles/` | 3 | C | retire if empty | high |
| `compat/` | 17 | D | retire if empty after contract/tool split | high |
| `lib/` | 22 | G | retire if empty after Python library migration | high |
| `libs/` | 86 | G | preserve until CMake/ABI blocker resolves | protected |
| `locks/` | 1 | D | retire if empty | high |
| `repo/` | 11 | D | retire if empty | high |
| `safety/` | 2 | D | retire if empty | high |
| `security/` | 4 | D | retire if empty | high |
| `specs/` | 9 | D | retire if empty after contract/spec review | protected |
| `updates/` | 6 | D | retire if empty | high |
| `meta/` | 26 | E | narrow after validator namespace migration | high |
| `governance/` | 2 | E | preserve until tool/repo owner gate | high |
| `performance/` | 3 | E | preserve until performance/tool owner gate | protected |
| `validation/` | 2 | E | retire if empty after shim migration | high |
| `modding/` | 2 | B | retire if empty after semantic owner review | high |
| `models/` | 2 | B | retire if empty after semantic owner review | high |
| `templates/` | 2 | B | retire if empty | medium |
| `net/` | 17 | F | retire if empty after runtime/protocol migration | high |
| `ide/` | 0 | retired | already retired | retired |

Total tracked files under remaining bad roots: 1,790.
