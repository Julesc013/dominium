--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. This spec is implemented under `tools/`.

GAME:
- None. This spec is implemented under `tools/`.

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

SCHEMA:
- Canonical formats and migrations defined here live under `schema/`.

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.
- No runtime authority or game rules inside tools.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# UI Doc TLV (IR + Wire Format)

## Scope
- Defines the canonical UI IR model and deterministic rules implemented in `source/domino/ui_ir`.
- Defines the TLV wire format for `ui_doc.tlv` (DTLV container + nested TLV streams).
- Defines the layout semantics and validation integration points.
- TLV is the source of truth; JSON is a deterministic mirror.

## IR model summary
- Document metadata (`domui_doc_meta`):
  - `doc_version` (u32, current = 2)
  - `doc_name` (string), optional `doc_guid` (string)
  - `target_backends` (string list), `target_tiers` (string list)
- Widget table keyed by `domui_widget_id` (u32). `parent_id = 0` means root.
- Widget fields (minimum):
  - identity: `id`, `type`, `name`, `parent_id`, `z_order`
  - rect: `x, y, w, h` (design pixels, integer)
  - layout: `layout_mode`, `dock`, `anchors` (bitmask), `margin`, `padding`
  - constraints: `min_w`, `min_h`, `max_w`, `max_h` (`-1` means unset)
  - `props` (typed property bag), `events` (event_name → action_key)
- Properties:
  - value types: `INT`, `UINT`, `BOOL`, `STRING`, `VEC2I`, `RECTI`
  - stored and iterated in lexicographic byte order by key
- Events:
  - `event_name -> action_key` bindings (e.g., `on_click`, `on_change`, `on_submit`)
  - stored and iterated in lexicographic order by event name

## Widget property keys (v2 additions)
- Splitter:
  - `splitter.orientation` = `"h"` or `"v"`
  - `splitter.pos` = int (pixels, design space)
  - `splitter.thickness` = int
  - `splitter.min_a`, `splitter.min_b` = int
- Tabs:
  - `tabs.selected_index` = int
  - `tabs.placement` = `"top"` | `"bottom"` | `"left"` | `"right"`
- Tab page:
  - `tab.title` = string
  - `tab.enabled` = bool
- Scroll panel:
  - `scroll.h_enabled`, `scroll.v_enabled` = bool
  - `scroll.x`, `scroll.y` = int

## Canonicalization rules
- IDs are monotonic per document; never reused after deletion.
- Canonical widget order:
  - root-first traversal
  - siblings ordered by `(z_order, id)` when no explicit order exists
- Properties ordered lexicographically by key bytes.
- Events ordered lexicographically by event name bytes.

## Layout semantics (v1, deterministic)
- Public API: `domui_compute_layout` in `source/domino/ui_ir/ui_layout.*`.
- Output is a flat array in canonical widget order.
- Parent content rect = parent rect inset by padding.
- Precedence per child: dock (`dock != NONE`) → anchors (`anchors != 0`) → absolute.

### Absolute
- `x,y` are left/top offsets from parent content rect.
- `w,h` are sizes in design pixels.
- Margins offset the final rect (`x += margin.left`, `y += margin.top`).

### Anchors
- L only: `x` is left offset, `w` is width.
- R only: `x` is right offset, `w` is width.
- L+R: `x` is left offset, `w` is right offset (width grows/shrinks with parent).
- T/B use `y,h` with the same rules.
- Margins apply before constraints.

### Dock
- Parent content rect starts as available space.
- Process children in canonical order:
  - LEFT/RIGHT reserve width
  - TOP/BOTTOM reserve height
  - FILL consumes remaining space
- Margins are applied before reservation.
- Dock ignores anchors.

### Stack layouts (`STACK_ROW` / `STACK_COL`)
- Children laid out sequentially along axis.
- Margins are applied between children.
- No wrapping in v1; excess space remains unused.
- Dock/anchors ignored in v1 stack.

### Constraints
- Apply `min_w/min_h/max_w/max_h` after base rect calculation.
- Clamp deterministically; `max_* = -1` means “no max”.

### Splitter
- Splits available rect into two panes (first two children).
- Orientation `"v"` splits left/right; `"h"` splits top/bottom.
- `splitter.pos` and `splitter.thickness` are in pixels.
- Extra children get zero rects.

