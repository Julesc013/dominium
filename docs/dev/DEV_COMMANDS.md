Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# Dev Commands

Developer wrappers are convenience surfaces only. RepoX/TestX/CI must continue using canonical adapter and tool policies.

## Tool Wrappers

Wrapper entrypoint:

- `python scripts/dev/dev.py`
- `scripts/dev/dev.cmd` (Windows convenience)

Supported commands:

- `python scripts/dev/dev.py tools list`
- `python scripts/dev/dev.py tools doctor`
- `python scripts/dev/dev.py tools ui_bind -- --repo-root . --check`

Behavior:

- wrappers call canonical tools by name only
- wrappers apply canonical tool PATH via `scripts/dev/env_tools.py`
- wrappers do not bypass RepoX/TestX invariants

## Notes

- These wrappers are optional quality-of-life helpers.
- They are not used as authority paths by RepoX/TestX.
