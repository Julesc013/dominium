Status: CANONICAL
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
# SPEC: DUI (Dominium UI) Facade + Schema

This document defines the **DUI (Dominium UI)** system: a presentation-only facade that allows the Dominium launcher to run with **native OS widgets**, a **DGFX-rendered fallback**, or **null/headless** mode without changing launcher-core behavior.

Related:
- `docs/specs/SPEC_FACADES_BACKENDS.md`
- `docs/specs/SPEC_CAPABILITY_REGISTRY.md`
- `docs/specs/SPEC_CONTAINER_TLV.md`
- `include/dui/dui_api_v1.h`
- `include/dui/dui_schema_tlv.h`

## 1. Goals and Non-Goals

Goals:
- Launcher core remains UI-agnostic (no UI toolkit headers; no UI logic in core).
- UI is selected deterministically via capability registry + profiles + `--ui=`.
- UI decisions and fallbacks are auditable.
- UI is data-driven: schema/state snapshots are TLV streams; backends render them.
- Backends degrade gracefully: refusal is explicit and reasoned.

Non-goals (explicitly deferred):
- Theming, animations, web UI.
- Pack-specific custom widgets.
- Accessibility tuning beyond basic exposure.

## 2. Facade ABI: `dui_api_v1`

The DUI facade is a **C ABI**, versioned POD vtable:
- Header: `include/dui/dui_api_v1.h`
- ABI version constant: `DUI_API_ABI_VERSION`
- Every ABI-visible struct begins with `{ abi_version, struct_size }` (`DOM_ABI_HEADER`).

Core handles (opaque):
- `dui_context`: owns backend-global state and the event queue.
- `dui_window`: owns a single top-level UI surface (native window, DGFX canvas, or null).

Required operations:
- Context lifecycle: `create_context`, `destroy_context`
- Window lifecycle: `create_window`, `destroy_window`
- Schema/state ingestion: `set_schema_tlv`, `set_state_tlv`
- Pump + event integration: `pump`, `poll_event`
- Present: `render` (may be a no-op for some native backends)
- Programmatic quit: `request_quit`

Extension discovery:
- `query_interface(iid, &out_iface)` supports optional surfaces without changing the root ABI.
- Defined IIDs:
  - `DUI_IID_TEST_API_V1`: event injection for smoke tests only.
  - `DUI_IID_NATIVE_API_V1`: native window handle access (presentation-only).

Capability surface:
- `dui_caps` is a `u64` bitset returned by `get_caps()`.
- Schemas may express visibility/requirements via `DUI_TLV_REQUIRED_CAPS_U64`.

Headless request:
- `DUI_WINDOW_FLAG_HEADLESS` asks a backend to operate without an OS-visible window when supported (used by CI smoke tests; DGFX uses a headless system backend).

## 3. Event Flow Contract (No UI-side State Authority)

Strict flow:
1. Launcher computes an authoritative **state snapshot** (and schema when needed).
2. DUI backend renders the snapshot (presentation only).
3. User interaction produces a DUI event (`DUI_EVENT_*`).
4. Launcher consumes the event and applies an action to core state.
5. Launcher emits the next snapshot; DUI reflects it.

Rules:
- UI backends must not mutate authoritative state.
- No hidden side effects in UI (no persistence, no gameplay/state decisions).
- UI must not influence determinism; only explicit events are inputs.

## 4. Data-Driven UI: TLV Schema + State

DUI uses TLV streams consistent with Domino’s TLV conventions (skip-unknown).

### 4.1 Schema TLV (`SCH1`)

Header: `include/dui/dui_schema_tlv.h`

Root:
- `DUI_TLV_SCHEMA_V1` (`'SCH1'`) → payload is nested TLV
  - `DUI_TLV_FORM_V1` (`'FORM'`) → payload is nested TLV
    - `DUI_TLV_NODE_V1` (`'NODE'`) → payload is nested TLV describing one node

Node fields:
- `DUI_TLV_ID_U32`: stable node/widget id
- `DUI_TLV_KIND_U32`: `dui_node_kind` (layout or widget)
- `DUI_TLV_TEXT_UTF8`: label text / button text / checkbox caption
- `DUI_TLV_ACTION_U32`: action id emitted on activation
- `DUI_TLV_BIND_U32`: state binding id used by `STATE/VALU` records
- `DUI_TLV_FLAGS_U32`: node flags (`DUI_NODE_FLAG_*`)
- `DUI_TLV_REQUIRED_CAPS_U64`: visibility requirement (capability bits)
- `DUI_TLV_CHILDREN_V1`: nested TLV stream of child nodes (for layout nodes)
- `DUI_TLV_VALIDATION_V1`: nested TLV rules (e.g. `DUI_TLV_MIN_U32`, `DUI_TLV_MAX_U32`)

Visibility / capability gating:
- Backends should treat `REQUIRED_CAPS` as: hide/disable a node when the backend does not provide the required capability bits.

### 4.2 State TLV (`STA1`)

State snapshots are separate from schema and are expected to be emitted frequently.

Root:
- `DUI_TLV_STATE_V1` (`'STA1'`) → payload is nested TLV
  - `DUI_TLV_VALUE_V1` (`'VALU'`) → one bound value record

Value record fields:
- `DUI_TLV_BIND_U32`: binding id (must match a node’s `BIND`)
- `DUI_TLV_VALUE_TYPE_U32`: `dui_value_type`
- One of:
  - `DUI_TLV_VALUE_U32`, `DUI_TLV_VALUE_I32`, `DUI_TLV_VALUE_U64`, `DUI_TLV_VALUE_UTF8`
  - `DUI_TLV_LIST_V1` (`'LIST'`) for list widgets:
    - `DUI_TLV_LIST_SELECTED_U32`, `DUI_TLV_LIST_ITEM_V1` (`'ITEM'`) with `DUI_TLV_ITEM_ID_U32` + `DUI_TLV_ITEM_TEXT_UTF8`

## 5. Backends

Backends are thin renderers that:
- parse schema/state TLV,
- create/update presentation surfaces,
- translate platform events into DUI events.

No backend may contain launcher business logic.

Current modules:
- `source/domino/dui/dui_win32.c`: Win32 common-controls backend.
- `source/domino/dui/dui_dgfx.c`: DGFX-rendered fallback backend (supports `DUI_WINDOW_FLAG_HEADLESS`).
- `source/domino/dui/dui_null.c`: headless backend (no OS window).
- `source/domino/dui/dui_gtk.c`: GTK backend module stub (unavailable when not supported/built).
- `source/domino/dui/dui_macos.c`: macOS backend module stub (unavailable when not supported/built).

## 6. Backend Selection + Audit

Selection is performed via the capability registry:
- DUI is a registry subsystem (`DOM_SUBSYS_DUI`).
- A profile may override the selected DUI backend using key `ui`.
- CLI `--ui=native|dgfx|null` maps to an appropriate backend name for the host OS.

If the selected backend cannot be created at runtime:
- the launcher attempts a deterministic fallback chain (native → dgfx → null),
- the final backend and fallback reason are recorded in audit output.

## 7. Smoke Tests

Smoke tests validate the event/pump/schema/state contract without user interaction:
- Test source: `source/tests/domino_dui_smoke.c`
- CTest entries:
  - `domino_dui_smoke_null`
  - `domino_dui_smoke_dgfx` (runs headless)
  - `domino_dui_smoke_native` (Windows: win32)

All smoke tests must:
- create a window/surface (or headless equivalent),
- render a small schema (≥ 3 widgets),
- pump events, request quit, observe a quit event, and exit cleanly.
