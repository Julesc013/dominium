# Event Queue

All platform/runtime events flow through a single FIFO queue and are consumed
by application loops via `dsys_poll_event()`.

## Event structure
- `dsys_event` includes `timestamp_us`, populated from the platform monotonic
  clock if not already set.
- `dsys_event.window` is the owning window handle (NULL for non-window events).
- `dsys_event.window_id` is a stable numeric id (0 when not associated).
- Event categories: window events, input events (raw), lifecycle events, and
  internal application events.

## Sources
- Platform backends enqueue events using internal helpers.
- Internal sources (e.g., terminal input for TUI) inject events using
  `dsys_inject_event()`.

## Ordering and determinism
- Events are dequeued in FIFO order.
- Timestamps are monotonic and best-effort; deterministic modes do not depend
  on wall-clock time for logical advancement.

## Capacity and errors
- Queue capacity is fixed (`128` events).
- `dsys_inject_event()` fails if the queue is full and sets the last-error
  string for diagnostics.
