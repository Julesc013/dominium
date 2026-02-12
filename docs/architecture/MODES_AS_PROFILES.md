Status: DERIVED
Last Reviewed: 2026-02-12
Supersedes: none
Superseded By: none

# Modes As Profiles

## Model
- Runtime "mode" is data composition, not code branching:
  - `ExperienceProfile`
  - `LawProfile`
  - `ParameterBundle`
  - optional `MissionSpec` constraints
- Setup installs bundle content; Launcher enables bundle content per instance.
- Client/Server resolve profile data and enforce resulting capabilities and entitlements.

## Canonical Rules
- Hardcoded mode branches are forbidden (`if (survival)`, `if (creative)`, etc.).
- Console, HUD, overlays, and freecam are permissioned surfaces.
- UI projection must read entitlement state and command refusals; UI cannot bypass law.
- Core runtime must boot with `bundle.core.runtime` only.
- Optional content remains optional: scenarios and missions may refuse if packs are missing.

## Composition
- `LawProfile` defines:
  - capabilities granted/revoked
  - entitlements granted
  - epistemic constraints
  - allowed/forbidden intent families
  - persistence/refusal policy
- `ExperienceProfile` defines:
  - which law profile is active
  - workspace/layout and visible scenario/mission sets
  - default parameter bundle and tool visibility
- `ParameterBundle` defines deterministic tuning values only.
- `MissionSpec` may narrow legal intents and add evaluators, but does not override law.

## Enforcement Points
- Client command dispatch checks entitlements before dispatch.
- Client render/panel visibility checks entitlements before presentation.
- Server authoritatively validates negotiated law and rejects escalation attempts.
- RepoX/TestX/AuditX lock profile-driven operation and regressions.

