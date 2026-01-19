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
# SPEC_TIME_STANDARDS — Time Standards and Resolution

Status: draft
Version: 1

## Purpose
Define TimeStandard objects and the resolution order for selecting them. Time
standards are data-defined renderers over ACT or frames.

This spec is documentation-only. It introduces no runtime logic.

## TimeStandard object
A TimeStandard defines:
- calendar renderer
- clock renderer
- frame preference (ACT/BST/GCT/CPT)
- intercalary policy
- locale/nameset

TimeStandards are stateless and deterministic.

## Resolution order (mandatory)
1) Explicit context (contract, document, UI override)
2) Organization standard
3) Jurisdiction standard
4) Personal preference
5) Fallback (numeric SCT/ACT)

Silent fallback is forbidden. Conflicts must be visible.

ASCII diagram:

  Explicit -> Organization -> Jurisdiction -> Personal -> Fallback

## Required standards (minimum set)
- SCT (Sol Coordinated Time)
- SEC (Sol Epoch Calendar)
- HPC-E (Earth Perfect Calendar)
- Historical Earth calendars (Gregorian, Julian, Islamic, Hebrew, Chinese, Persian,
  Holocene, Metric, ISO week, financial year calendars)
- Mars calendars (MSD, MTC, Darian, Allison-McEwen, Metric Mars, HAC-Mars)
- Venus HAC-V
- Mercury HHC
- Gas giants: moon-local calendars only
- Pluto HKC-Pl, TNO HDTF
- Galactic GEC, Universal UEF

Calendar definitions live in `docs/SPEC_CALENDARS.md`.

## Conflict handling
Conflicts are expected and must be shown. If a higher-precedence standard is
blocked by knowledge or access, the result is UNKNOWN and resolution proceeds.
Different actors may legitimately disagree on time/date; conflicts are visible.

## Examples
Positive:
- A contract requires HPC-E; UI shows conflict against local preference.
Negative (forbidden):
- Defaulting to a standard without provenance.

## References
- docs/SPEC_STANDARDS_AND_RENDERERS.md
- docs/SPEC_STANDARD_RESOLUTION.md
- docs/SPEC_CALENDARS.md
- docs/SPEC_INFORMATION_MODEL.md
- docs/SPEC_EFFECT_FIELDS.md

## Test and validation requirements (spec-only)
- Conflicting standards resolution tests
- UNKNOWN propagation tests
- Deterministic resolution tests
