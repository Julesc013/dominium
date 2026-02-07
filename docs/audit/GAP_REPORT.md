Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Gap Report

This report lists blocked, deferred, and immediate next actions discovered
during the normalization/inventory pass.

## Blocked items (require scoped prompts)

1) Pack validation failures (content references missing)
   - Source: `docs/audit/PACK_AUDIT.txt`
   - Examples:
     - `org.dominium.core.assemblies.extended` missing part/interface refs
     - `org.dominium.core.parts.basic` missing material/interface refs
     - `org.dominium.examples.*` dependency mismatch fields
   - Current count: 14 failing packs (see report summary)
   - Requires: content/schema pack fixes with explicit migration or reference additions

2) Non-legacy runtime stubs flagged by marker scan
   - Source: `docs/audit/MARKER_SCAN.txt`
   - Examples:
     - `engine/modules/system/*_stub.c` (platform/system stubs)
     - `engine/render/*_stub.*` (render backend placeholders)
     - `game/rules/*_stub.cpp` (rules stubs)
     - `launcher/*_stub.*`, `setup/*_stub.*`, `libs/ui_backends/*_stub.*`
   - Requires: classification per stub (acceptable/permanent vs. explicit refusal), or scoped implementation prompts

2) Appcore scaffolding TODOs
   - Source: `docs/audit/MARKER_SCAN.txt` (libs/appcore/* TODO)
   - Requires: APP-CANON scoped implementation prompts

## Deferred items (non-blocking but tracked)

- UI backend placeholders (GTK/macOS) remain unimplemented.
- Launcher/setup GUI/TUI placeholders remain (non-authoritative scaffolding).
- Legacy stubs in `legacy/` remain quarantined.
- "stage_root" references appear only in setup test scaffolding (staging paths), not runtime progression.

## Immediate next actions (safe, local)

- Formalize pack reference resolution fixes for the 14 failing packs.
- Convert raw TODOs to standardized TODO_* markers per `docs/ci/CODEHYGIENE_RULES.md`.
- Generate a specific prompt for appcore scaffolding completion.
- Classify non-legacy runtime stubs and decide explicit refusal vs. implementation scope.
