Status: DERIVED
Version: 1.0.0

# System Topology Map

- topology_id: `dominium.audit.topology_map`
- repository_hash: `HEAD:382ec4253d419c3e4491e4a2e993bda3b4262c27`
- generated_tick: `0`
- deterministic_fingerprint: `e5fc7db7f0a960433e0fa49a4261643fc4acd776fdacd3d21ce7ce3e13571664`

## Counts
- node_count: 2248
- edge_count: 87649

## Node Kinds
- contract_set: 4
- module: 70
- policy_set: 106
- process_family: 149
- registry: 157
- schema: 780
- tool: 982

## Edge Kinds
- consumes: 2285
- depends_on: 1073
- enforces: 19800
- produces: 1
- validates: 64490

## Major Runtime Modules
- `module:client`
- `module:client/adapters`
- `module:client/app`
- `module:client/core`
- `module:client/gui`
- `module:client/input`
- `module:client/modes`
- `module:client/observability`
- `module:client/presentation`
- `module:client/shell`
- `module:client/ui`
- `module:engine`
- `module:engine/include`
- `module:engine/modules`
- `module:engine/render`
- `module:engine/tests`
- `module:game`
- `module:game/content`
- `module:game/core`
- `module:game/include`
- `module:game/mods`
- `module:game/rules`
- `module:game/tests`
- `module:launcher`
- `module:launcher/cli`
- `module:launcher/core`
- `module:launcher/gui`
- `module:launcher/include`
- `module:launcher/tui`
- `module:server`
- `module:server/app`
- `module:server/authority`
- `module:server/gui`
- `module:server/net`
- `module:server/persistence`
- `module:server/shard`
- `module:server/tests`
- `module:setup`
- `module:setup/cli`
- `module:setup/core`
- `module:setup/gui`
- `module:setup/include`
- `module:setup/packages`
- `module:setup/tui`
- `module:src`
- `module:src/client`
- `module:src/control`
- `module:src/control/control_plane_engine.py`
- `module:src/control/effects/effect_engine.py`
- `module:src/control/fidelity/fidelity_engine.py`
- `module:src/control/ir/control_ir_compiler.py`
- `module:src/control/negotiation/negotiation_kernel.py`
- `module:src/control/view/view_engine.py`
- `module:src/core`
- `module:src/diegetics`
- `module:src/epistemics`
- `module:src/infrastructure`
- `module:src/inspection`
- `module:src/interaction`
- `module:src/interior`
- `module:src/logistics`
- `module:src/machines`
- `module:src/materials`
- `module:src/mechanics`

## Control Subsystem Nodes
- `module:src/control/control_plane_engine.py`
- `module:src/control/effects/effect_engine.py`
- `module:src/control/fidelity/fidelity_engine.py`
- `module:src/control/ir/control_ir_compiler.py`
- `module:src/control/negotiation/negotiation_kernel.py`
- `module:src/control/view/view_engine.py`

## Notes
- Process-family discovery is best-effort via deterministic process token scanning.
- Control dependency edges are synthesized for modules that reference control-plane APIs.
- Artifact is governance-only and not loaded by runtime simulation code.
