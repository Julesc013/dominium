# UI Doc TLV (IR foundation)

## Scope
- Defines the in-memory UI IR concepts and canonicalization rules implemented in `source/domino/ui_ir`.
- Defines the TLV wire format v1 for `ui_doc.tlv` (DTLV container + nested TLV streams).
- TLV is the canonical on-disk format; JSON is a deterministic mirror generated on save.

## IR concepts
- Document metadata: `doc_version` (starts at 1), `doc_name`, optional `doc_guid`.
- Widget table keyed by `id` (0 is reserved for “no parent”).
- Widget fields: `type`, `name`, `parent_id`, `z_order`, rect (`x,y,w,h`), `layout_mode`, `dock`,
  `anchors`, `margin`, `padding`, constraints (`min_w/min_h/max_w/max_h`), `props`, and `events`.
- Properties: typed key/value pairs (`INT`, `UINT`, `BOOL`, `STRING`, `VEC2I`, `RECTI`).
- Events: `event_name -> action_key` bindings (e.g., `on_click`, `on_change`, `on_submit`).

## Canonicalization rules
- IDs are monotonic per document; never reused after deletion.
- Canonical widget order is root-first traversal; siblings are ordered by `(z_order, id)` when no explicit order exists.
- Properties are stored and iterated in lexicographic byte order by key.
- Events are stored and iterated in lexicographic byte order by event name.

## Capability system and validation
- Backends register capability tables declaratively in `source/domino/ui_ir/ui_caps.*`.
- Targets are declared in `doc.meta.target_backends` and `doc.meta.target_tiers`.
- If targets are empty, validation defaults to `["win32"]` and the highest known tier for that backend.
- Validator checks widget types, properties, and events against each target backend/tier.
- Unsupported widget/property/event is an error; emulated features are warnings.
- Tier mismatches (e.g., doc requires `win32_t1` but targets include `win32_t0`) are errors.
- Diagnostics are deterministically ordered by severity, widget id, feature key, and message.

## Layout engine v1 (deterministic)
- Layout is computed by `domui_compute_layout` in `source/domino/ui_ir/ui_layout.*` with canonical widget order output.
- Parent content rect = parent rect inset by padding.
- Precedence per child: dock (`dock != NONE`) -> anchors (`anchors != 0`) -> absolute.
- Dock uses the remaining parent content rect (canonical order): LEFT/RIGHT reserve width, TOP/BOTTOM reserve height, FILL consumes remaining space.
- Margins are treated as outer offsets and are included in dock reservations and stack spacing.
- Anchor offsets are stored in widget fields:
  - L only: `x` is left offset, `w` is width.
  - R only: `x` is right offset, `w` is width.
  - L+R: `x` is left offset, `w` is right offset (width grows/shrinks with parent).
  - T/B use `y`/`h` with the same rules.
- Absolute uses `x,y` as left/top offsets and `w,h` as size (margins shift by left/top).
- Stack layouts (`STACK_ROW`/`STACK_COL`) place children sequentially along the axis using their sizes and margins; dock/anchors are ignored; no wrapping; excess space remains unused.
- Constraints clamp final sizes after base rect calculation; z-order never affects geometry.
- Diagnostics: multiple FILL dock children -> warning; negative size after constraints -> error; child outer bounds exceeding parent content -> error.
- Example: parent width 100, anchored L+R child `x=10`, `w=20` yields width `100 - 10 - 20 = 70`.

## TLV wire format v1 (ui_doc.tlv)
### Container header
- File is a DTLV container v1 (see `docs/SPEC_CONTAINER_TLV.md`).
- Header fields: magic `DTLV`, endian marker `0xFFFE` (little-endian), version `1`, directory entries.

### Top-level chunks (DTLV directory entries)
- `META` (version 1): document metadata TLV stream.
- `WIDG` (version 1): widget records TLV stream.
- `RSRC` (version 1): reserved (not written yet).
- `EVNT` (version 1): reserved (not written yet).
- `ORDR` (version 1): reserved (not written yet).

### META chunk TLV stream
- `VERS` (u32): `doc_version`.
- `NAME` (utf8 bytes): `doc_name`.
- `GUID` (utf8 bytes, optional): `doc_guid`.
- `BACK` (TLV list): target backends list.
- `TIER` (TLV list): target tiers list.
- List encoding: TLV stream of `ITEM` entries (each `ITEM` payload is UTF-8 bytes).

### WIDG chunk TLV stream
- Contains repeated `WID1` records. Each `WID1` payload is a TLV stream:
  - `ID__` (u32): widget id.
  - `TYPE` (u32): widget type enum.
  - `NAME` (utf8 bytes): widget name.
  - `PAR_` (u32): parent id (0 means root).
  - `ZORD` (u32): z-order.
  - `RECT` (4x i32): `x, y, w, h` (little-endian).
  - `LAYO` (u32): layout mode enum.
  - `DOCK` (u32): dock mode enum.
  - `ANCH` (u32): anchor bitmask (L=1,R=2,T=4,B=8).
  - `MARG` (4x i32): margin box in order `left, right, top, bottom`.
  - `PADD` (4x i32): padding box in order `left, right, top, bottom`.
  - `MINW` (i32): min width.
  - `MINH` (i32): min height.
  - `MAXW` (i32): max width (-1 means unset).
  - `MAXH` (i32): max height (-1 means unset).
  - `PROP` (TLV list): widget properties.
  - `EVTS` (TLV list): widget events.

### PROP list entries (within `PROP`)
- Each entry is `PRP1` with:
  - `PKEY` (utf8 bytes): property key.
  - `PTYP` (u32): value type enum.
  - One value tag:
    - `PINT` (i32)
    - `PUNT` (u32)
    - `PBOL` (u32; 0/1)
    - `PSTR` (utf8 bytes)
    - `PV2I` (2x i32): `x, y`
    - `PRCT` (4x i32): `x, y, w, h`

### EVTS list entries (within `EVTS`)
- Each entry is `EVT1` with:
  - `ENAM` (utf8 bytes): event name.
  - `ACTN` (utf8 bytes): action key.

### Canonical write rules
- Widgets are written in canonical widget order (root-first; siblings by `(z_order, id)`).
- Properties are written in lexicographic key order.
- Events are written in lexicographic event name order.
- TLV tags/lengths are little-endian; no timestamps or random IDs.

### Save behavior
- Writes `path.tmp`, rotates backups `path.bak1..bak10`, then atomically replaces `path`.
- Writes a deterministic JSON mirror alongside the TLV (`ui_doc.json`).

## Non-goals (this prompt)
- No TLV schema for resources/events/ordering chunks yet.
- No JSON import or JSON-as-source-of-truth.
- No editor UI.
- No DPI scaling or backend-specific rendering changes.
