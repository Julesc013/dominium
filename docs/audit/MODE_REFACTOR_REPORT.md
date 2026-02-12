Status: DERIVED
Last Reviewed: 2026-02-12
Supersedes: none
Superseded By: none

# Mode Refactor Report

## Implemented
- Added canonical schemas for `LawProfile`, `ExperienceProfile`, `ParameterBundle`, and `BundleProfile`.
- Added baseline registries for observer, survival, hardcore, creative, lab, and mission profile composition.
- Wired client command graph with profile selection commands:
  - `client.experience.list/select`
  - `client.scenario.list/select`
  - `client.mission.list/select`
  - `client.parameters.list/select`
  - `client.session.create_from_selection`
- Added entitlement-sensitive command surfaces for HUD, overlays, console, and freecam with deterministic refusal paths.
- Added RepoX invariants:
  - `INV-MODE-AS-PROFILES`
  - `INV-UI-ENTITLEMENT-GATING`
  - `INV-DEFAULTS-OPTIONAL`

## Usable Scaffolding
- Profile-driven selection state in `client/core/client_command_bridge.c` with law binding and default parameter resolution.
- Optional bundle declarations in `data/registries/bundle_profiles.json` with explicit `extensions.optional` policy.
- AuditX analyzers for:
  - `ModeFlagSmell`
  - `CapabilityBypassSmell`

## Deferred / Stubbed
- Deep server runtime mapping from law-profile IDs to protocol-level capability masks remains incremental.
- Mission evaluator semantics remain intentionally unchanged; enforcement is limited to profile/registry wiring.
- Full launcher/setup UX composition for bundles and per-instance profile editing remains tracked as follow-up.

## Safe Extension Path
1. Add a new law profile in `data/registries/law_profiles.json`.
2. Add matching experience profile and default parameter bundle.
3. Add scenario/mission constraints by registry IDs only.
4. Add TestX and RepoX locks before enabling in launcher defaults.
