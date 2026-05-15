# packs Draft Salvage Map

## Status: Draft / Not Approved

- Apply allowed: `false`
- Approval status: `not_approved`
- Entry count: 364

## Recommended Fates

- `adapt`: 4
- `convert`: 1
- `preserve_unknown`: 359

## Candidate Future Target Locations

No target paths are approved. Future targets must be selected by an approved move plan.

## High-Risk Files

- `packs/__init__.py`
- `packs/README.md`
- `packs/blueprints/blueprints.default.m1/data/blueprint.house.basic.json`
- `packs/blueprints/blueprints.default.m1/data/blueprint.lathe.basic.json`
- `packs/blueprints/blueprints.default.m1/data/blueprint.road.segment.basic.json`
- `packs/blueprints/blueprints.default.m1/data/blueprint.simple_bridge.basic.json`
- `packs/blueprints/blueprints.default.m1/data/blueprint.space_elevator.template.json`
- `packs/compat/__init__.py`
- `packs/compat/pack_compat_validator.py`
- `packs/compat/pack_verification_pipeline.py`
- `packs/core/constraints.worldgen.default_lab/pack.capabilities.json`
- `packs/core/constraints.worldgen.default_lab/pack.compat.json`
- `packs/core/constraints.worldgen.default_lab/pack.json`
- `packs/core/constraints.worldgen.default_lab/pack.trust.json`
- `packs/core/constraints.worldgen.default_lab/data/constraints.lab.navigation.default.json`
- `packs/core/pack.core.camera/pack.capabilities.json`
- `packs/core/pack.core.camera/pack.compat.json`
- `packs/core/pack.core.camera/pack.json`
- `packs/core/pack.core.camera/pack.trust.json`
- `packs/core/pack.core.camera/data/camera_assembly.main.json`
- `packs/core/pack.core.camera/data/camera_processes.json`
- `packs/core/pack.core.diegetic_instruments/pack.capabilities.json`
- `packs/core/pack.core.diegetic_instruments/pack.compat.json`
- `packs/core/pack.core.diegetic_instruments/pack.json`
- `packs/core/pack.core.diegetic_instruments/pack.trust.json`

## preserve_unknown Files

- `packs/blueprints`
- `packs/blueprints/blueprints.default.m1`
- `packs/blueprints/blueprints.default.m1/data`
- `packs/blueprints/blueprints.default.m1/data/blueprint.house.basic.json`
- `packs/blueprints/blueprints.default.m1/data/blueprint.lathe.basic.json`
- `packs/blueprints/blueprints.default.m1/data/blueprint.road.segment.basic.json`
- `packs/blueprints/blueprints.default.m1/data/blueprint.simple_bridge.basic.json`
- `packs/blueprints/blueprints.default.m1/data/blueprint.space_elevator.template.json`
- `packs/compat`
- `packs/core`
- `packs/core/constraints.worldgen.default_lab`
- `packs/core/constraints.worldgen.default_lab/pack.capabilities.json`
- `packs/core/constraints.worldgen.default_lab/pack.compat.json`
- `packs/core/constraints.worldgen.default_lab/pack.json`
- `packs/core/constraints.worldgen.default_lab/pack.trust.json`
- `packs/core/constraints.worldgen.default_lab/data`
- `packs/core/constraints.worldgen.default_lab/data/constraints.lab.navigation.default.json`
- `packs/core/pack.core.camera`
- `packs/core/pack.core.camera/pack.capabilities.json`
- `packs/core/pack.core.camera/pack.compat.json`
- `packs/core/pack.core.camera/pack.json`
- `packs/core/pack.core.camera/pack.trust.json`
- `packs/core/pack.core.camera/data`
- `packs/core/pack.core.camera/data/camera_assembly.main.json`
- `packs/core/pack.core.camera/data/camera_processes.json`

## References Requiring Future Rewrite

- Raw references recorded: 2775

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
