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
# SPEC: ABI Templates (Versioned POD VTables)

This document defines the reusable ABI template used for cross-module
interfaces (DLLs/plugins/backends).

## 1. C ABI only

All module boundaries use **C ABI**:

- No C++ name mangling across boundaries.
- No exceptions, RTTI, or STL types across boundaries.
- ABI-visible data is POD-only (plain structs, integers, pointers).

## 2. Versioned, size-stamped structs

Every ABI-visible struct and vtable begins with:

```
{ u32 abi_version; u32 struct_size; }
```

Rules:

- `abi_version` identifies the **layout + semantics** contract for that struct.
- `struct_size` allows forward/backward compatibility by permitting older code
  to pass smaller structs and newer code to detect missing fields.

Baseline helpers live in `include/domino/abi.h`.

## 3. Function tables (no inline ABI semantics)

All callable behavior across ABI boundaries is exposed via **function tables**
(vtables). Inline helpers may exist for ergonomics but must not be required to
preserve ABI semantics.

## 4. Interface discovery (query_interface)

Facades expose a `query_interface` function pointer with the canonical
signature:

```
dom_abi_result (*query_interface)(dom_iid iid, void** out_iface);
```

Where:

- `iid` is a `u32` constant identifying an interface.
- `out_iface` receives a pointer to the requested interface vtable/struct on
  success.

## 5. Ownership + handles

- Prefer opaque handles (`struct foo; typedef struct foo* foo_handle;`) to raw
  pointers when lifetime/ownership is non-trivial.
- Do not pass C++ object pointers across boundaries.
- If a platform-native handle must cross the boundary, it must be explicitly
  labeled as a **native handle** and exposed only via an optional extension.

