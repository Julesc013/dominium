# RENDER_BACKEND_LIFECYCLE (FINAL0)

Status: draft  
Version: 1

## Purpose
Define the lifecycle of renderer backends and their deprecation rules.

## Lifecycle stages
- **Active**: supported and tested in CI.
- **Deprecated**: supported for compatibility, no new features.
- **Retired**: removed only after documented deprecation window.

## Deprecation rules
- Deprecation requires:
  - explicit notice in this document
  - replacement path
  - minimum support window
- Removal requires updating:
  - this lifecycle document
  - compatibility promises
  - CI enforcement matrix (FINAL-RENDER-001)

## Prohibitions
- Removing a backend without documenting lifecycle impact.
- Silent renderer capability changes.
