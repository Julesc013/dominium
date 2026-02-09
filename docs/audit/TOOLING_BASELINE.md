Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# Tooling Baseline

## Scope

This baseline captures canonical tool discoverability guarantees for RepoX, TestX, CI, and developer shells.

## Enforced Invariants

- `INV-TOOL-NAME-ONLY`
- `INV-TOOLS-PATH-SET`
- `INV-TOOL-UNRESOLVABLE`

## Required Adapter

- `scripts/dev/env_tools.py`
- `scripts/dev/env_tools.cmd`
- `scripts/dev/env_tools.ps1`
- `scripts/dev/env_tools.sh`

## TestX Regression Coverage

- `test_tool_discoverability` verifies canonical tools resolve by name after canonical PATH setup.
- `test_tool_discoverability_missing_path` verifies RepoX fails loudly when canonical tools PATH is absent.

## Diagnostics Contract

CI prints resolved canonical tool paths after adapter initialization and fails if any canonical tool is missing from PATH.
