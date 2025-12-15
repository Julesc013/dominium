# Dominium — Code Style and Naming Rules

This document defines repository-wide style and naming conventions. Determinism
requirements are specified in `docs/SPEC_DETERMINISM.md` and enforced by
`docs/DETERMINISM_REGRESSION_RULES.md`.

## Language levels (build-enforced)
- C code that participates in deterministic simulation is C90 (`CMAKE_C_STANDARD 90`).
- C++ code in the product layer is C++98 (`CMAKE_CXX_STANDARD 98`).

## Prefixes (canonical)
Use existing prefixes consistently:
- `d_*`: Domino subsystem APIs and deterministic domain code (world/res/env/build/trans/struct/decor/job/net/etc.).
- `dg_*`: deterministic generic primitives and authoring/compile pipelines (pose/quant, graph toolkit, SIM framework, TRANS/STRUCT/DECOR models).
- `dom_*`: stable product-facing Domino APIs (`dom_core`, `dom_pkg`, `dom_sim`) and Dominium product code (`dom_game_*`, `dom_launcher_*`, `dom_setup_*`).
- `dsys_*`: platform/system abstraction (OS/window/events/files/time/processes).

Do not introduce new prefixes without an explicit spec update.

## File placement and naming
- Public headers live under `include/domino/**` and `include/dominium/**`.
- Implementations live under `source/domino/**` and `source/dominium/**`.
- Prefer `d_*.{c,h}` / `dg_*.{c,h}` for new Domino C code; legacy single-token
  names (e.g. `dworld.c`) are allowed only where already established.
- Tests live under `source/tests/` and `tests/`. Prefer descriptive `*_test.c`
  names that match the subsystem under test.

## Formatting
- 4 spaces, no tabs.
- No trailing whitespace.
- Keep lines ≤ 100 characters where practical.
- Match the local file/directory style for brace placement and whitespace
  (avoid mechanical reformatting in unrelated diffs).

## Error handling
- Deterministic core code returns explicit status codes; avoid `abort()`/`exit()`
  and unbounded logging in deterministic paths.
- UI/tools/platform layers may report errors to stderr/stdout; they must not use
  IO or wall-clock time as an input to deterministic simulation decisions.

## Header rules
- Public headers must be self-contained and include only what they need.
- Do not include private implementation headers from `source/**` across module
  boundaries; use `include/**` APIs.
