# Control Layers (TESTX2)

Status: binding.
Scope: optional external control systems and their engine/game exposure.

## Purpose
Control layers are optional, external systems that can gate access,
connectivity, or execution without altering authoritative simulation results.
This document defines the mechanism/policy boundary and the capability model.

## Core rules
- Control systems are optional and disabled by default.
- Engine/game provide mechanisms only; policy lives outside the engine/game.
- Control layers never alter authoritative simulation results, ordering, or
  timing. See `docs/arch/NON_INTERFERENCE.md`.
- No secrets, keys, or credentials exist in engine or game code.
- All control activity is discoverable and auditable.

## Mechanism vs policy
Mechanism (engine/game):
- Capability registry + resolution.
- Hook points that can refuse access or connectivity.
- Audit-friendly reporting APIs.

Policy (external):
- Which capabilities are enabled.
- Platform enforcement, DRM, moderation, entitlement logic.
- Any secrets or credentials.

## Capability model
Control support is expressed exclusively as capabilities.
Canonical keys are data-driven and stored in:
`data/registries/control_capabilities.registry`

Key format:
`CAPABILITY.CONTROL.<SUBSYSTEM>.<ACTION>`

Examples:
- `CAPABILITY.CONTROL.DRM.LICENSE_CHECK`
- `CAPABILITY.CONTROL.ANTICHEAT.CLIENT_PROBE`
- `CAPABILITY.CONTROL.ANTICHEAT.SERVER_VALIDATION`
- `CAPABILITY.CONTROL.TELEMETRY.OPT_IN`
- `CAPABILITY.CONTROL.PLATFORM.ENTITLEMENT`

Rules:
- Registry IDs are stable and deterministic.
- String lookup is load-time only.
- Runtime checks use numeric IDs.
- Unavailable capabilities are refused loudly.

## Placement constraints
Permitted:
- Client: optional instrumentation, integrity checks.
- Server: authoritative validation only.
- Launcher: DRM, entitlement, update control.
- Setup: activation/binding.
- Cloud/backend/platform services.

Forbidden:
- Engine authoritative logic.
- Game authoritative logic.
- Content formats, save formats, replay formats.

## Discoverability
Every product exposes:
- `--build-info` listing enabled control capabilities.
- `--status` reporting active control layers.
- Logs that record control decisions.

## Related canon
- `docs/arch/NON_INTERFERENCE.md`
- `docs/arch/THREAT_MODEL.md`
- `docs/arch/AUDITABILITY_AND_DISCLOSURE.md`
- `docs/arch/INVARIANTS.md`
