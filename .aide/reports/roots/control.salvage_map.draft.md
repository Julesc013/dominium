# control Draft Salvage Map

## Status: Draft / Not Approved

- Apply allowed: `false`
- Approval status: `not_approved`
- Entry count: 29

## Recommended Fates

- `adapt`: 21
- `preserve_unknown`: 8

## Candidate Future Target Locations

No target paths are approved. Future targets must be selected by an approved move plan.

## High-Risk Files

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

## preserve_unknown Files

- `control/capability`
- `control/effects`
- `control/fidelity`
- `control/ir`
- `control/negotiation`
- `control/planning`
- `control/proof`
- `control/view`

## References Requiring Future Rewrite

- Raw references recorded: 1267

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
