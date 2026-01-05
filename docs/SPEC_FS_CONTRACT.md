# Filesystem Resolution Contract (Launcher-Owned)

This spec defines how the game resolves filesystem paths when launched by a
launcher. The launcher owns all physical roots and the game only consumes
logical references.

## 1. Prohibitions
- `launcher_handshake.tlv` MUST NOT contain absolute filesystem paths.
- The game MUST NOT guess or scan for roots in launcher mode.
- Any path passed to the engine MUST be relative to a launcher-defined root
  and reproducible.

## 2. Allowed roots (environment-owned)
The launcher provides the physical layout via environment variables:
- `DOMINIUM_RUN_ROOT` (preferred): ephemeral per run; authoritative for logs,
  saves, replays, cache, and refusal output. The engine MUST NOT traverse
  above this root.
- `DOMINIUM_HOME` (allowed): logical root for instances and content in the
  launcher contract layout (`instances/<instance_id>`, `repo/`, etc).
- When both are set, `DOMINIUM_RUN_ROOT` is authoritative for writable outputs.

## 3. Allowed path forms
Handshake/config paths MUST be one of:
- Tagged logical refs (`PATH_REF`) with relative paths only.
- Relative paths interpreted relative to `DOMINIUM_RUN_ROOT` or
  `DOMINIUM_HOME` as defined by the field context.

`PATH_REF` schema:
- `base`: `RUN_ROOT` or `HOME`.
- `rel`: relative path (no absolute, no "..", no drive/UNC prefix).

## 4. Resolution precedence
- Writable outputs: require `DOMINIUM_RUN_ROOT`. If missing, refuse unless
  `--dev-allow-ad-hoc-paths=1` is explicitly enabled.
- Instance reads: prefer `DOMINIUM_HOME/instances/<instance_id>`.
- If `DOMINIUM_HOME` is absent, a `PATH_REF` anchored at `RUN_ROOT` MAY provide
  a read-only instance view.
- All paths are strictly normalized and must remain under the selected base
  root after normalization.

## 5. Refusal codes (stable)
These codes are stable and intended for telemetry/audit:
- `FS_REFUSAL_MISSING_RUN_ROOT` (1001)
- `FS_REFUSAL_MISSING_HOME_ROOT` (1002)
- `FS_REFUSAL_INVALID_RUN_ROOT` (1003)
- `FS_REFUSAL_INVALID_HOME_ROOT` (1004)
- `FS_REFUSAL_ABSOLUTE_PATH` (1101)
- `FS_REFUSAL_TRAVERSAL` (1102)
- `FS_REFUSAL_NORMALIZATION` (1103)
- `FS_REFUSAL_NON_CANONICAL` (1104)
- `FS_REFUSAL_OUTSIDE_ROOT` (1105)

## 6. Normalization rules
- Normalize separators to '/'.
- Collapse redundant separators.
- Reject any ".." segment.
- Reject absolute inputs (including drive-qualified and UNC paths).
- Reject non-canonical paths that would normalize to a different string.

## Related specs
- `docs/SPEC_LAUNCH_HANDSHAKE_GAME.md`
- `docs/SPEC_UNIVERSE_BUNDLE.md`
- `docs/SPEC_GAME_PRODUCT.md`
