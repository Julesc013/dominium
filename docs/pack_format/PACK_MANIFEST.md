Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# UPS Pack Manifest Format

This document defines the canonical UPS pack manifest format. It MUST be read
alongside `schema/pack_manifest.schema` and `docs/content/UPS_OVERVIEW.md`.

Runtime manifests are stored as `pack.toml`. Tooling may use
`pack_manifest.json` with a direct schema mapping; conversion must preserve
unknown fields.

## Format

- Manifest is plain text: one `key = value` pair per line.
- Order is not significant.
- Unknown keys MUST be preserved by tooling, even if ignored at runtime.
- The loader chooses the file location; the format does not hardcode paths.

## Required Keys

- `pack_id` (string)
  - Reverse-DNS identifier (e.g., `com.example.pack.base`).
  - ASCII letters, digits, dots, dashes, and underscores only.
- `pack_version` (semver)
  - `major.minor.patch` required.
- `pack_format_version` (integer)
  - Format version for manifest structure.
- `requires_engine` (semver range)
  - Minimum engine version required to load the pack.

## Optional Keys

- `required_protocols` (list)
  - Comma-separated `protocol_id:version` entries.
  - Example: `required_protocols = core.save:2, core.replay:1`
- `provides` (list)
  - Comma-separated capability identifiers.
  - Example: `provides = caps.sim, caps.ui.text`
- `depends` (list)
  - Comma-separated capability identifiers required by this pack.
- `optional` (bool)
  - `true` or `false`.

## Rules

- Manifests MUST be loadable without reading pack contents.
- Capabilities are resolved by identifier only; file paths are never used.
- Precedence is supplied externally (loader policy); it is not encoded here.
- Unknown fields MUST NOT invalidate the manifest.

## Non-Semantics

- This manifest does NOT define behavior, rules, or default content.
- It does NOT grant authority or bypass capability checks.