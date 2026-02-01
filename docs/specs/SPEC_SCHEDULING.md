Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_SCHEDULING — Temporal Scheduling and Recurrence

Status: draft
Version: 1

## Purpose
Define canonical scheduling and recurrence rules. Scheduling is ACT-anchored and
deterministic; calendars are renderers only.

This spec is documentation-only. It introduces no runtime logic.

## Event storage (mandatory)
Events store:
- ACT timestamp or ACT-anchored recurrence
- TimeStandard ID (for civil rendering only)

No stored formatted dates. No leap seconds.

ASCII diagram:

  ACT -> Recurrence Rule -> Schedule -> Event Execution

## Recurrence modes
1) Physical: every N seconds (ACT)
2) Civil: e.g., "every Monday at 09:00 in HPC-E"
3) Astronomical: e.g., "at sunrise"

Intercalary inclusion/exclusion must be explicit.

## Determinism rules
- Recurrence expansion is deterministic.
- Civil recurrence is rendered over ACT via the selected TimeStandard.
- Astronomical recurrence uses physical computation, not calendar shortcuts.

## Examples
Positive:
- "Every 86400 ACT seconds" uses physical recurrence.
- "Every Monday at 09:00 in HPC-E" uses civil recurrence with explicit standard.

Negative (forbidden):
- Storing "2025-01-01 09:00" as authoritative time.
- Using leap seconds to adjust schedules.

## References
- docs/specs/SPEC_STANDARDS_AND_RENDERERS.md
- docs/specs/SPEC_TIME_CORE.md
- docs/specs/SPEC_TIME_STANDARDS.md
- docs/specs/SPEC_CALENDARS.md
- docs/specs/SPEC_INFORMATION_MODEL.md
- docs/specs/SPEC_EFFECT_FIELDS.md

## Test and validation requirements (spec-only)
- ACT monotonicity tests
- Calendar reversibility tests for civil recurrence
- Sunrise spawn determinism tests
- Leap second exclusion tests