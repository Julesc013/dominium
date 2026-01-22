# Distribution Profiles (TESTX2)

Status: binding.
Scope: declarative control capability bundles for distribution.

## Definition
A distribution profile is a declarative configuration that specifies:
- Enabled control capabilities.
- Required platforms.
- Offline allowance.
- Telemetry allowance.
- Mod restrictions.

Profiles never change authoritative simulation behavior.

## Rules
- Profiles are data-driven and immutable once released.
- Profiles cannot bypass TESTX invariants.
- Profiles cannot enable hidden enforcement paths.
- Profiles do not contain secrets.

## Example profiles
community_offline:
- control capabilities: none
- offline: allowed
- telemetry: disabled
- mods: allowed

commercial_online:
- control capabilities: DRM license check, platform entitlement
- offline: limited
- telemetry: opt-in only
- mods: restricted

academic_research:
- control capabilities: none
- offline: allowed
- telemetry: disabled
- mods: allowed (audited)

enterprise_simulation:
- control capabilities: connectivity gate, entitlement
- offline: controlled
- telemetry: allowed (declared)
- mods: restricted

restricted_jurisdiction_X:
- control capabilities: moderation hook, entitlement
- offline: controlled
- telemetry: opt-in
- mods: restricted

## Integration points
- Launcher and setup interpret profiles.
- Engine/game expose hooks only; policy stays external.
