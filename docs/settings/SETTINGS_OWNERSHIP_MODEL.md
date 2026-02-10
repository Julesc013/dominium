Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# Settings Ownership Model

This document defines which subsystem owns which user-facing settings surfaces.

## Ownership

- Client owns presentation and local UX preferences only:
  - mode preference (`cli|tui|gui`)
  - renderer preference
  - accessibility and input preferences
  - local replay and diagnostic overlays
  - local network browsing preferences
- Launcher owns instance/session orchestration preferences:
  - active/default instance
  - per-instance pack enablement
  - compatibility strictness
  - local launch defaults and launcher logging verbosity
- Setup owns install mutation preferences:
  - install roots
  - package/cache locations
  - trust policy and repair policy
  - rollback depth and install profile defaults
- Server owns authority/runtime policy settings:
  - tick rate
  - authority mode
  - snapshot cadence
  - server logging level
  - SRZ policy
- Tools own tool-local output and filtering preferences only.
- Engine and Game own no user-mutable settings surfaces. They consume explicit parameters.

## Forbidden Overlaps

- Client MUST NOT mutate install roots, package stores, trust policy, or rollback state.
- Client MUST NOT directly modify pack enablement or lockfiles.
- Launcher MUST NOT write simulation or authority state.
- Setup MUST NOT expose gameplay/session behavior controls.
- Tools MUST NOT mutate runtime installs by default.
- Engine/Game MUST NOT read end-user config files directly.

## Boundary Rule

When a setting belongs to another subsystem, the caller must use command-level orchestration
with deterministic refusal codes instead of direct mutation.

