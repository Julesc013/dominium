# UI Doc TLV (IR foundation)

## Scope
- Defines the in-memory UI IR concepts and canonicalization rules implemented in `source/domino/ui_ir`.
- TLV wire format is deferred to Prompt 3.

## IR concepts
- Document metadata: `doc_version` (starts at 1), `doc_name`, optional `doc_guid`.
- Widget table keyed by `id` (0 is reserved for “no parent”).
- Widget fields: `type`, `name`, `parent_id`, `z_order`, rect (`x,y,w,h`), `dock`, `anchors`,
  `margin`, `padding`, constraints (`min_w/min_h/max_w/max_h`), `props`, and `events`.
- Properties: typed key/value pairs (`INT`, `UINT`, `BOOL`, `STRING`, `VEC2I`, `RECTI`).
- Events: `event_name -> action_key` bindings (e.g., `on_click`, `on_change`, `on_submit`).

## Canonicalization rules
- IDs are monotonic per document; never reused after deletion.
- Canonical widget order is root-first traversal; siblings are ordered by `(z_order, id)` when no explicit order exists.
- Properties are stored and iterated in lexicographic byte order by key.
- Events are stored and iterated in lexicographic byte order by event name.

## Deferred (Prompt 3)
- TLV serialization/deserialization details.
