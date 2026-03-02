Status: DERIVED
Version: 1.0.0

# System Topology Map

- topology_id: `dominium.audit.topology_map`
- repository_hash: `HEAD:f3977546774343fe489268444635502b8082fca4`
- generated_tick: `0`
- deterministic_fingerprint: `120fc8744c62c24c24b20d0da267dbe823a1a2c1fc73fd501bf76f9d1d859420`

## Counts
- node_count: 2318
- edge_count: 97713

## Node Kinds
- contract_set: 4
- module: 72
- policy_set: 117
- process_family: 153
- registry: 167
- schema: 804
- tool: 1001

## Edge Kinds
- consumes: 2345
- depends_on: 1105
- enforces: 22748
- produces: 1
- validates: 71514

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
- `module:src/fields`
- `module:src/infrastructure`
- `module:src/inspection`
- `module:src/interaction`
- `module:src/interior`
- `module:src/logistics`
- `module:src/machines`
- `module:src/materials`

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
