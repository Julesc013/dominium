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
# SPEC_CALENDARS - Calendar Renderers

Status: draft
Version: 1

Calendars are derived, non-authoritative renderers from canonical time to
human-readable labels. They never mutate simulation state or causality.

ASCII diagram:

  ACT -> Frame (optional) -> Calendar Renderer -> Label

## 1. Authoritative inputs
- ACT (Atomic Continuous Time), represented by tick_index + ups.
- Optional frame selection (BST, GCT, CPT) as a renderer over ACT.

Calendars are pure renderers over ACT or a declared frame. They never advance time.

## 2. Calendar kinds
- Fixed-ratio: constant day/year lengths defined as rational seconds.
- Orbit-synced: derives days/years from body rotation/orbit period.
- Hybrid: fixed-ratio base with periodic corrections from an orbit source.

Only fixed-ratio calendars are implemented in v1; others return NOT_IMPLEMENTED.

## 3. Intercalary days
- Intercalary days exist physically.
- They are not part of weeks or months canonically.
- They use explicit tokens (e.g., Year Day, Leap Day).
- Projection into month/day is allowed only as a compatibility view.

## 4. Determinism rules
- Integer-only math; no floating-point.
- No locale, timezone, or wall-clock dependencies.
- Output is a presentation label only (not canonical state).
- Leap seconds are forbidden in ACT/BST/GCT/CPT.

## 4.1 Leap seconds (display-only)
- Leap seconds do not exist in ACT/BST/GCT/CPT.
- Allowed only as a display layer for UTC compatibility.
- Leap tables are external, versioned, and deterministic.
- Leap tables MUST NOT affect scheduling or simulation.

## 5. Required calendar renderers

### Sol Coordinated Time (SCT)
- Rendering of BST.
- Atomic days only.
- No leap seconds.
- Used for interplanetary law, trade, military, archives.

### Sol Epoch Calendar (SEC)
- 400-day year.
- 10 x 40-day months (Decan-1 .. Decan-10).
- 8-day weeks (Day-1 .. Day-8).
- No leap logic.

### Earth Perfect Calendar (HPC-E)
Structure:
- 13 months x 28 days = 364 days.
- 7-day weeks (Monday .. Sunday).
- Intercalary days appended only to February.

Month order (fixed):
1. March
2. April
3. May
4. June
5. July
6. August
7. September
8. October
9. November
10. December
11. Undecember
12. January
13. February

Intercalary:
- Year Day (every year)
- Leap Day (leap years)
- Canonical: undated
- Compatibility: Feb 29 = Year Day, Feb 30 = Leap Day

Seasons:
- Spring: March-May
- Summer: June-August
- Autumn: September-November
- Winter: December-February

### Earth historical calendars (renderers)
- Gregorian
- Julian
- Islamic
- Hebrew
- Chinese
- Persian
- Holocene
- Metric
- ISO week date
- Financial year calendars (US, UK, ISO, 4-4-5)

### Mars calendars
- Scientific: MSD, MTC, Mars Year.
- Civil: Darian, Allison-McEwen, Metric Mars.
- Perfect Mars Calendar (HAC-Mars): 24 x 28-sol months, 7-sol weeks, intercalary sols outside weeks.

### Venus calendars
- Perfect Venus Calendar (HAC-V): 225 atomic-day year, 9 x 25-day months, 5-day work cycles, explicit intercalary days.

### Mercury calendars
- Perfect Mercury Calendar (HHC): 88 atomic-day year, 8 x 11-day months, explicit correction day.

### Gas giants
- No planetary civil calendars.
- Moons have local calendars: fixed-length months and cycles, no leap logic.

### Pluto and TNOs
- Pluto HKC-Pl: 8 x 32-day.
- Other TNOs: duration/epoch only (HDTF).

### Sun
- No civil calendar.
- Carrington rotation and activity epochs only.

### Galactic and universal scale
- Galactic Epoch Calendar (GEC): Block (1,000 days), Era (100,000 days), Epoch (10,000,000 days).
- Universal Epoch Framework (UEF): Phase (~10^6 days), Age (~10^9 days), Era (~10^12 days).
- No days/weeks/months.

## 6. Output fields
Fixed-ratio output uses integer fields:
- year
- day_of_year
- hour, minute, second
- optional subsecond fields derived from tick remainder

## 7. Examples
Positive:
- ACT -> HPC-E render, Year Day appears as an intercalary token.
- SCT render used for interplanetary scheduling, no leap seconds.

Negative (forbidden):
- Storing formatted dates in authoritative state.
- Calendar math in the engine.
- Applying leap seconds to ACT or BST.

## Related specs
- docs/specs/SPEC_STANDARDS_AND_RENDERERS.md
- docs/specs/SPEC_TIME_CORE.md
- docs/specs/SPEC_TIME_FRAMES.md
- docs/specs/SPEC_TIME_STANDARDS.md
- docs/specs/SPEC_INFORMATION_MODEL.md
- docs/specs/SPEC_EFFECT_FIELDS.md
- docs/specs/SPEC_SPACETIME.md
- docs/specs/SPEC_DETERMINISM.md