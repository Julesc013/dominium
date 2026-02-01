Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Exploration Metrics (W1)

Status: derived, non-authoritative.
Scope: exploration navigation, camera, inspect, and renderer behavior.

These metrics are derived from replay logs, UI event logs, and CLI output. They
never affect simulation and are reproducible from the same artifacts.

## Source artifacts
- Replay logs (`DOMINIUM_REPLAY_V1`) from exploration runs.
- UI event logs (`--ui-log`) for GUI/TUI runs.
- CLI status output (`where`) for current domain snapshot.

## Metric definitions

### active_domain_count
Count of active domains at the end of the navigation script.
Derived from `where` output:
- `current_node_id` present → `active_domain_count = 1`
- no active world → `active_domain_count = 0`

### expanded_domain_count
Count of expanded domains at the end of the navigation script.
Derived from event logs:
- if expand events are logged, count unique expanded domains.
- if no expand events are logged, treat as `1` when a world is active.

### camera_update_ops_per_tick
Count of `client.nav.camera` events per navigation script tick.
Derived from replay event log counts for `client.nav.camera`.

### inspect_ops_per_tick
Count of `client.inspect.toggle` events per navigation script tick.
Derived from replay event log counts for `client.inspect.toggle`.

### renderer_draw_calls
Count of renderer draw events per UI script.
Derived from UI logs:
- count `renderer.draw` and `ui.render` tokens if present
- if no renderer tokens are emitted, the value is `0`

### renderer_traversal_nodes
Count of topology node references seen by the renderer.
Derived from UI logs:
- count tokens like `node_id=` or `topology.` in UI logs
- `0` indicates renderer did not traverse world topology

### snapshot_reads_per_tick
Count of world snapshot loads per navigation script tick.
Derived from replay event log counts for `client.world.load`.

## Notes
- All metrics are relative counts, not wall-clock time.
- These metrics are deterministic and can be recomputed from logs.
- This document does not authorize changes to simulation behavior.