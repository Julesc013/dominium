Status: DERIVED
Last Reviewed: 2026-02-12
Supersedes: none
Superseded By: none

# Mode Governance Policy

## Scope
This policy governs mode-like behavior through profile data:
- `LawProfile`
- `ExperienceProfile`
- `ParameterBundle`
- `BundleProfile`

No subsystem may introduce runtime mode forks outside this profile model.

## Modes-as-Profiles Invariants
- Every `ExperienceProfile` must reference a valid `LawProfile`.
- Every `ExperienceProfile` must declare a valid default `ParameterBundle`.
- Mode behavior is resolved from registries; mode booleans are forbidden.

## Ownership Boundaries
- Setup:
  - installs optional bundles and core runtime bundles
  - never enables per-instance content
- Launcher:
  - enables/disables bundle packs per instance
  - selects `experience_id`, `scenario_id`, and `parameter_bundle_id`
- Client:
  - presents selectors and session flow
  - enforces entitlement checks at dispatch/render
  - never mutates install/package state
- Server:
  - authoritative law enforcement in multiplayer
  - rejects client escalation attempts

## ParameterBundle Policy
- Allowed:
  - deterministic numeric tuning
  - policy flags that map to existing legal behavior
- Forbidden:
  - new mechanics via bundle keys
  - bypassing law constraints
  - implicit defaults that are not declared in data

## Entitlement Gating
- HUD, overlays, console surfaces, and freecam are entitlements.
- Command dispatch refuses when entitlement or profile selection is missing.
- Render surfaces must not bypass entitlement checks.

## Optional Default Bundles
- `bundle.core.runtime` is always required and marked non-optional.
- All additional defaults are optional bundles and can be removed safely.
- Missing optional bundles must refuse deterministically with recovery guidance.

## Adding New Experiences Safely
1. Add/extend schema and registries.
2. Bind each new experience to an explicit law profile.
3. Declare required bundles/capabilities in scenario/mission metadata.
4. Add RepoX and TestX locks for permission and determinism behavior.
5. Add AuditX checks for mode-branch and capability-bypass smell classes.
