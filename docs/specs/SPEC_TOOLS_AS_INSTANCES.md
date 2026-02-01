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
# Tools as Instances

Tools are first-class launch targets. They run inside instances with the same
handshake, identity, and path contracts as the game.

## 1. Launch contract
- Tools are launched by the launcher and receive `launcher_handshake.tlv`.
- `DOMINIUM_RUN_ROOT` and `DOMINIUM_HOME` define physical roots.
- The handshake MUST NOT contain absolute filesystem paths.
- Tools MUST reject missing `DOMINIUM_RUN_ROOT` when in launcher mode.

## 2. Identity validation
- Tools MUST parse and validate the handshake before any instance access.
- Required handshake fields:
  - `instance_id`
  - `run_id`
  - `sim_caps`
- Identity digest rules match `docs/specs/SPEC_LAUNCH_HANDSHAKE_GAME.md`.
- On mismatch, tools MUST refuse and emit a refusal report under `RUN_ROOT`.

## 3. Modes
- Tools run in one of two modes:
  - `read-only` (default)
  - `edit` (explicit flag; audited)
- Edit mode MUST be declared by the tool and recorded in outputs/audit logs.
- Tools MUST NOT mutate sim-affecting state outside explicit edit mode.

## 4. Path rules
- Tools MUST use `DOMINIUM_RUN_ROOT` / `DOMINIUM_HOME` only.
- All input/output paths are relative and resolved via the launcher contract.
- Absolute paths and traversal (`..`) are forbidden.

## 5. Refusals and auditing
- Refusals are first-class:
  - emit `refusal.tlv` or structured refusal output under `RUN_ROOT`.
  - include refusal code + instance/run identity when available.
- Tools MUST log any edit operations with deterministic, structured output.

## Related specs
- `docs/specs/SPEC_LAUNCH_HANDSHAKE_GAME.md`
- `docs/specs/SPEC_FS_CONTRACT.md`
- `docs/specs/SPEC_TOOL_IO.md`
- `docs/specs/SPEC_UNIVERSE_BUNDLE.md`