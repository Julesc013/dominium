# Ecosystem Integration (Handshake, Tools, Selection Summary)

Doc Version: 1

This document specifies the stable integration surfaces for the launcher-as-control-plane model:

- `handshake.tlv` (launcher → engine/tool)
- `tools_registry.tlv` (tools-as-instances registry)
- `selection_summary.tlv` (unified selection visibility)
- how these relate to `audit_ref.tlv`

All formats are **versioned TLV**, **canonical-encoded**, and **skip-unknown** on read.

## 1) Run Artifacts (Where These Files Live)

Every launch attempt (game or tool), including refusals, creates:

`<state_root>/instances/<instance_id>/logs/runs/<run_dir_id>/`

Where:
- `run_dir_id` is the 16-hex-digit `run_id` without the `0x` prefix.

Files produced (best-effort, stable names):
- `handshake.tlv`
- `launch_config.tlv`
- `selection_summary.tlv`
- `exit_status.tlv`
- `audit_ref.tlv`
- `stdout.txt` / `stderr.txt` when capture is supported; otherwise the files may be absent and `exit_status.tlv` must state capture support explicitly.

The exact directory layout invariants are defined in `docs/specs/launcher/ARCHITECTURE.md`.

## 2) Handshake (`handshake.tlv`) Schema v1

Schema version: `LAUNCHER_HANDSHAKE_TLV_VERSION = 1`

Purpose:
- Provides the engine/tool with a deterministic, self-contained snapshot of what the launcher resolved for a run.
- Allows the engine/tool to validate that the resolved content matches the effective instance manifest and artifact store.

### 2.1 Root Fields (Required Unless Stated Optional)

See `source/dominium/launcher/core/include/launcher_handshake.h` for tag ids and canonical encoding rules.

Required fields:
- `run_id` (u64): unique run id; also identifies the run directory.
- `instance_id` (string): selected instance id.
- `instance_manifest_hash` (bytes): hash of the effective instance manifest used for this run (SHA-256 recommended).
- `launcher_profile_id` (string): active launcher profile id.
- `determinism_profile_id` (string): active determinism profile id.
- `selected_platform_backend` (string, repeated): platform backend ids.
- `selected_renderer_backend` (string, repeated): renderer backend ids (may be empty for `--gfx=null`).
- `selected_ui_backend_id` (string): UI backend id (`native`, `dgfx`, `null`, etc).
- `pin_engine_build_id` (string): pinned engine build id.
- `pin_game_build_id` (string): pinned game build id.
- `resolved_pack_entry` (container, repeated; order preserved): resolved pack list for this run.
- `timestamp_monotonic_us` (u64): monotonic timestamp for the run.

Optional fields:
- `timestamp_wall_us` (u64): when available.

### 2.2 Resolved Pack Entries

Each `resolved_pack_entry` contains:
- `pack_id` (string)
- `version` (string)
- `hash_bytes` (bytes)
- `enabled` (u32; 0/1): effective enable after layering and safe mode.
- `sim_flag` (string, repeated): deterministic sim-affecting flags derived from the pack/manifest.
- `safe_mode_flag` (string, repeated): safe-mode diagnostics flags (stable strings).
- `offline_mode_flag` (u32; 0/1): snapshot of offline mode for the run.

Ordering:
- The launcher preserves deterministic resolver order for enabled entries.
- When safe mode disables pack-like entries that would otherwise be enabled, disabled entries may be appended for diagnostics; their order must be stable (lexicographic by `pack_id`).

### 2.3 Refusal Codes (Stable, Enumerated)

Handshake validation uses stable refusal codes (subset mirrored engine-side):

- `0` `LAUNCHER_HANDSHAKE_REFUSAL_OK`
- `1` `LAUNCHER_HANDSHAKE_REFUSAL_MISSING_REQUIRED_FIELDS`
- `2` `LAUNCHER_HANDSHAKE_REFUSAL_MANIFEST_HASH_MISMATCH`
- `3` `LAUNCHER_HANDSHAKE_REFUSAL_MISSING_SIM_AFFECTING_PACK_DECLARATIONS`
- `4` `LAUNCHER_HANDSHAKE_REFUSAL_PACK_HASH_MISMATCH`
- `5` `LAUNCHER_HANDSHAKE_REFUSAL_PRELAUNCH_VALIDATION_FAILED`

