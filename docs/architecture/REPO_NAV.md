# Repository Navigation (NAV0)

Status: binding.
Scope: where to place schemas, core code, content, tests, and docs.

This is the fast path for contributors. It is subordinate to:
- `docs/architecture/CANONICAL_SYSTEM_MAP.md`
- `docs/architecture/ARCH_REPO_LAYOUT.md`
- `docs/architecture/DIRECTORY_STRUCTURE.md`

## Direct answers
- Where do I add schemas? Add them under `schema/` with a `schema_id`.
- Where do I add core code? Add it under `engine/` or `game/`, not products.
- Where do I add content? Add it under `data/` (packs, modpacks, profiles).
- Where do I add tests? Add them under `tests/` in the relevant domain.
- Where do I add docs? Add them under `docs/` (usually `docs/architecture/`).

## If you want X, go to Y
| If you want to add or change... | Go here first |
| --- | --- |
| engine mechanisms, determinism, ECS, execution substrate | `engine/` |
| game meaning, rules, processes, law targets | `game/` |
| client or server entrypoints and composition | `client/` or `server/` |
| orchestration, install, profiles, compatibility checks | `launcher/` or `setup/` |
| validators, editors, inspectors, audit tools | `tools/` |
| stable schemas and data shape contracts | `schema/` |
| content packs, modpacks, saves, replays, profiles | `data/` |
| cross-product contracts and shared interfaces | `libs/contracts/` |
| SDK-facing headers, samples, and docs | `sdk/` |
| policies, constitutions, and architectural contracts | `docs/architecture/` |
| contract enforcement and TESTX suites | `tests/` (use a focused subdir) |

## Placement rules that do not change lightly
- Do not add gameplay rules to `engine/`.
- Do not add engine internals to `game/`, `client/`, or `server/`.
- Do not place runtime content under `docs/`, `schema/`, or `tests/`.
- Do not add authoritative mutation paths to `tools/`, `launcher/`, or `setup/`.
- Prefer extending existing systems over creating new top-level domains.

## See also
- `docs/architecture/CODE_DATA_BOUNDARY.md`
- `docs/architecture/EXTEND_VS_CREATE.md`
- `docs/architecture/CONTRACTS_INDEX.md`
