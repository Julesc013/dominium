# control Semantic Scan

## Status

- Scan type: `semantic_scan`
- Findings: 2108
- Moves/rewrites applied: `false`

## Markers Found

- `control/control_plane_engine.py:1` deterministic
- `control/control_plane_engine.py:1` control
- `control/control_plane_engine.py:11` capability
- `control/control_plane_engine.py:16` control
- `control/control_plane_engine.py:17` control
- `control/control_plane_engine.py:17` entitlement
- `control/control_plane_engine.py:18` control
- `control/control_plane_engine.py:19` control
- `control/control_plane_engine.py:20` control
- `control/control_plane_engine.py:21` control
- `control/control_plane_engine.py:22` control
- `control/control_plane_engine.py:23` mutation
- `control/control_plane_engine.py:23` control
- `control/control_plane_engine.py:23` replay
- `control/control_plane_engine.py:24` control
- `control/control_plane_engine.py:79` seed
- `control/control_plane_engine.py:79` hash
- `control/control_plane_engine.py:83` seed
- `control/control_plane_engine.py:117` control
- `control/control_plane_engine.py:128` process
- `control/control_plane_engine.py:133` process
- `control/control_plane_engine.py:134` process
- `control/control_plane_engine.py:135` process
- `control/control_plane_engine.py:137` process
- `control/control_plane_engine.py:145` schema
- `control/control_plane_engine.py:149` entitlement
- `control/control_plane_engine.py:157` control
- `control/control_plane_engine.py:160` control
- `control/control_plane_engine.py:161` control
- `control/control_plane_engine.py:165` schema
- `control/control_plane_engine.py:166` control
- `control/control_plane_engine.py:190` schema
- `control/control_plane_engine.py:218` server
- `control/control_plane_engine.py:220` server
- `control/control_plane_engine.py:222` server
- `control/control_plane_engine.py:223` server
- `control/control_plane_engine.py:234` process
- `control/control_plane_engine.py:234` replay
- `control/control_plane_engine.py:235` process
- `control/control_plane_engine.py:239` process
- `control/control_plane_engine.py:240` process
- `control/control_plane_engine.py:241` process
- `control/control_plane_engine.py:242` process
- `control/control_plane_engine.py:243` process
- `control/control_plane_engine.py:244` process
- `control/control_plane_engine.py:248` control
- `control/control_plane_engine.py:249` control
- `control/control_plane_engine.py:251` control
- `control/control_plane_engine.py:252` control
- `control/control_plane_engine.py:257` control

## Highest-Risk Files

- `control/__init__.py`
- `control/control_plane_engine.py`
- `control/capability/__init__.py`
- `control/capability/capability_engine.py`
- `control/effects/__init__.py`
- `control/effects/effect_engine.py`
- `control/fidelity/__init__.py`
- `control/fidelity/fidelity_engine.py`
- `control/ir/__init__.py`
- `control/ir/control_ir_compiler.py`
- `control/ir/control_ir_multiplayer.py`
- `control/ir/control_ir_programs.py`
- `control/ir/control_ir_verifier.py`
- `control/negotiation/__init__.py`
- `control/negotiation/negotiation_kernel.py`
- `control/planning/__init__.py`
- `control/planning/plan_engine.py`
- `control/proof/__init__.py`
- `control/proof/control_proof_bundle.py`
- `control/view/__init__.py`
- `control/view/view_engine.py`

## Unknowns

- preserve_unknown entries: 8

## Future Validator Needs

Dedicated validators are required before moving any sensitive files from this root.
