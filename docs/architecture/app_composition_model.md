Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# App Composition Model

An app is a product composition. App identity is not the executable filename,
launcher option, or implementation directory.

## Descriptor

An app descriptor declares:

- `app_id`
- `product_id`
- owner, version, and stability
- supported modes such as CLI, TUI, rendered, native, or headless
- required services
- enabled modules
- default packs and profiles
- provider preferences
- required capabilities
- release profiles
- proof

Examples include `dominium.client`, `dominium.server`,
`dominium.launcher`, `dominium.setup`, and `dominium.workbench`.

## Composition

App composition combines apps, modules, packs, providers, capabilities, and
release profiles. It must reference governed IDs and must not embed private
paths. Another game on Domino should be able to compose its own apps from
registered modules, packs, and providers without adopting Dominium Workbench as
semantic authority.

## Boundary

This law does not implement App Composer, app runtime dispatch, package
mounting, release publication, or product features. It defines the descriptor
and validator surface that later implementation must obey.
