Status: DERIVED
Version: 1.0.0

# System Topology Map

- topology_id: `dominium.audit.topology_map`
- repository_hash: `HEAD:c982fd0b40bc5e4208aee687644f8eed2cbe993a`
- generated_tick: `0`
- deterministic_fingerprint: `9d8e9469043a7becb09f2050dea3db77f886e0b4d4113a055a7c12755a49ad58`

## Counts
- node_count: 4921
- edge_count: 10244

## Node Kinds
- contract_set: 147
- module: 98
- policy_set: 308
- process_family: 393
- registry: 371
- schema: 1309
- tool: 2295

## Edge Kinds
- consumes: 4759
- depends_on: 2765
- enforces: 955
- produces: 1
- validates: 1764

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
- `module:src/appshell`
- `module:src/chem`
- `module:src/client`
- `module:src/compat`
- `module:src/control`
- `module:src/control/control_plane_engine.py`
- `module:src/control/effects/effect_engine.py`
- `module:src/control/fidelity/fidelity_engine.py`
- `module:src/control/ir/control_ir_compiler.py`
- `module:src/control/negotiation/negotiation_kernel.py`
- `module:src/control/view/view_engine.py`
- `module:src/core`
- `module:src/diag`
- `module:src/diegetics`
- `module:src/electric`
- `module:src/embodiment`
- `module:src/epistemics`
- `module:src/field`
- `module:src/fields`

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
