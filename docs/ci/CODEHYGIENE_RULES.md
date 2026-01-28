# CODEHYGIENE Rules

This document defines the enforcement rules for the code/data boundary program.

## Scope
Targets: engine/, game/, tools/, client/, server/, launcher/, setup/, libs/,
schema/, docs/, scripts/, ci/.

## Category Rules
- Category A: enums allowed, closed-world, no CUSTOM/OTHER.
- Category B: registries only (u32 ids); strings only at load/tools.
- Category C: tunables are data-driven; no magic numbers in runtime logic.
- Category D: derived data is deterministic; never authoritative.

## Magic Numbers
Policy:
- Inline numeric literals allowed only: 0, 1, -1.
- Bitmasks allowed only via named constants/macros.
- All other literals must be named constants or validated data parameters.

Allowlist markers:
- `MAGIC_NUMBER_OK: <reason>` on the same line.
- `MAGIC_NUMBER_FILE_OK: <reason>` anywhere in the file (use sparingly).

## Forbidden Enums
The following are forbidden in non-architectural enums:
- CUSTOM
- OTHER
- UNKNOWN (unless parsing-only)

Allowlist marker:
- `HYGIENE_ALLOW_UNKNOWN_ENUM: <reason>`

## Switch on Taxonomy
Switches over taxonomy ids/types are forbidden unless they are registry
dispatch tables.

Allowlist marker:
- `HYGIENE_TAXONOMY_SWITCH_OK: <reason>`

## TODO Standard
Allowed forms:
- TODO_BLOCKER(ID)
- TODO_FUTURE(ID)
- TODO_DOC(ID)

Rules:
- TODO_BLOCKER must exist in docs/ci/KNOWN_BLOCKERS.md.
- TODO_FUTURE must reference docs/architecture/FUTURE_PROOFING.md.
- TODO_DOC must reference the target doc.

## Comment Density + Doc Blocks
Targets:
- engine/ and game/ aim for ~30% comment lines.
- Each .c/.cpp/.h must have a file header doc block.

Exception marker (per-file):
- `COMMENT_DENSITY_EXCEPTION: <reason>`

## Tools
- scripts/ci/check_hygiene_scan.py
- scripts/ci/check_comment_density.py
- scripts/ci/check_todo_blockers.py
- scripts/ci/check_magic_numbers.py
- scripts/ci/check_forbidden_enums.py
- scripts/ci/check_switch_on_taxonomy.py