### Tabs
- Reserves a tab strip (default thickness 24) by `tabs.placement`.
- Only the selected page is laid out to remaining content rect.
- Non-selected pages get zero rects.

### Scroll panel
- Establishes a viewport (panel rect).
- First child is laid out at `(0,0)` with its own size (or viewport if size is 0).
- Extra children get zero rects.

### Diagnostics
- Multiple FILL dock children in a container → warning.
- Negative size after constraints → error.
- Parent rect too small to satisfy child constraints → error.

## Capability system integration
- Backends register capability tables in `source/domino/ui_ir/ui_caps.*`.
- Targets declared in `doc.meta.target_backends` and `doc.meta.target_tiers`.
- If targets are empty, validation defaults to `["win32"]` + highest known tier.
- Validator checks widget types, properties, and events against each target.
- Unsupported widget/property/event is an error; emulated features are warnings.
- Diagnostics are ordered by severity, widget id, feature key, and message.

## TLV wire format v2 (ui_doc.tlv)
### Container header
- DTLV container v1 (see `docs/SPEC_CONTAINER_TLV.md`).
- Header: magic `DTLV`, endian marker `0xFFFE` (LE), version `1`, directory entries.

### Top-level chunks (DTLV directory entries)
- `META` (version 2): document metadata TLV stream.
- `WIDG` (version 2): widget records TLV stream.
- `RSRC`, `EVNT`, `ORDR`: reserved (not written yet).

### META chunk TLV stream
- `VERS` (u32): `doc_version`
- `NAME` (utf8 bytes): `doc_name`
- `GUID` (utf8 bytes, optional): `doc_guid`
- `BACK` (TLV list): target backends
- `TIER` (TLV list): target tiers
- List encoding: TLV stream of `ITEM` entries (payload is UTF-8 bytes)

### WIDG chunk TLV stream
- Repeated `WID1` records; each `WID1` payload is a TLV stream:
  - `ID__` (u32): widget id
  - `TYPE` (u32): widget type enum
  - `NAME` (utf8 bytes): widget name
  - `PAR_` (u32): parent id (0 = root)
  - `ZORD` (u32): z-order
  - `RECT` (4x i32): `x, y, w, h`
  - `LAYO` (u32): layout mode enum
  - `DOCK` (u32): dock mode enum
  - `ANCH` (u32): anchor bitmask (L=1,R=2,T=4,B=8)
  - `MARG` (4x i32): margin box `left, right, top, bottom`
  - `PADD` (4x i32): padding box `left, right, top, bottom`
  - `MINW` / `MINH` / `MAXW` / `MAXH` (i32)
  - `PROP` (TLV list): widget properties
  - `EVTS` (TLV list): widget events

### PROP list entries
- Each entry is `PRP1` with:
  - `PKEY` (utf8 bytes): property key
  - `PTYP` (u32): value type enum
  - One value tag:
    - `PINT` (i32)
    - `PUNT` (u32)
    - `PBOL` (u32; 0/1)
    - `PSTR` (utf8 bytes)
    - `PV2I` (2x i32): `x, y`
    - `PRCT` (4x i32): `x, y, w, h`

### EVTS list entries
- Each entry is `EVT1` with:
  - `ENAM` (utf8 bytes): event name
  - `ACTN` (utf8 bytes): action key

### Canonical write rules
- Widgets are written in canonical widget order.
- Properties are written in lexicographic key order.
- Events are written in lexicographic event name order.
- Tags/lengths are little-endian; no timestamps or random IDs.

## Versioning and migration
- `doc_version` is stored in `META.VERS`.
- v1 documents are accepted on load and migrated to v2:
  - Splitter defaults: `orientation="v"`, `pos=-1`, `thickness=4`, `min_a=0`, `min_b=0`
  - Tabs defaults: `selected_index=0`, `placement="top"`
  - Tab page defaults: `title=""`, `enabled=true`
  - Scroll panel defaults: `h_enabled=true`, `v_enabled=true`, `x=0`, `y=0`
- Migration is deterministic and does not renumber IDs.

## Save behavior
- Atomic save: write `path.tmp`, rotate `path.bak1..bak10`, then replace `path`.
- JSON mirror: `ui_doc.json` written alongside TLV when `DOMUI_ENABLE_JSON_MIRROR=ON`.

## Non-goals
- No TLV schema for resources/events/ordering chunks yet.
- No JSON import or JSON-as-source-of-truth.
- No editor UI or backend rendering changes.