When a run is refused:
- `exit_status.tlv` must record `termination_type=LAUNCHER_TERM_REFUSED`.
- The run audit must include `outcome=refusal`, `refusal_code=<code>`, and `refusal_detail=<text>`.

For code `5`, `refusal_detail` is a stable, parseable `;`-separated string beginning with:
- `prelaunch_validation_failed`

And may include:
- `code=<failure_code>`
- `detail=<failure_detail>`

## 3) Tools Registry (`tools_registry.tlv`) v1

Schema version: `LAUNCHER_TOOLS_REGISTRY_TLV_VERSION = 1`

Location (load order):
- `<state_root>/tools_registry.tlv` (preferred)
- `<state_root>/data/tools_registry.tlv` (fallback)

Purpose:
- Defines tools as first-class launch targets that run under an instance’s resolved content context.
- Enables deterministic enumeration of available tools for a given instance.

Tool entry fields (see `source/dominium/launcher/core/include/launcher_tools_registry.h`):
- `tool_id` (string): stable id used in `--target=tool:<tool_id>`.
- `display_name` (string)
- `description` (string)
- `executable_artifact_hash` (bytes): artifact store identity for the tool executable.
- `required_pack` (string, repeated): packs that must be enabled for the tool to be considered available.
- `optional_pack` (string, repeated): packs the tool can use when present/enabled.
- `capability_requirement` (string, repeated): declarative requirements (used for validation/refusal; no OS leakage).
- `ui_entrypoint_metadata` (container, optional): placeholders only (`label`, `icon_placeholder`).

Determinism:
- Enumeration for an instance is sorted lexicographically by `tool_id`.

## 4) Tools-as-Instances (Operational Model)

Tools are launched as targets under a selected instance:

- You select an `instance_id`.
- You launch `--target=tool:<tool_id>`.
- The launcher resolves packs deterministically, applies overlays/overrides, and produces the same run artifacts as a game launch:
  - `handshake.tlv`
  - `selection_summary.tlv`
  - `exit_status.tlv`
  - `audit_ref.tlv`

This keeps tooling inside the same determinism boundaries as gameplay: tools are consumers of the instance ecosystem, not separate ad-hoc processes.

## 5) Selection Summary (`selection_summary.tlv`) v1

Schema version: `LAUNCHER_SELECTION_SUMMARY_TLV_VERSION = 1`

Purpose:
- Provides a stable snapshot of “what was selected, and why” for UI/CLI/diagnostics.
- Serves as the unified selection visibility surface and is derived from the same selected-and-why inputs used by the run audit.

Key fields (see `source/dominium/launcher/core/include/launcher_selection_summary.h`):
- `run_id` (u64)
- `instance_id` (string)
- `launcher_profile_id` (string)
- `determinism_profile_id` (string)
- `offline_mode` (u32; 0/1)
- `safe_mode` (u32; 0/1)
- `manifest_hash64` (u64) and `manifest_hash_bytes` (bytes; SHA-256 recommended)
- `backends.ui.id` + `backends.ui.why`
- `backends.platform[i].id` + `backends.platform[i].why`
- `backends.renderer[i].id` + `backends.renderer[i].why` (count may be `0`)
- `packs.resolved.count` + `packs.resolved.order` (comma-separated pack ids; deterministic)

Stable text rendering:
- `launcher_selection_summary_to_text` emits a deterministic, line-oriented dump.
- `launcher_selection_summary_to_compact_line` emits a stable one-line summary for status bars.

## 6) Relationship to Audit (`audit_ref.tlv`)

Per-run audit (`audit_ref.tlv`) is the authoritative record for a launch attempt.

Invariants:
- The audit must include stable reasons for “no silent paths” (operation type, instance id, outcome or refusal).
- The audit records `handshake_path=...` and `selection_summary_path=...` as reason keys.
- The audit may embed `selection_summary.tlv` bytes as an attached TLV sub-chunk; when present, the embedded bytes must match the `selection_summary.tlv` file for that run.

See:
- `docs/specs/launcher/ARCHITECTURE.md`
- `docs/launcher/CLI.md`

