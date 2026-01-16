--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- None. Game consumes engine primitives where applicable.

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
# SPEC_DGFX_IR_VERSIONING — DGFX IR Stream and Versioning

This spec defines the versioned DGFX IR stream contract used for backend
conformance tests and trace capture. The DGFX IR is derived-only and must not
affect authoritative simulation.

## 1. Scope
- DGFX IR is a **derived** render command stream.
- Backends must not mutate sim state based on IR ordering or content.
- Determinism applies to IR ordering, acceptance/rejection, and trace output.

## 2. Stream header
The serialized DGFX IR stream begins with a fixed header:

```
magic      u32_le  // ASCII "DGIR"
version    u32_le  // IR stream version (current: 1)
endian     u32_le  // 0x0000FFFE (little-endian marker)
cmd_count  u32_le  // number of commands following
```

## 3. Command record format
Each command record is:

```
opcode   u16_le
size     u16_le  // payload byte count
payload  [size]
```

Rules:
- Unknown `opcode` values MUST be skipped using `size`.
- `size` MUST be honored even when the backend ignores the opcode.
- Backends MUST NOT read beyond `size`.

## 4. Opcode mapping (v1)
The IR command opcode values map to `d_gfx_opcode`:
- `0` `D_GFX_OP_CLEAR`
- `1` `D_GFX_OP_SET_VIEWPORT`
- `2` `D_GFX_OP_SET_CAMERA`
- `3` `D_GFX_OP_DRAW_RECT`
- `4` `D_GFX_OP_DRAW_TEXT`

## 5. Versioning rules
- IR stream versions are explicit and monotonic.
- A backend MAY accept a lower version if it implements all required opcodes.
- A backend MUST reject unknown future versions unless explicitly declared
  compatible by capability flags.

## 6. Capability declarations
- Backends MUST declare which IR opcodes they accept.
- Declared capabilities MUST match observed acceptance in trace capture.
- Missing capability declarations MUST result in deterministic rejections.

## 7. Related specs
- `docs/SPEC_BACKEND_CONFORMANCE.md`
- `docs/SPEC_DETERMINISM.md`
