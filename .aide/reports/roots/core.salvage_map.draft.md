# core Draft Salvage Map

## Status: Draft / Not Approved

- Apply allowed: `false`
- Approval status: `not_approved`
- Entry count: 23

## Recommended Fates

- `adapt`: 16
- `preserve_unknown`: 7

## Candidate Future Target Locations

No target paths are approved. Future targets must be selected by an approved move plan.

## High-Risk Files

- `core/__init__.py`
- `core/constraints/__init__.py`
- `core/constraints/constraint_engine.py`
- `core/flow/__init__.py`
- `core/flow/flow_engine.py`
- `core/graph/__init__.py`
- `core/graph/network_graph_engine.py`
- `core/graph/routing_engine.py`
- `core/hazards/__init__.py`
- `core/hazards/hazard_engine.py`
- `core/schedule/__init__.py`
- `core/schedule/schedule_engine.py`
- `core/spatial/__init__.py`
- `core/spatial/spatial_engine.py`
- `core/state/__init__.py`
- `core/state/state_machine_engine.py`

## preserve_unknown Files

- `core/constraints`
- `core/flow`
- `core/graph`
- `core/hazards`
- `core/schedule`
- `core/spatial`
- `core/state`

## References Requiring Future Rewrite

- Raw references recorded: 5098

## Validators Required Before Any Move

- AIDE salvage-map check
- repo layout strict validator
- root allowlist strict validator
- distribution/component validators
- docs/build/UI/ABI checks as applicable

## Blockers Before Move

- No approved salvage map.
- No approved move map.
- No reference rewrite plan.
- No rollback evidence packet.
