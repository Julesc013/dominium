Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- None. Game consumes engine primitives where applicable.

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

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
# Tool I/O Contract

Tools must read and write data in a launcher-controlled, reproducible way.

## 1. Inputs
- Inputs are provided as logical references:
  - `PATH_REF` with base `RUN_ROOT` or `HOME`.
  - Relative paths resolved against the appropriate base.
- Absolute paths are forbidden.
- Tools MUST NOT scan for ad-hoc install layouts.

## 2. Output root and layout
- All tool outputs live under `DOMINIUM_RUN_ROOT`.
- Default output layout:
  - `RUN_ROOT/tools/<tool_id>/`
- Tools MAY create subdirectories under their tool output root.

## 3. Output types
- Outputs are structured and reproducible:
  - TLV, JSON, or line-oriented text.
- Tools MUST avoid embedding absolute paths in output payloads.

## 4. Universe edits
- Tools MUST NOT overwrite universe bundles in place.
- Any edits MUST produce a new bundle at a new output path.
- The original bundle is treated as read-only unless explicitly replaced by
  a new artifact.

## 5. Refusal output
- Refusal output is written under `RUN_ROOT/tools/<tool_id>/refusal.tlv`
  (or a tool-specific equivalent).
- Refusal records include:
  - refusal code
  - message text
  - instance/run identifiers when available

## Related specs
- `docs/specs/SPEC_TOOLS_AS_INSTANCES.md`
- `docs/specs/SPEC_LAUNCH_HANDSHAKE_GAME.md`
- `docs/specs/SPEC_FS_CONTRACT.md`