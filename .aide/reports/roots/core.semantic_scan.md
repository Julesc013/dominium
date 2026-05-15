# core Semantic Scan

## Status

- Scan type: `semantic_scan`
- Findings: 367
- Moves/rewrites applied: `false`

## Markers Found

- `core/__init__.py:1` deterministic
- `core/constraints/constraint_engine.py:1` deterministic
- `core/constraints/constraint_engine.py:13` deterministic
- `core/constraints/constraint_engine.py:61` schema
- `core/constraints/constraint_engine.py:112` schema
- `core/constraints/constraint_engine.py:141` deterministic
- `core/constraints/constraint_engine.py:155` process
- `core/constraints/constraint_engine.py:160` process
- `core/constraints/constraint_engine.py:201` process
- `core/constraints/constraint_engine.py:208` process
- `core/constraints/constraint_engine.py:222` deterministic
- `core/constraints/__init__.py:1` deterministic
- `core/flow/flow_engine.py:1` deterministic
- `core/flow/flow_engine.py:9` network
- `core/flow/flow_engine.py:10` shard
- `core/flow/flow_engine.py:20` deterministic
- `core/flow/flow_engine.py:59` fixed
- `core/flow/flow_engine.py:137` schema
- `core/flow/flow_engine.py:140` deterministic
- `core/flow/flow_engine.py:160` schema
- `core/flow/flow_engine.py:164` deterministic
- `core/flow/flow_engine.py:484` deterministic
- `core/flow/flow_engine.py:516` deterministic
- `core/flow/flow_engine.py:538` deterministic
- `core/flow/flow_engine.py:552` schema
- `core/flow/flow_engine.py:648` schema
- `core/flow/flow_engine.py:649` schema
- `core/flow/flow_engine.py:650` schema
- `core/flow/flow_engine.py:652` schema
- `core/flow/flow_engine.py:685` schema
- `core/flow/flow_engine.py:686` schema
- `core/flow/flow_engine.py:687` schema
- `core/flow/flow_engine.py:690` schema
- `core/flow/flow_engine.py:699` deterministic
- `core/flow/flow_engine.py:702` deterministic
- `core/flow/flow_engine.py:703` deterministic
- `core/flow/flow_engine.py:740` process
- `core/flow/flow_engine.py:744` process
- `core/flow/flow_engine.py:747` process
- `core/flow/flow_engine.py:748` process
- `core/flow/flow_engine.py:749` process
- `core/flow/flow_engine.py:751` process
- `core/flow/flow_engine.py:794` runtime
- `core/flow/flow_engine.py:826` network
- `core/flow/flow_engine.py:849` shard
- `core/flow/flow_engine.py:853` deterministic
- `core/flow/flow_engine.py:855` shard
- `core/flow/flow_engine.py:857` network
- `core/flow/flow_engine.py:865` deterministic
- `core/flow/flow_engine.py:867` shard

## Highest-Risk Files

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

## Unknowns

- preserve_unknown entries: 7

## Future Validator Needs

Dedicated validators are required before moving any sensitive files from this root.
