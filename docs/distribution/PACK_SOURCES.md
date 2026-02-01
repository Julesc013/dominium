Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Pack Sources (OPS0)

Status: binding.
Scope: ordered pack sources, trust tiers, and offline-first resolution.

## Canonical schema

Pack source definitions are described by:

- `schema/pack.sources.schema`

## Source types

- local
- lan
- removable
- http
- https

## Rules

- Launcher/setup resolve packs via ordered sources.
- Offline-first must be supported.
- No hardcoded URLs or implicit sources.
- Sources must declare trust tiers and allowed capabilities.

## Trust tiers

- official
- community
- local
- experimental

## See also

- `docs/distribution/LAUNCHER_SETUP_CONTRACT.md`
- `docs/architecture/INSTALL_MODEL.md`