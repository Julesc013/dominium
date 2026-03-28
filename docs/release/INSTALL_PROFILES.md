Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DIST/UPDATE-MODEL
Replacement Target: release-index governed install-profile selection with trust-policy and remote acquisition

# Install Profiles

## Purpose

Install profiles are deterministic selector sets resolved through the component graph. They define named bundle shapes without hardcoding file lists outside graph resolution.

## Profiles

### `install.profile.full`

- Purpose: full default portable/installable MVP surface.
- Required selectors:
  - `binary.client`
  - `binary.game`
  - `binary.launcher`
  - `binary.server`
  - `binary.setup`
  - `docs.release_notes`
  - `manifest.instance.default`
  - `manifest.release_manifest`
- Optional selectors: none.
- Default mod policy: `mod_policy.lab`
- Default overlay conflict policy: `overlay.conflict.last_wins`

### `install.profile.client`

- Purpose: client-centric install with runtime content, no dedicated server binary.
- Required selectors:
  - `binary.client`
  - `manifest.instance.default`
  - `manifest.release_manifest`
- Optional selectors:
  - `binary.launcher`
  - `binary.setup`
  - `docs.release_notes`
- Default mod policy: `mod_policy.lab`
- Default overlay conflict policy: `overlay.conflict.last_wins`

### `install.profile.server`

- Purpose: minimal authoritative runtime without rendered client binaries.
- Required selectors:
  - `binary.server`
  - `manifest.instance.default`
  - `manifest.release_manifest`
- Optional selectors:
  - `binary.launcher`
  - `binary.setup`
  - `docs.release_notes`
- Default mod policy: `mod_policy.lab`
- Default overlay conflict policy: `overlay.conflict.last_wins`

### `install.profile.tools`

- Purpose: offline verification, store management, and release tooling surface.
- Required selectors:
  - `binary.setup`
  - `manifest.release_manifest`
- Optional selectors:
  - `binary.launcher`
  - `docs.release_notes`
- Default mod policy: `mod_policy.lab`
- Default overlay conflict policy: `overlay.conflict.last_wins`

### `install.profile.sdk`

- Purpose: future SDK/documentation/tooling surface.
- Required selectors:
  - `docs.release_notes`
  - `manifest.release_manifest`
- Optional selectors:
  - `binary.setup`
- Default mod policy: `mod_policy.lab`
- Default overlay conflict policy: `overlay.conflict.last_wins`

## Resolution Rules

- Setup and launcher resolve profiles through `release/component_graph_resolver.py`.
- Required selectors are always expanded.
- Optional selectors are reported as disabled by default unless a later policy enables them.
- Provider selection remains delegated to the deterministic LIB provides resolver.

## Stability

- Profile ids are treated as frozen user-facing handles for `v0.0.0-mock`.
- Selector contents remain provisional until release indices, trust policy, and remote acquisition are formalized.
